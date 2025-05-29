import json
import re
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import structlog

from lkr.load_test.embed_dashboard_observability.events import EventLogger

logger = structlog.get_logger("looker-embed-observability")


class EmbedHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override to disable default server logging
        pass

    def do_GET(self):
        path, *rest = self.path.split("?")
        if path == "/":
            # Serve the HTML file
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html_path = Path(__file__).parent / "embed_container.html"
            with open(html_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(204)
            self.end_headers()

    def do_POST(self):
        path, *rest = self.path.split("?")
        if path == "/log_event":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            event_data = json.loads(post_data)
            # Extract the ISO datetime at the start of the string
            iso_str_full = event_data["task_start_time"]
            match = re.match(r"([0-9T:\.\-\+:]+)", iso_str_full)
            if match:
                iso_str = match.group(1)
                parsed_task_start_time = datetime.fromisoformat(iso_str)
                if parsed_task_start_time.tzinfo is None:
                    parsed_task_start_time = parsed_task_start_time.replace(
                        tzinfo=timezone.utc
                    )
            else:
                raise ValueError(f"Could not extract ISO datetime from: {iso_str_full}")
            event_logger = EventLogger.initialize(
                log_event_prefix=getattr(
                    self, "log_event_prefix", "looker_embed_observability"
                ),
                user_id=event_data["user_id"],
                dashboard=event_data["dashboard_id"],
                task_id=event_data["task_id"],
                task_start_time=parsed_task_start_time,
            )
            event_logger.log_event(event_data["event_type"], **event_data["event_data"])

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

    server_address = ("", port)
    httpd = HTTPServer(server_address, EmbedHandlerWithPrefix)
    logger.info(
        f"{log_event_prefix}:embed_server_started",
        port=port,
        embed_domain=f"http://localhost:{port}",
    )
    httpd.serve_forever()


if __name__ == "__main__":
    run_server(4000, log_event_prefix="looker_embed_observability")
