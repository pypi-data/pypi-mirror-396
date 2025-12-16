# Django API Gate 🏦

Monetize your Django API in minutes.
django-api-gate is a drop-in middleware that turns your API into a metered, paid service.
It connects to the API Gate Hub protocol to handle API keys, credit balances, and billing automatically.

# 🚀 Features

Instant Paywall: Protects your API routes with one line of code.

Metered Billing: Deducts credits per request automatically.

Zero-Config Banking: No need to set up Stripe or Ledger logic yourself—API Gate Hub handles the backend.

High Performance: Uses persistent connection pooling for minimal latency impact (~20ms).

# 📦 Installation

pip install django-api-gate

# ⚙️ Configuration

1. Add into your settings.py:

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    # ...

    'django_api_gate.middleware.ApiGateMiddleware', # <--- Add this

    # ...

]


2. Go to API Gate Hub and create an account.

3. Copy your API Key from the dashboard.

4. Add your API Key to settings.py:

API_GATE_API_KEY = "your-merchant-uuid-here"

OPTIONAL VARIABLES:

Change which URLS are protected (Default: '/api/'):

API_GATE_URL_PREFIX = "/v1/"

Change the cost per request (Default: 1 credit):

API_GATE_PRICE = 5


# 🛠️ Usage

Once installed, any request to your protected URL prefix (e.g., /api/data) will require an API Gate Key in the header:

curl -H "X-Api-Key: 'customer-uuid-here'" [https://yoursite.com/api/data](https://yoursite.com/api/data)

If a user runs out of credits, they receive a standard 402 Payment Required response:

{
    "error": "Insufficient Credits",
    "balance": 0,
    "top_up_url": "[https://https://api-gate-hub.onrender.com/](https://https://api-gate-hub.onrender.com/)"
}

If a user is missing a key, they receive a standard 401 Unauthorized response:

{
    "error": "Unauthorized",
    "message": "Access requires a prepaid API Key in header 'X-Api-Key'.",
    "portal_url": "[https://https://api-gate-hub.onrender.com/](https://https://api-gate-hub.onrender.com/)"
}

# 🏗️ Architecture

This library operates as a Spoke in a Hub-and-Spoke financial model.

The Hub: The API Gate Hub (Ledger, Stripe Processing, User Accounts).

The Spoke: Your Django App (Product, Logic, Value).

When a request comes in, this middleware pings the Hub to verify funds and transfer credits from the Consumer to the Merchant.