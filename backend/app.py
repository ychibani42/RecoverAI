from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            return

        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))


def run(host: str = "127.0.0.1", port: int = 8000):
    server = HTTPServer((host, port), HealthHandler)
    print(f"Python backend running on http://{host}:{port}")
    print("Health check: GET /health")
    server.serve_forever()


if __name__ == "__main__":
    run()
