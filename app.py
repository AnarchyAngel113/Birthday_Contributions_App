"""
Birthday Contributions App

A Flask web application for collecting birthday contributions from colleagues.
Features contribution tracking and display.

Author: AI Assistant
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from dotenv import load_dotenv
from datetime import datetime
import google.generativeai as genai
import requests
import json

# Load environment variables from .env file
load_dotenv()

# Configure Google AI
genai.configure(api_key=os.environ.get('GOOGLE_AI_API_KEY'))

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# In-memory storage for contributions (in production, use a database)
# TODO: Replace with persistent database storage (e.g., SQLite, PostgreSQL)
contributions = []

@app.route('/')
def index():
    """Render the main contribution form page"""
    return render_template('index.html')

@app.route('/contribute', methods=['POST'])
def contribute():
    """Handle contribution form submission and redirect to payment page"""
    amount = int(request.form['amount'])  # Amount in dollars
    name = request.form['name']

    # Store temporarily in session-like behavior (for demo - in production use session)
    # For now, we'll pass via query params to payment page
    return redirect(url_for('payment', amount=amount, name=name))

@app.route('/process_payment', methods=['POST'])
def process_payment():
    """Process mock payment and store contribution"""
    # For demo purposes, we'll add contribution when payment is "successful"
    amount = int(request.form.get('amount', 0))
    name = request.form.get('name', 'Anonymous')

    # Store the contribution
    contribution = {
        'name': name,
        'amount': amount,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    contributions.append(contribution)

    # Store amount and name in session for gift suggestions
    session['last_amount'] = amount
    session['last_name'] = name

    return redirect(url_for('success'))

@app.route('/payment')
def payment():
    """Display the payment page with debit card and cash options"""
    amount = request.args.get('amount', 0)
    name = request.args.get('name', 'Anonymous')
    return render_template('payment.html', amount=int(amount), name=name)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/contributions')
def view_contributions():
    """Route to display all contributions and total amount"""
    total = sum(c['amount'] for c in contributions)
    return render_template('contributions.html', contributions=contributions, total=total)

def get_gift_suggestions(keyword, budget):
    """Get gift suggestions using Google AI"""
    try:
        # Try different model names as the API might have changed
        models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        model = None

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                break
            except Exception:
                continue

        if not model:
            raise Exception("No suitable model found")

        prompt = f"""
        Suggest 5 birthday gift ideas for someone who likes {keyword}.
        Budget range: ${budget - 10} to ${budget + 10}
        Each suggestion should include:
        - Name of the gift
        - Brief description (2-3 sentences)
        - Estimated price

        Format as JSON array with objects containing 'name', 'description', and 'price' fields.
        """

        response = model.generate_content(prompt)
        suggestions_text = response.text.strip()

        # Try to extract JSON from response
        if suggestions_text.startswith('```json'):
            suggestions_text = suggestions_text[7:-3].strip()
        elif suggestions_text.startswith('```'):
            suggestions_text = suggestions_text[3:-3].strip()

        suggestions = json.loads(suggestions_text)

        # Ensure all suggestions have required fields
        for suggestion in suggestions:
            if 'price' in suggestion and isinstance(suggestion['price'], str):
                # Remove $ and convert to float
                suggestion['price'] = float(suggestion['price'].replace('$', '').replace(',', ''))

        return suggestions

    except Exception as e:
        print(f"Error getting gift suggestions: {e}")
        # Enhanced fallback suggestions based on keyword
        fallback_suggestions = {
            'practical': [
                {'name': 'Multi-tool Kit', 'description': 'A compact multi-tool with various functions for everyday use.', 'price': budget},
                {'name': 'Insulated Water Bottle', 'description': 'Stainless steel water bottle that keeps drinks cold for 24 hours.', 'price': budget},
                {'name': 'Portable Charger', 'description': 'Compact power bank for charging devices on the go.', 'price': budget}
            ],
            'fun': [
                {'name': 'Board Game', 'description': 'Engaging board game perfect for family game nights.', 'price': budget},
                {'name': 'Wireless Headphones', 'description': 'High-quality wireless headphones for music and calls.', 'price': budget},
                {'name': 'Puzzle Set', 'description': 'Challenging puzzle set for hours of entertainment.', 'price': budget}
            ],
            'luxury': [
                {'name': 'Designer Wallet', 'description': 'Premium leather wallet with multiple card slots.', 'price': budget},
                {'name': 'Scented Candle Set', 'description': 'Luxury scented candles with elegant fragrances.', 'price': budget},
                {'name': 'Silk Scarf', 'description': 'Beautiful silk scarf in trendy patterns.', 'price': budget}
            ],
            'premium': [
                {'name': 'Smart Watch', 'description': 'Advanced smartwatch with health tracking features.', 'price': budget},
                {'name': 'Wireless Earbuds', 'description': 'Premium wireless earbuds with noise cancellation.', 'price': budget},
                {'name': 'Leather Briefcase', 'description': 'High-quality leather briefcase for professionals.', 'price': budget}
            ],
            'books': [
                {'name': 'Bestseller Book', 'description': 'Popular fiction or non-fiction book.', 'price': budget},
                {'name': 'Book Light', 'description': 'LED book light for reading in low light.', 'price': budget}
            ],
            'gadgets': [
                {'name': 'Smart Home Device', 'description': 'Voice-controlled smart home assistant.', 'price': budget},
                {'name': 'Bluetooth Speaker', 'description': 'Portable Bluetooth speaker with great sound.', 'price': budget}
            ]
        }

        return fallback_suggestions.get(keyword.lower(), [
            {
                'name': f'{keyword.title()} Gift',
                'description': f'A thoughtful gift related to {keyword} interests.',
                'price': budget
            },
            {
                'name': f'Custom {keyword.title()} Item',
                'description': f'Personalized item based on {keyword} preferences.',
                'price': budget - 5 if budget > 5 else budget
            }
        ])

@app.route('/gift_keyword')
def gift_keyword():
    """Display gift keyword selection page"""
    # Use total contributions instead of last individual amount
    total = sum(c['amount'] for c in contributions)
    return render_template('gift_keyword.html', amount=total)

@app.route('/gift_suggestions', methods=['GET', 'POST'])
def gift_suggestions():
    """Display gift suggestions page"""
    # Use total contributions instead of last individual amount
    amount = sum(c['amount'] for c in contributions)
    name = session.get('last_name', 'Friend')

    if request.method == 'POST':
        keyword = request.form.get('keyword')
        if keyword == 'custom':
            keyword = request.form.get('custom_keyword', 'general')
    else:
        # For GET requests, use amount-based default
        if amount <= 15:
            keyword = "practical"
        elif amount <= 25:
            keyword = "fun"
        elif amount <= 35:
            keyword = "luxury"
        else:
            keyword = "premium"

    try:
        suggestions = get_gift_suggestions(keyword, amount)
    except Exception as e:
        suggestions = []
        error = f"Unable to generate suggestions: {str(e)}"
        return render_template('gift_suggestions.html', keyword=keyword, amount=amount, suggestions=suggestions, error=error)

    return render_template('gift_suggestions.html', keyword=keyword, amount=amount, suggestions=suggestions)

if __name__ == '__main__':
    app.run(debug=True)