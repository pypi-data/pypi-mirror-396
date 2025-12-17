import http.server
import socketserver
import json
import logging
from .bridge import text_to_tensor
from .core.api import tensor7

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CMFO - %(levelname)s - %(message)s'
)

PORT = 8000


class CMFORESTHandler(http.server.BaseHTTPRequestHandler):
    """
    Production-grade Request Handler for CMFO API.
    Returns JSON. Handles Errors. Stateless.
    """

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # CORS
        self.end_headers()

    def do_GET(self):
        """Health check endpoint."""
        if self.path == "/health" or self.path == "/":
            self._set_headers()
            response = {
                "status": "active",
                "system": "CMFO v1.0.0",
                "mode": "fractal"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())

    def do_POST(self):
        """
        Handle compute requests.
        Endpoints:
        - /tensor7: Scalar op
        - /encode: Text to Vector
        """
        if self.path == "/tensor7":
            self._handle_tensor7()
        elif self.path == "/encode":
            self._handle_encode()
        else:
            self._set_headers(404)
            response = {"error": "Endpoint not found"}
            self.wfile.write(json.dumps(response).encode())

    def _handle_tensor7(self):
        try:
            data = self._read_json()
            # Validation
            if 'a' not in data or 'b' not in data:
                self._send_error(400, "Missing parameters 'a' or 'b'")
                return

            res = tensor7(float(data['a']), float(data['b']))

            self._set_headers()
            response = {"operation": "tensor7", "result": float(res)}
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            logging.error(f"Error in /tensor7: {e}")
            self._send_error(500, str(e))

    def _handle_encode(self):
        try:
            data = self._read_json()
            if 'text' not in data:
                self._send_error(400, "Missing parameter 'text'")
                return

            vec = text_to_tensor(data['text'])

            self._set_headers()
            # Convert numpy array to list for JSON serialization
            response = {
                "text": data['text'],
                "vector": vec.tolist(),
                "dim": 7
            }
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            logging.error(f"Error in /encode: {e}")
            self._send_error(500, str(e))

    def _read_json(self):
        length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(length)
        return json.loads(post_data.decode('utf-8'))

    def _send_error(self, code, message):
        self._set_headers(code)
        self.wfile.write(json.dumps({"error": message}).encode())


def run(port=PORT):
    server = socketserver.TCPServer(("", port), CMFORESTHandler)
    logging.info(f"Serving CMFO API at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        logging.info("Server stopped.")


if __name__ == "__main__":
    run()
