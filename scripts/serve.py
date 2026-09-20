"""Local static preview, including the fictional interactive demo. No AWS credentials needed."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1] / 'backend' / 'static'

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path == '/config':
            data = json.dumps({'region': 'us-east-1', 'clientId': '', 'poolId': ''}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(data)
            return
        path = self.path.split('?')[0]
        if path in ('/', '/privacy', '/app', '/integrations', '/pricing', '/docs'):
            self.path = '/support.html'
        elif path == '/email-preview':
            self.path = '/email-preview.html'
        elif path == '/widget-demo':
            self.path = '/widget.html'
        elif path == '/integration-demo':
            self.path = '/integration-demo.html'
        elif path == '/orders' or path.startswith('/confirm/'):
            self.path = '/index.html'
        super().do_GET()

if __name__ == '__main__':
    print('OrderProof preview: http://127.0.0.1:8080', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8080), Handler).serve_forever()
