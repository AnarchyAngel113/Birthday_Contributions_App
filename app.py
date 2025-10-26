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

def get_gift_images(keyword, count=5):
    """Get gift images from Unsplash API"""
    access_key = os.environ.get('UNSPLASH_ACCESS_KEY')
    if not access_key:
        return []

    try:
        url = f"https://api.unsplash.com/search/photos?query={keyword}+gift&per_page={count}&orientation=landscape"
        headers = {"Authorization": f"Client-ID {access_key}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        return [photo['urls']['regular'] for photo in data.get('results', [])]

    except Exception as e:
        print(f"Error getting gift images: {e}")
        return []

def get_gift_suggestions(keyword, budget):
    """Get gift suggestions using Google AI Gemini 1.5"""
    try:
        # Use Gemini 1.5 Pro for text generation
        model = genai.GenerativeModel('gemini-1.5-pro')

        prompt = f"""
        Suggest 5 unique birthday gift ideas for someone who likes {keyword}.
        Budget range: ${max(10, budget - 10)} to ${budget + 10}
        Each suggestion should include:
        - Creative and specific name of the gift
        - Detailed description (3-4 sentences explaining why it's great)
        - Estimated price within budget range
        - Why this gift matches the {keyword} interest

        Format as JSON array with objects containing 'name', 'description', 'price', and 'reason' fields.
        Make suggestions creative and personalized.
        """

        response = model.generate_content(prompt)
        suggestions_text = response.text.strip()

        # Try to extract JSON from response
        if suggestions_text.startswith('```json'):
            suggestions_text = suggestions_text[7:-3].strip()
        elif suggestions_text.startswith('```'):
            suggestions_text = suggestions_text[3:-3].strip()

        suggestions = json.loads(suggestions_text)

        # Ensure all suggestions have required fields and get images
        images = get_gift_images(keyword, len(suggestions))

        for i, suggestion in enumerate(suggestions):
            if 'price' in suggestion and isinstance(suggestion['price'], str):
                # Remove $ and convert to float
                suggestion['price'] = float(suggestion['price'].replace('$', '').replace(',', ''))

            # Add image URL if available
            suggestion['image_url'] = images[i] if i < len(images) else None

        return suggestions

    except Exception as e:
        print(f"Error getting gift suggestions: {e}")
        # Enhanced fallback suggestions with images
        images = get_gift_images(keyword, 5)
        fallback_suggestions = {
            'practical': [
                {'name': 'Multi-tool Kit', 'description': 'A compact multi-tool with various functions for everyday use. Perfect for someone who appreciates functional and reliable tools.', 'price': budget, 'reason': 'Combines practicality with versatility for daily tasks.', 'image_url': images[0] if images else None},
                {'name': 'Insulated Water Bottle', 'description': 'Stainless steel water bottle that keeps drinks cold for 24 hours or hot for 12 hours. Eco-friendly and durable.', 'price': budget, 'reason': 'Essential for staying hydrated on the go.', 'image_url': images[1] if len(images) > 1 else None},
                {'name': 'Portable Charger', 'description': 'Compact power bank for charging devices on the go. Fast charging technology with multiple USB ports.', 'price': budget, 'reason': 'Never run out of battery when you need it most.', 'image_url': images[2] if len(images) > 2 else None}
            ],
            'fun': [
                {'name': 'Strategy Board Game', 'description': 'Engaging board game perfect for family game nights. Hours of entertainment with challenging gameplay.', 'price': budget, 'reason': 'Creates memorable moments with friends and family.', 'image_url': images[0] if images else None},
                {'name': 'Wireless Gaming Headphones', 'description': 'High-quality wireless headphones with surround sound for immersive gaming experience.', 'price': budget, 'reason': 'Enhances gaming sessions with superior audio quality.', 'image_url': images[1] if len(images) > 1 else None},
                {'name': '3D Puzzle Set', 'description': 'Challenging 3D puzzle set for hours of creative entertainment. Develops problem-solving skills.', 'price': budget, 'reason': 'Provides intellectual stimulation and satisfaction of completion.', 'image_url': images[2] if len(images) > 2 else None}
            ],
            'luxury': [
                {'name': 'Designer Leather Wallet', 'description': 'Premium leather wallet with multiple card slots and RFID protection. Handcrafted with attention to detail.', 'price': budget, 'reason': 'Elevates everyday carry with sophistication and quality.', 'image_url': images[0] if images else None},
                {'name': 'Artisan Scented Candle Collection', 'description': 'Luxury scented candles with elegant fragrances. Hand-poured with natural soy wax and essential oils.', 'price': budget, 'reason': 'Creates a relaxing ambiance and aromatic experience.', 'image_url': images[1] if len(images) > 1 else None},
                {'name': 'Silk Sleep Mask', 'description': 'Beautiful silk sleep mask with adjustable strap. Ultra-soft and comfortable for better sleep.', 'price': budget, 'reason': 'Promotes restful sleep with luxurious comfort.', 'image_url': images[2] if len(images) > 2 else None}
            ],
            'premium': [
                {'name': 'Smart Fitness Watch', 'description': 'Advanced smartwatch with health tracking, GPS, and heart rate monitoring. Premium build quality.', 'price': budget, 'reason': 'Combines technology with health and fitness tracking.', 'image_url': images[0] if images else None},
                {'name': 'Wireless Noise-Cancelling Earbuds', 'description': 'Premium wireless earbuds with active noise cancellation and superior sound quality.', 'price': budget, 'reason': 'Delivers exceptional audio experience in any environment.', 'image_url': images[1] if len(images) > 1 else None},
                {'name': 'Executive Leather Briefcase', 'description': 'High-quality leather briefcase with organized compartments and professional design.', 'price': budget, 'reason': 'Perfect for the modern professional who values quality and style.', 'image_url': images[2] if len(images) > 2 else None}
            ]
        }

        suggestions = fallback_suggestions.get(keyword.lower(), [
            {
                'name': f'Premium {keyword.title()} Gift',
                'description': f'A thoughtful and high-quality gift related to {keyword} interests. Carefully selected for its excellence and appeal.',
                'price': budget,
                'reason': f'Matches {keyword} interests with premium quality and attention to detail.',
                'image_url': images[0] if images else None
            },
            {
                'name': f'Custom {keyword.title()} Experience',
                'description': f'Personalized experience based on {keyword} preferences. Unique and memorable way to celebrate.',
                'price': budget - 5 if budget > 5 else budget,
                'reason': f'Creates lasting memories centered around {keyword} passion.',
                'image_url': images[1] if len(images) > 1 else None
            }
        ])

        # Add images to suggestions if available
        for i, suggestion in enumerate(suggestions):
            if 'image_url' not in suggestion and i < len(images):
                suggestion['image_url'] = images[i]

        return suggestions

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