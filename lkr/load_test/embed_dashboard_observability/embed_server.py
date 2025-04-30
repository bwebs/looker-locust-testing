import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import structlog

logger = structlog.get_logger()

class EmbedHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Override to disable default server logging
        pass

    def do_GET(self):
        path, *rest = self.path.split('?')
        if path =='/':
        # Serve the HTML file
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_path = Path(__file__).parent / 'embed_container.html'
            with open(html_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(204)
            self.end_headers()


    def do_POST(self):
        path, *rest = self.path.split('?')
        if path == '/log_event':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            event_data = json.loads(post_data)
            
            # Log the event using structlog
            logger.info(
                event_data['event_type'],
                timestamp=event_data['timestamp'],
                duration_ms=event_data['duration_ms'],
                dashboard_id=event_data['dashboard_id'],
                user_id=event_data['user_id'],
                **event_data['event_data'],
            )
            
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=3000, log_event_prefix="looker_embed_observability"):
    class EmbedHandlerWithPrefix(EmbedHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.log_event_prefix = log_event_prefix

    server_address = ('', port)
    httpd = HTTPServer(server_address, EmbedHandlerWithPrefix)
    logger.info(f"{log_event_prefix}:embed_server_started", port=port, embed_domain=f"http://localhost:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server(3000, log_event_prefix="looker_embed_observability") 