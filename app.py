"""
Birthday Contributions App

A Flask web application for collecting birthday contributions from colleagues
using Stripe payment processing. Features contribution tracking and display.

Author: AI Assistant
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
import stripe
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configure Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

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
    """Process successful payment and store contribution"""
    # In a real app, you'd verify the payment with Stripe webhook
    # For demo purposes, we'll add contribution when payment is "successful"
    amount = int(request.form.get('amount', 0)) / 100  # Convert back to dollars
    name = request.form.get('name', 'Anonymous')

    # Store the contribution
    contribution = {
        'name': name,
        'amount': amount,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    contributions.append(contribution)

    return redirect(url_for('view_contributions'))

@app.route('/payment')
def payment():
    """Display the payment page with debit card and cash options"""
    amount = request.args.get('amount', 0)
    name = request.args.get('name', 'Anonymous')
    return render_template('payment.html', amount=int(amount) * 100, name=name)  # Multiply by 100 for cents

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/contributions')
def view_contributions():
    """Route to display all contributions and total amount"""
    total = sum(c['amount'] for c in contributions)
    return render_template('contributions.html', contributions=contributions, total=total)

if __name__ == '__main__':
    app.run(debug=True)