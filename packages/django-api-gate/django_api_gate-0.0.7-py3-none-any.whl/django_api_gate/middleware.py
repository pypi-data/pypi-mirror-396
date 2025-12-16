import requests
from django.http import JsonResponse
from django.conf import settings

class ApiGateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # CONFIGURATION
        self.bank_url = getattr(settings, 'API_GATE_BANK_URL', 'https://api-gate-hub.onrender.com')
        self.price = getattr(settings, 'API_GATE_PRICE', 1) 
        self.api_key = getattr(settings, 'API_GATE_API_KEY', None)
        self.protected_prefix = getattr(settings, 'API_GATE_URL_PREFIX', '/api/')

        # PERFORMANCE: Create a persistent session
        # This reuses the TCP connection, skipping the SSL handshake on every request.
        self.session = requests.Session()
        
        # Pre-set headers that don't change
        if self.api_key:
            self.session.headers.update({'X-Merchant-Key': self.api_key})

        if not self.api_key:
            print("WARNING: API Gate is missing API_GATE_API_KEY. You won't get paid!")

    def __call__(self, request):
        # 1. CHECK PATH (Fastest check first)
        if not request.path.startswith(self.protected_prefix):
             return self.get_response(request)

        # 2. CHECK FOR VISITOR KEY
        visitor_key = request.headers.get("X-Api-Key")
        
        if not visitor_key:
            return JsonResponse({
                "error": "Unauthorized",
                "message": f"Access requires a prepaid API Key in header 'X-Api-Key'.",
                "portal_url": f"{self.bank_url}"
            }, status=401)

        # 3. EXECUTE PAYMENT (Using Persistent Session)
        try:
            # We use self.session.post instead of requests.post
            response = self.session.post(
                f"{self.bank_url}/api/spend/",
                json={'amount': self.price},
                headers={'X-Customer-Key': visitor_key}, # Merchant Key is already in session
                timeout=2.0 # Strict timeout: If Bank is slow, fail fast.
            )
            
            if response.status_code == 200:
                return self.get_response(request)
            
            elif response.status_code == 402:
                data = response.json()
                return JsonResponse({
                    "error": "Insufficient Credits",
                    "balance": data.get('balance'),
                    "top_up_url": data.get('portal_url')
                }, status=402)
            
            else:
                # Bank Error (500, 404, etc)
                return JsonResponse({"error": "Payment Bank Error"}, status=502)

        except requests.exceptions.RequestException:
             # If the Bank is down, we have a choice:
             # A. Fail Closed (Safe for you): Return 503
             # B. Fail Open (Nice for users): Let them in for free this time
             
             # Currently configured to Fail Closed:
             return JsonResponse({"error": "Payment System Unavailable"}, status=503)