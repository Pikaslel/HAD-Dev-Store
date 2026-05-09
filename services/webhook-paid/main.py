import hmac
import hashlib
import base64
import json
import urllib.request
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

# --- CONFIGURACIÓN DESDE VARIABLES DE ENTORNO ---
SHOPIFY_WEBHOOK_SECRET = os.getenv('SHOPIFY_WEBHOOK_SECRET')
MOCK_ENDPOINT = os.getenv('MOCK_ENDPOINT')

class WebhookHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        # Silenciar logs automáticos de la consola
        return

    def do_POST(self):
        print(f"\n[LOG][{time.strftime('%H:%M:%S')}] Webhook recibido desde Shopify...")
        
        content_length = int(self.headers.get('Content-Length', 0))
        hmac_header = self.headers.get('X-Shopify-Hmac-Sha256')
        raw_body = self.rfile.read(content_length)

        # 1. Validación HMAC (Seguridad)
        if not self.verify_hmac(raw_body, hmac_header):
            print("[ERROR] Firma HMAC inválida. Petición rechazada.")
            self.send_response(401)
            self.end_headers()
            return

        print("[OK] Firma HMAC verificada.")

        # 2. Transformación del Payload
        try:
            order = json.loads(raw_body)
            transformed_payload = {
                "customer_name": f"{order.get('customer', {}).get('first_name', '')} {order.get('customer', {}).get('last_name', '')}",
                "email": order.get('email'),
                "city": order.get('shipping_address', {}).get('city', 'N/A'),
                "total_value": order.get('total_price'),
                "items": [
                    {
                        "product": item.get('title'),
                        "qty": item.get('quantity'),
                        "sku": item.get('sku')
                    } for item in order.get('line_items', [])
                ]
            }
            print(f"[INFO] Payload transformado para orden: {order.get('order_number')}")
        except Exception as e:
            print(f"[ERROR] Falló la transformación: {e}")
            self.send_response(400)
            self.end_headers()
            return

        # 3. Envío al endpoint externo con Reintentos
        if self.send_with_retry(transformed_payload):
            self.send_response(200)
            print("[SUCCESS] Webhook procesado y enviado con éxito.")
        else:
            self.send_response(500)
            print("[CRITICAL] Fallo tras múltiples reintentos.")
            
        self.end_headers()

    def verify_hmac(self, data, hmac_header):
        if not hmac_header or not SHOPIFY_WEBHOOK_SECRET: return False
        digest = hmac.new(SHOPIFY_WEBHOOK_SECRET.encode('utf-8'), data, hashlib.sha256).digest()
        computed = base64.b64encode(digest).decode('utf-8')
        return hmac.compare_digest(computed, hmac_header)

    def send_with_retry(self, payload, max_retries=3):
        data = json.dumps(payload).encode('utf-8')
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(
                    MOCK_ENDPOINT, 
                    data=data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=5) as res:
                    if res.status in [200, 201]:
                        return True
            except Exception as e:
                print(f"[RETRY {attempt + 1}/{max_retries}] Error enviando a mock: {e}")
                time.sleep(2)
        return False

if __name__ == '__main__':
    if not SHOPIFY_WEBHOOK_SECRET or not MOCK_ENDPOINT:
        print("ERROR: Verifique que las variables de entorno estén configuradas.")
    else:
        server = HTTPServer(('', 3000), WebhookHandler)
        print(f"--- SERVICIO DE WEBHOOKS INICIADO ---")
        print(f"Escuchando en: server NGrok o localhost:3000")
        print(f"Destino final: {MOCK_ENDPOINT}")
        server.serve_forever()