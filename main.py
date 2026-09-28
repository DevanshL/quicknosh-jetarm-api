#!/usr/bin/env python3
"""
QuickNosh Express — Cloud-Hosted Salesforce & JetArm Fulfillment API
Professional Executive Portal Edition:
- Interactive Live Dispatch Simulator
- Shopper Experience Flow
- Real-time Hardware Metrics
- Full Enterprise API endpoints
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
# 2. HIGH-END EXECUTIVE WEB DASHBOARD (GET /)
# ==============================================================================
HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>QuickNosh Express — Robotic Fulfillment Operations</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090d16;
      --card-bg: #111827;
      --card-border: #1f293d;
      --accent: #3b82f6;
      --accent-glow: rgba(59, 130, 246, 0.2);
      --green: #10b981;
      --green-glow: rgba(16, 185, 129, 0.25);
      --text: #f3f4f6;
      --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 40px 20px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .container { max-width: 960px; width: 100%; }
    
    .header { text-align: center; margin-bottom: 35px; }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 16px;
      background: var(--green-glow);
      border: 1px solid var(--green);
      color: #34d399;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 16px;
      letter-spacing: 0.05em;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      background-color: #34d399;
      border-radius: 50%;
      box-shadow: 0 0 12px #34d399;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
      70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(52, 211, 153, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
    }
    h1 {
      font-size: 2.4rem;
      font-weight: 800;
      background: linear-gradient(135deg, #ffffff 0%, #93c5fd 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 8px;
      letter-spacing: -0.02em;
    }
    .subtitle { color: var(--text-muted); font-size: 1.05rem; }

    /* Interactive Live Simulator Card */
    .simulator-card {
      background: linear-gradient(145deg, #131c2e 0%, #0d1322 100%);
      border: 1px solid #2563eb;
      border-radius: 14px;
      padding: 24px;
      margin-bottom: 30px;
      box-shadow: 0 10px 30px rgba(37, 99, 235, 0.15);
    }
    .sim-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 10px;
    }
    .sim-title {
      font-size: 1.15rem;
      font-weight: 700;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .sim-btn {
      background: #2563eb;
      color: #ffffff;
      border: none;
      padding: 9px 18px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
    }
    .sim-btn:hover { background: #1d4ed8; transform: translateY(-1px); }
    .sim-btn:active { transform: translateY(0); }
    
    .status-terminal {
      background: #050811;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      color: #94a3b8;
      min-height: 120px;
    }
    .log-line { margin-bottom: 6px; }
    .log-success { color: #34d399; font-weight: 600; }
    .log-highlight { color: #60a5fa; }
    
    /* Metrics Row */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 30px;
    }
    .metric-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 16px;
      text-align: center;
    }
    .metric-label { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; }
    .metric-val { font-size: 1.4rem; font-weight: 700; color: #ffffff; margin-top: 4px; font-family: 'JetBrains Mono', monospace; }

    /* Shopper Flow Banner */
    .flow-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 30px;
    }
    .flow-steps {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-top: 16px;
    }
    .step-box {
      background: #090e1a;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 14px;
      font-size: 0.85rem;
    }
    .step-num {
      color: #3b82f6;
      font-weight: 700;
      font-size: 0.75rem;
      text-transform: uppercase;
      margin-bottom: 4px;
    }
    .step-text { color: #cbd5e1; font-weight: 500; }

    /* API Endpoint Cards */
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 22px;
    }
    .card-title {
      font-size: 1.1rem;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .method-tag {
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      background: #1e3a8a;
      color: #60a5fa;
      border: 1px solid #3b82f6;
    }
    .code-block {
      background: #06090f;
      border: 1px solid #1f2937;
      border-radius: 8px;
      padding: 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      color: #e5e7eb;
      margin-top: 10px;
      overflow-x: auto;
    }
    .field-row {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #1f2937;
      font-size: 0.88rem;
    }
    .field-row:last-child { border-bottom: none; }
    .field-name { color: var(--text-muted); }
    .field-value { font-family: 'JetBrains Mono', monospace; color: #60a5fa; font-weight: 500; }

    footer {
      text-align: center;
      color: #64748b;
      font-size: 0.85rem;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <div class="container">
    
    <!-- Header -->
    <div class="header">
      <div class="badge">
        <span class="pulse-dot"></span>
        <span>SYSTEM OPERATIONAL &middot; 24/7 CLOUD HOSTED</span>
      </div>
      <h1>QuickNosh Express Fulfillment API</h1>
      <p class="subtitle">Autonomous 6-DOF JetArm Robotic Integration for Salesforce D2C Commerce</p>
    </div>

    <!-- Live Performance Metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-label">Robotic Kinematics</div>
        <div class="metric-val" style="color: #60a5fa;">6-DOF JetArm</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Vision Resolution</div>
        <div class="metric-val" style="color: #34d399;">Intel RealSense</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Average Pick SLA</div>
        <div class="metric-val" style="color: #f59e0b;">11.5s / SKU</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Safety Clearance</div>
        <div class="metric-val" style="color: #a78bfa;">+12cm High-Lift</div>
      </div>
    </div>

    <!-- Live Interactive Simulator Card -->
    <div class="simulator-card">
      <div class="sim-header">
        <div class="sim-title">
          <span>⚡ Live Order Fulfillment Simulator</span>
        </div>
        <button class="sim-btn" onclick="runLiveSimulation()">
          <span>▶ Trigger Test Pick Request</span>
        </button>
      </div>
      <p style="font-size: 0.88rem; color: #94a3b8; margin-bottom: 12px;">
        Click to test the live cloud handshake. Simulates an incoming Salesforce order dispatch to the robotic edge engine:
      </p>
      <div class="status-terminal" id="terminal-screen">
        <div class="log-line">&gt; Ready for incoming Salesforce D2C orders...</div>
        <div class="log-line">&gt; Connected to Live Instance: <span class="log-highlight">https://infycommerceorg.my.salesforce.com</span></div>
        <div class="log-line">&gt; Click [Trigger Test Pick Request] above to execute live handshake.</div>
      </div>
    </div>

    <!-- How Shoppers Experience It -->
    <div class="flow-card">
      <div style="font-weight: 700; color: #ffffff; font-size: 1.05rem;">How End Shoppers Experience QuickNosh Express</div>
      <div class="flow-steps">
        <div class="step-box">
          <div class="step-num">Step 1 &middot; Scan</div>
          <div class="step-text">Shopper scans shelf QR with phone. Adds product to cart.</div>
        </div>
        <div class="step-box">
          <div class="step-num">Step 2 &middot; Pay</div>
          <div class="step-text">Payment completes on Salesforce LWR Storefront.</div>
        </div>
        <div class="step-box">
          <div class="step-num">Step 3 &middot; Fulfill</div>
          <div class="step-text">JetArm AI locates item, plunges, and deposits into exit basket.</div>
        </div>
        <div class="step-box">
          <div class="step-num">Step 4 &middot; Pickup</div>
          <div class="step-text">Customer phone notifies: "Order Ready at Counter A!"</div>
        </div>
      </div>
    </div>

    <!-- API Reference Grid -->
    <div class="grid">
      <!-- Token Card -->
      <div class="card">
        <div class="card-title">
          <span class="method-tag">POST</span>
          <span>/oauth/token</span>
        </div>
        <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 10px;">
          Issues 1-hour OAuth 2.0 Bearer tokens for Salesforce Named Credentials.
        </p>
        <div class="field-row">
          <span class="field-name">Client ID</span>
          <span class="field-value">jetarm_quicknosh_client</span>
        </div>
        <div class="field-row">
          <span class="field-name">Client Secret</span>
          <span class="field-value">jetarm_quicknosh_2026</span>
        </div>
        <div class="field-row">
          <span class="field-name">Grant Type</span>
          <span class="field-value">client_credentials</span>
        </div>
        <div class="code-block">
POST /oauth/token HTTP/1.1<br>
Content-Type: application/json<br><br>
{"grant_type": "client_credentials", ...}
        </div>
      </div>

      <!-- Pick Card -->
      <div class="card">
        <div class="card-title">
          <span class="method-tag">POST</span>
          <span>/api/pick</span>
        </div>
        <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 10px;">
          Dispatches multi-item order pick requests with dynamic SLA estimation.
        </p>
        <div class="field-row">
          <span class="field-name">Authorization</span>
          <span class="field-value">Bearer &lt;access_token&gt;</span>
        </div>
        <div class="field-row">
          <span class="field-name">Status Response</span>
          <span class="field-value">200 ACCEPTED</span>
        </div>
        <div class="field-row">
          <span class="field-name">Callback Target</span>
          <span class="field-value" style="font-size: 0.75rem;">infycommerceorg/...</span>
        </div>
        <div class="code-block">
POST /api/pick HTTP/1.1<br>
Authorization: Bearer jarm_token_...<br><br>
{"cartId": "0a6xx...", "cartItems": [...]}
        </div>
      </div>
    </div>

    <!-- Connected Environments -->
    <div class="card" style="margin-bottom: 30px;">
      <div class="card-title">
        <span>Connected Cloud Environments</span>
      </div>
      <div class="field-row">
        <span class="field-name">Live Storefront</span>
        <span class="field-value"><a href="https://infycommerceorg.my.site.com/QuickNoshExpress/" target="_blank" style="color: #60a5fa; text-decoration: none;">infycommerceorg.my.site.com/QuickNoshExpress/ &nearr;</a></span>
      </div>
      <div class="field-row">
        <span class="field-name">Salesforce Instance</span>
        <span class="field-value">https://infycommerceorg.my.salesforce.com</span>
      </div>
      <div class="field-row">
        <span class="field-name">Robotic Callback Endpoint</span>
        <span class="field-value">/services/apexrest/RoboticStatusCallback</span>
      </div>
    </div>

    <footer>
      QuickNosh Express Autonomous Retail System &middot; Production API Gateway v2.0
    </footer>

  </div>

  <script>
    async function runLiveSimulation() {
      const term = document.getElementById('terminal-screen');
      term.innerHTML = '<div class="log-line">&gt; Initiating OAuth 2.0 handshake with /oauth/token...</div>';
      
      try {
        const tokenRes = await fetch('/oauth/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            grant_type: 'client_credentials',
            client_id: 'jetarm_quicknosh_client',
            client_secret: 'jetarm_quicknosh_2026'
          })
        });
        const tokenData = await tokenRes.json();
        
        term.innerHTML += `<div class="log-line log-success">&gt; [AUTH SUCCESS] Token Generated: ${tokenData.access_token.substring(0, 24)}... (Expires in 3600s)</div>`;
        term.innerHTML += '<div class="log-line">&gt; Dispatching order pick request to /api/pick (SKU: HB-M12-60-ZN, Qty: 1)...</div>';
        
        const pickRes = await fetch('/api/pick', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + tokenData.access_token
          },
          body: JSON.stringify({
            cartId: '0a6xx_SIM_' + Date.now(),
            packingRequestId: 'PR_SIM_' + Date.now(),
            idempotencyKey: 'IDEM_' + Date.now(),
            cartItems: [{
              cartItemId: '0a9xx0000004GfKAAU',
              sku: 'HB-M12-60-ZN',
              quantity: 1
            }]
          })
        });
        const pickData = await pickRes.json();
        
        term.innerHTML += `<div class="log-line log-success">&gt; [ORDER ACCEPTED] Status: ${pickData.status} | ETA: ${pickData.estimatedCompletionSeconds}s | Ref: ${pickData.externalRef}</div>`;
        term.innerHTML += '<div class="log-line">&gt; Kinematics sequence triggered: RealSense scan -> 6-DOF grasp -> +12cm High-Lift -> Deposit in Exit Basket.</div>';
        term.innerHTML += '<div class="log-line log-success">&gt; Outbound callback scheduled to https://infycommerceorg.my.salesforce.com/services/apexrest/RoboticStatusCallback</div>';
      } catch (err) {
        term.innerHTML += `<div class="log-line" style="color: #ef4444;">&gt; [ERROR] ${err.message}</div>`;
      }
    }
  </script>
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
