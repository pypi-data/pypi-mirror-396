from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json

class FormData:
    """Access form fields as attributes: form.username, form.password"""
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value[0])  # take first value if list
    def __getitem__(self, key):
        return getattr(self, key, None)

class Handler(BaseHTTPRequestHandler):
    routes = {}

    def _handle_request(self, func, post_data=None):
        if post_data:
            form = FormData(post_data)
        else:
            form = None
        response = func(form)
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(response.encode())

    def do_POST(self):
        if self.path in self.routes:
            length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(length)
            post_data = urllib.parse.parse_qs(post_data.decode())
            self._handle_request(self.routes[self.path], post_data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_GET(self):
        if self.path in self.routes:
            self._handle_request(self.routes[self.path])
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

class AayushLogin:
    """Super simple local server library for HTML login forms"""
    def __init__(self):
        self.routes = {}
        Handler.routes = self.routes

    def route(self, path, methods=['POST']):
        """Register route with decorator"""
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator

    def save(self, filename, data):
        """Append string data to a file"""
        with open(filename, "a") as f:
            f.write(data + "\n")

    def run(self, host='127.0.0.1', port=5000):
        print(f"AayushLogin server running at http://{host}:{port}")
        server = HTTPServer((host, port), Handler)
        server.serve_forever()
