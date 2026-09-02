# ui/server.py: buillt by AI
import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import html

# Add the parent directory to Python path so we can import core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.indexer import Indexer
from core.searcher import Searcher


class SearchHandler(BaseHTTPRequestHandler):
    """HTTP handler for the search engine web interface."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == "/" or path == "/index.html":
            self.serve_html_page()
        elif path == "/search":
            self.handle_search(parsed_url)
        elif path == "/style.css":
            self.serve_css()
        else:
            self.send_error(404, "Page not found")
    
    def serve_html_page(self):
        """Serve the main HTML page."""
        try:
            with open("ui/templates/index.html", 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "index.html not found")
    
    def serve_css(self):
        """Serve CSS file."""
        try:
            with open("ui/templates/style.css", 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(css_content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "style.css not found")
    
    def handle_search(self, parsed_url):
        """Handle search requests."""
        # Parse query parameters
        query_params = parse_qs(parsed_url.query)
        query = query_params.get('q', [''])[0].strip()
        k = int(query_params.get('k', ['10'])[0])
        
        if not query:
            self.send_json_response({"error": "No query provided"}, 400)
            return
        
        try:
            # Load index (auto-loads from disk)
            indexer = Indexer()
            
            # Create searcher
            searcher = Searcher(indexer)
            
            # Execute search
            results = searcher.search(query, k)
            
            # Return JSON response
            self.send_json_response({
                "query": query,
                "count": len(results),
                "results": results
            })
            
        except FileNotFoundError:
            self.send_json_response({"error": "Index not found. Run 'python main.py build' first."}, 500)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def send_json_response(self, data, status_code=200):
        """Send a JSON response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to reduce console spam."""
        print(f"[{self.address_string()}] {format % args}")


def run_server(port: int = 8000):
    """Run the HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SearchHandler)
    print(f"🚀 Search engine server running at http://localhost:{port}")
    print(f"🔍 Visit http://localhost:{port} to search")
    print("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()