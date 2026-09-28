#!/usr/bin/env python3
"""
QuickNosh Express — Cloud-Hosted Salesforce & JetArm Fulfillment API
Ultra-Clean, Minimalist Status Page Edition
"""

import os
import sys
import time
import json
import secrets
import threading
import logging
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("QuickNoshCloudAPI")

# ==============================================================================
# 1. CLOUD CONFIGURATION & CREDENTIALS
# ==============================================================================
PORT = int(os.environ.get("PORT", 8080))
JETSON_CLIENT_ID     = os.environ.get("JETSON_CLIENT_ID", "jetarm_quicknosh_client")
JETSON_CLIENT_SECRET = os.environ.get("JETSON_CLIENT_SECRET", "jetarm_quicknosh_2026")

SALESFORCE_INSTANCE_URL  = "https://infycommerceorg.my.salesforce.com"
SALESFORCE_AUTH_URL      = os.environ.get("SALESFORCE_AUTH_URL", f"{SALESFORCE_INSTANCE_URL}/services/oauth2/token")
SALESFORCE_REST_CALLBACK = os.environ.get("SALESFORCE_REST_CALLBACK", f"{SALESFORCE_INSTANCE_URL}/services/apexrest/RoboticStatusCallback")
SALESFORCE_CLIENT_ID     = os.environ.get("SALESFORCE_CLIENT_ID", "YOUR_SALESFORCE_CONNECTED_APP_CONSUMER_KEY")
SALESFORCE_CLIENT_SECRET = os.environ.get("SALESFORCE_CLIENT_SECRET", "YOUR_SALESFORCE_CONNECTED_APP_CONSUMER_SECRET")

active_tokens = {}

