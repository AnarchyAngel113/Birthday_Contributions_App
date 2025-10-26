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
        model = genai.GenerativeModel('gemini-pro')

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
        # Fallback suggestions
        return [
            {
                'name': f'{keyword.title()} Related Gift',
                'description': f'A thoughtful gift related to {keyword} interests.',
                'price': budget
            }
        ]

@app.route('/gift_suggestions')
def gift_suggestions():
    """Display gift suggestions page"""
    amount = session.get('last_amount', 20)
    name = session.get('last_name', 'Friend')

    # Determine keyword based on amount (this is a simple mapping, could be more sophisticated)
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