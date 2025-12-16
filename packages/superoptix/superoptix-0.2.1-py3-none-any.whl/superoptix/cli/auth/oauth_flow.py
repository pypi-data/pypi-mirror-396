"""Browser-based OAuth flow for CLI authentication."""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional
import time


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from browser."""

    auth_code = None
    auth_error = None

    def do_GET(self):
        """Handle GET request with OAuth callback."""
        # Ignore favicon and other browser requests
        if self.path == "/favicon.ico" or not self.path.startswith("/callback"):
            self.send_response(404)
            self.end_headers()
            return

        query = urlparse(self.path).query
        params = parse_qs(query)

        if "code" in params:
            OAuthCallbackHandler.auth_code = params["code"][0]

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html = """
            <html>
            <head>
                <title>SuperOptiX Authentication</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        text-align: center;
                        padding: 50px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    .container {
                        background: white;
                        color: #333;
                        padding: 40px;
                        border-radius: 12px;
                        max-width: 500px;
                        margin: 0 auto;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    }
                    h1 { color: #10b981; margin: 0 0 20px 0; }
                    p { font-size: 16px; line-height: 1.6; }
                    .icon { font-size: 60px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">✅</div>
                    <h1>Authentication Successful!</h1>
                    <p>You can close this window and return to the CLI.</p>
                    <p style="color: #666; font-size: 14px; margin-top: 20px;">
                        This window will close automatically in 3 seconds...
                    </p>
                </div>
                <script>setTimeout(function(){ window.close(); }, 3000);</script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())

        elif "error" in params:
            OAuthCallbackHandler.auth_error = params["error"][0]

            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html = """
            <html>
            <head>
                <title>SuperOptiX Authentication</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        text-align: center;
                        padding: 50px;
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        color: white;
                    }
                    .container {
                        background: white;
                        color: #333;
                        padding: 40px;
                        border-radius: 12px;
                        max-width: 500px;
                        margin: 0 auto;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    }
                    h1 { color: #ef4444; margin: 0 0 20px 0; }
                    p { font-size: 16px; line-height: 1.6; }
                    .icon { font-size: 60px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">❌</div>
                    <h1>Authentication Failed</h1>
                    <p>Please try again in the CLI.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())

    def log_message(self, format, *args):
        """Suppress server logs."""
        pass


class BrowserOAuthFlow:
    """Browser-based OAuth flow for CLI using Supabase client."""

    def __init__(self, supabase_client, callback_port: int = 54321):
        """Initialize OAuth flow.

        Args:
            supabase_client: Initialized Supabase client instance
            callback_port: Port for local callback server
        """
        self.supabase = supabase_client
        self.callback_port = callback_port
        self.server = None

    def get_oauth_url(self) -> str:
        """Get OAuth URL using Supabase client (handles PKCE correctly).

        Returns:
            OAuth URL string
        """
        # Use Supabase client's built-in method (handles PKCE automatically)
        redirect_uri = f"http://localhost:{self.callback_port}/callback"

        response = self.supabase.auth.sign_in_with_oauth(
            {"provider": "github", "options": {"redirect_to": redirect_uri}}
        )

        # This URL includes proper PKCE parameters and state token
        return response.url

    def start_server(self):
        """Start the callback server so it's ready to receive requests.

        Call this BEFORE displaying the URL to the user.
        """
        # Reset class variables
        OAuthCallbackHandler.auth_code = None
        OAuthCallbackHandler.auth_error = None

        try:
            # Start local callback server
            self.server = HTTPServer(
                ("localhost", self.callback_port), OAuthCallbackHandler
            )
            return True
        except OSError:
            # Port already in use or other error
            return False

    def wait_for_callback(self, timeout: int = 300) -> Optional[str]:
        """Wait for OAuth callback after server is started.

        Args:
            timeout: Timeout in seconds (default 5 minutes)

        Returns:
            Authorization code or None if failed/timeout
        """
        try:
            # Wait for callback with timeout
            start_time = time.time()

            while (
                OAuthCallbackHandler.auth_code is None
                and OAuthCallbackHandler.auth_error is None
            ):
                # Handle one request at a time
                self.server.handle_request()

                # Check timeout
                if time.time() - start_time > timeout:
                    return None

            # Return auth code if successful
            if OAuthCallbackHandler.auth_code:
                return OAuthCallbackHandler.auth_code

            return None

        except Exception:
            return None

        finally:
            if self.server:
                self.server.server_close()

    def start(
        self, timeout: int = 300, auto_open_browser: bool = True
    ) -> Optional[str]:
        """Start OAuth flow and wait for callback (legacy method).

        Args:
            timeout: Timeout in seconds (default 5 minutes)
            auto_open_browser: Whether to automatically open browser (default True)

        Returns:
            Authorization code or None if failed/timeout
        """
        if not self.start_server():
            return None
        return self.wait_for_callback(timeout, auto_open_browser)
