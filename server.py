from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class SimpleHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Preflight response for CORS
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)

        print("Received:", data)

        response = {
            "message": f"You said: {data.get('text', '')}"
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  # ✅ CORS!
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))

httpd = HTTPServer(("localhost", 5000), SimpleHandler)
print("Server running at http://localhost:5000")
httpd.serve_forever()
