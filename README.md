# Birthday Contributions App

A Flask web application for collecting birthday contributions from colleagues using Stripe payment processing.

## Features

- 🎉 Beautiful, animated UI with fade-in effects and hover animations
- 💳 Secure payment processing with Stripe
- 🔐 Environment variable configuration for API keys
- 📱 Responsive design
- 📊 Real-time contribution tracking and display
- 💰 Total contributions summary
- 👥 Individual contribution history with timestamps

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/anarchyangel113/birthday-contributions-app.git
   cd birthday-contributions-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env` file and fill in your keys:
     ```
     SECRET_KEY=your-secret-key-here
     STRIPE_SECRET_KEY=sk_test_...
     ```
   - In `payment.html`, replace `pk_test_...` with your Stripe publishable key.

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser to `http://127.0.0.1:5000/`

## Usage

1. Enter your name and contribution amount
2. Click "Contribute" to proceed to payment
3. Complete the test payment (demo mode)
4. View all contributions and total amount collected
5. Receive confirmation of successful contribution

### Viewing Contributions

- After making a contribution, you'll be redirected to the contributions page
- This page shows the total amount collected from all contributors
- Individual contributions are listed with names, amounts, and timestamps
- Navigate back to make additional contributions as needed

## Configuration

- **SECRET_KEY**: Flask application secret key
- **STRIPE_SECRET_KEY**: Your Stripe secret key (test or live)
- **Stripe Publishable Key**: Update in `templates/payment.html`

## Development Notes

- Current implementation uses in-memory storage for contributions
- In production, replace with persistent database storage
- Contributions are stored as list of dictionaries with name, amount, and timestamp
- Test payment mode allows UI testing without real Stripe transactions

## Technologies Used

- Flask (Python web framework)
- Stripe (Payment processing)
- HTML/CSS/JavaScript (Frontend)
- Jinja2 (Templating)

## License

This project is open source and available under the [MIT License](LICENSE).