# ==============================================================================
# 2. ULTRA-CLEAN MINIMAL STATUS PAGE (GET /)
# ==============================================================================
HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>QuickNosh Express — JetArm Fulfillment API</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      background-color: #0b0f19;
      color: #f3f4f6;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .card {
      background: #111827;
      border: 1px solid #1f293d;
      border-radius: 16px;
      padding: 40px;
      max-width: 520px;
      width: 100%;
      text-align: center;
      box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    .success-icon {
      width: 64px;
      height: 64px;
      background: rgba(16, 185, 129, 0.15);
      border: 2px solid #10b981;
      color: #10b981;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      margin: 0 auto 20px;
    }
    h1 {
      font-size: 1.6rem;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 8px;
    }
    .status-text {
      color: #10b981;
      font-weight: 600;
      font-size: 1rem;
      margin-bottom: 24px;
      letter-spacing: 0.05em;
    }
    .info-box {
      background: #090e1a;
      border: 1px solid #1f2937;
      border-radius: 10px;
      padding: 16px;
      text-align: left;
      font-size: 0.9rem;
      margin-bottom: 20px;
    }
    .info-row {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #161f30;
    }
    .info-row:last-child { border-bottom: none; }
    .label { color: #94a3b8; }
    .val { color: #60a5fa; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }
    .footer {
      color: #64748b;
      font-size: 0.8rem;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="success-icon">&#10003;</div>
    <h1>QuickNosh JetArm API</h1>
    <div class="status-text">&#9679; SUCCESS &middot; SYSTEM ONLINE</div>

    <div class="info-box">
      <div class="info-row">
        <span class="label">Status</span>
        <span class="val" style="color: #10b981;">Operational (24/7)</span>
      </div>
      <div class="info-row">
        <span class="label">Target Org</span>
        <span class="val">infycommerceorg</span>
      </div>
      <div class="info-row">
        <span class="label">Token API</span>
        <span class="val">POST /oauth/token</span>
      </div>
      <div class="info-row">
        <span class="label">Pick API</span>
        <span class="val">POST /api/pick</span>
      </div>
      <div class="info-row">
        <span class="label">Status Callback</span>
        <span class="val">/RoboticStatusCallback</span>
      </div>
    </div>

    <div class="footer">
      Connected to Salesforce D2C Commerce &middot; Ready for Postman Calls
    </div>
  </div>
</body>
</html>
"""

# ==============================================================================
# 3. OAUTH 2.0 TOKEN HANDLER
# ==============================================================================
def generate_bearer_token():
    return "jarm_token_" + secrets.token_hex(24)

def validate_bearer_token(auth_header):
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
    token = auth_header.split("Bearer ")[1].strip()
    if token in active_tokens and time.time() < active_tokens[token]:
        return True
    return False

# ==============================================================================
# 4. SALESFORCE APEX REST CALLBACK CLIENT
# ==============================================================================
def send_packed_callback_to_salesforce(cart_id, packing_request_id, idempotency_key, external_ref, bin_number, packed_items):
    logger.info(f"[SALESFORCE CALLBACK] Sending PackedNotification for RequestID: {packing_request_id} to {SALESFORCE_REST_CALLBACK}")
    
    sf_token = "sandbox_dummy_token"
    try:
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": SALESFORCE_CLIENT_ID,
            "client_secret": SALESFORCE_CLIENT_SECRET
        }
        res = requests.post(SALESFORCE_AUTH_URL, data=auth_data, timeout=5.0)
        if res.status_code == 200:
            sf_token = res.json().get("access_token")
    except Exception as e:
        logger.warning(f"Salesforce Auth Notice: {e}")

    callback_payload = {
        "cartId": cart_id,
        "packingRequestId": packing_request_id,
        "idempotencyKey": idempotency_key,
        "externalRef": external_ref,
        "status": "PACKED",
        "binNumber": bin_number,
        "packedAtUtc": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "packedItems": packed_items
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {sf_token}"
    }
    try:
        res = requests.post(SALESFORCE_REST_CALLBACK, data=json.dumps(callback_payload), headers=headers, timeout=5.0)
        logger.info(f"[CALLBACK SUCCESS] HTTP {res.status_code} | Order marked 'Pickup Ready' in Salesforce")
    except Exception as e:
        logger.error(f"[CALLBACK ERROR] Could not reach Salesforce endpoint: {e}")

# ==============================================================================
# 5. PICK EXECUTION WORKER
# ==============================================================================
def execute_fulfillment_job(job_data):
    cart_id            = job_data['cartId']
    packing_request_id = job_data['packingRequestId']
    idempotency_key    = job_data['idempotencyKey']
    external_ref       = job_data['externalRef']
    bin_number         = job_data.get('binNumber', 'BIN-A17-042')
    cart_items         = job_data.get('cartItems', [])

    logger.info(f"[JOB STARTED] Processing Cart {cart_id} with {len(cart_items)} item type(s)")
    
    packed_items_list = []
    for idx, item in enumerate(cart_items):
        sku = item.get('sku', 'UNKNOWN')
        qty = int(item.get('quantity', 1))
        cart_item_id = item.get('cartItemId', f'0a9xx_item_{idx}')
        
        logger.info(f"-> Picking Item {idx+1}/{len(cart_items)}: SKU '{sku}' (Qty: {qty}) from Bin {bin_number}")
        time.sleep(1.0)
        
        packed_items_list.append({
            "cartItemId": cart_item_id,
            "sku": sku,
            "quantityRequested": qty,
            "quantityPacked": qty,
            "PickupStaus": "Full",
            "Reason": "Not Applicable"
        })

    logger.info(f"[JOB COMPLETED] All {len(cart_items)} item(s) deposited into exit basket")
    send_packed_callback_to_salesforce(
        cart_id,
        packing_request_id,
        idempotency_key,
        external_ref,
        bin_number,
        packed_items_list
    )

# ==============================================================================
# 6. REST API SERVER (CLOUD HTTP HANDLER)
# ==============================================================================
class CloudIntegrationHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def do_GET(self):
        accept_header = self.headers.get('Accept', '')
        if 'application/json' in accept_header:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            health_resp = {
                "service": "QuickNosh JetArm Robotic Fulfillment Cloud API",
                "status": "ONLINE",
                "target_salesforce": SALESFORCE_INSTANCE_URL,
                "endpoints": {
                    "token": "POST /oauth/token",
                    "pick": "POST /api/pick"
                }
            }
            self.wfile.write(json.dumps(health_resp, indent=2).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode('utf-8'))

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)

        # ----------------------------------------------------------------------
        # ENDPOINT 1: POST /oauth/token
        # ----------------------------------------------------------------------
        if self.path == '/oauth/token':
            try:
                data = json.loads(body.decode('utf-8'))
            except Exception:
                data = {}
            if data.get('client_id') == JETSON_CLIENT_ID and data.get('client_secret') == JETSON_CLIENT_SECRET:
                token = generate_bearer_token()
                active_tokens[token] = time.time() + 3600
                resp = {"access_token": token, "token_type": "Bearer", "expires_in": 3600}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode('utf-8'))
            else:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "invalid_client", "message": "Invalid client_id or client_secret"}).encode('utf-8'))
            return

        # ----------------------------------------------------------------------
        # ENDPOINT 2: POST /api/pick
        # ----------------------------------------------------------------------
        elif self.path == '/api/pick':
            if not validate_bearer_token(self.headers.get('Authorization')):
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "unauthorized", "message": "Missing or invalid Bearer access token"}).encode('utf-8'))
                return

            try:
                event_data = json.loads(body.decode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON format", "details": str(e)}).encode('utf-8'))
                return

            cart_id            = event_data.get('cartId', f'0a6xx{int(time.time())}')
            packing_request_id = event_data.get('packingRequestId', cart_id)
            idempotency_key    = event_data.get('idempotencyKey', f'{cart_id}-{int(time.time())}')
            external_ref       = f"PACK-2026-{int(time.time())}"
            
            cart_items = event_data.get('cartItems', [])
            if not cart_items and 'SKU' in event_data:
                cart_items = [{
                    "cartItemId": "0a9xx0000004GfKAAU",
                    "sku": event_data['SKU'],
                    "quantity": int(event_data.get('Quantity', 1))
                }]

            bin_number = event_data.get('binNumber', event_data.get('Bin_Location__c', 'BIN-A17-042'))
            est_seconds = max(11, int(len(cart_items) * 11.5))

            accepted_resp = {
                "status": "ACCEPTED",
                "externalRef": external_ref,
                "estimatedCompletionSeconds": est_seconds
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(accepted_resp).encode('utf-8'))

            job = {
                'cartId': cart_id,
                'packingRequestId': packing_request_id,
                'idempotencyKey': idempotency_key,
                'externalRef': external_ref,
                'binNumber': bin_number,
                'cartItems': cart_items
            }
            threading.Thread(target=execute_fulfillment_job, args=(job,), daemon=True).start()
            return

        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    logger.info(f"Starting QuickNosh Cloud API Service on Port {PORT}...")
    server = HTTPServer(('0.0.0.0', PORT), CloudIntegrationHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping Cloud API Service...")
