"""
Authentication utilities for CLI - integrates with API auth system
"""

import os
import json
import jwt
import webbrowser
import time
import requests
import socket
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


class CLIAuthManager:
    """Manager for CLI authentication token storage and validation"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".sentient"
        self.token_file = self.config_dir / "auth.json"
        self.config_dir.mkdir(exist_ok=True)
        

        self.api_base_url = os.getenv("SENTIENT_API_URL", "https://api.sentient-space.com")
        self.clerk_frontend_api = os.getenv("CLERK_FRONTEND_API", "")
    
    def store_token(self, access_token: str, refresh_token: str, user_info: Dict[str, Any], expires_at: int) -> None:
        """
        Store authentication tokens and user info locally
        
        Args:
            access_token: platform-issued access token (JWT)
            refresh_token: platform-issued refresh token (JWT)
            user_info: User information
            expires_at: Unix timestamp when access token expires
        """
        auth_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "user_info": user_info,
            "stored_at": datetime.utcnow().isoformat()
        }
        
        try:
            with open(self.token_file, 'w') as f:
                json.dump(auth_data, f, indent=2)
            
            # Set restrictive permissions (owner read/write only)
            os.chmod(self.token_file, 0o600)
            
        except Exception as e:
            raise RuntimeError(f"Failed to store authentication token: {str(e)}")
    
    def get_stored_token(self) -> Optional[Dict[str, Any]]:
        """
        Get stored authentication token and user info
        
        Returns:
            Dict containing token and user info, or None if not found
        """
        if not self.token_file.exists():
            return None
        
        try:
            with open(self.token_file, 'r') as f:
                auth_data = json.load(f)
            
            return auth_data
            
        except Exception:
            # If we can't read the token file, treat as not authenticated
            return None
    
    def clear_token(self) -> None:
        """Clear stored authentication token"""
        if self.token_file.exists():
            try:
                self.token_file.unlink()
            except Exception:
                pass  # Ignore errors when clearing
    
    def is_token_valid(self, token: str) -> bool:
        """
        Check if a token is still valid (not expired)
        
        Args:
            token: JWT token to validate
            
        Returns:
            True if token is valid and not expired
        """
        try:
            # Decode without verification to check expiration
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Check if token has expiration
            exp = payload.get("exp")
            if not exp:
                return False
            
            # Check if token is expired
            exp_datetime = datetime.utcfromtimestamp(exp)
            return exp_datetime > datetime.utcnow()
            
        except Exception:
            return False
    
    def _exchange_clerk_token(self, clerk_token: str) -> Dict[str, Any]:
        """
        Exchange Clerk token for platform-issued tokens.
        """
        url = f"{self.api_base_url}/api/auth/cli-exchange"
        r = requests.post(url, json={"token": clerk_token}, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"Token exchange failed: {r.status_code} {r.text}")
        return r.json()
    
    def _refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh platform access token using refresh token.
        """
        url = f"{self.api_base_url}/api/auth/cli-refresh"
        r = requests.post(url, json={"refresh_token": refresh_token}, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"Token refresh failed: {r.status_code} {r.text}")
        return r.json()
    
    def get_valid_token(self) -> Optional[str]:
        """
        Get a valid authentication token if available
        
        Returns:
            Valid JWT token or None if not available/expired
        """
        auth_data = self.get_stored_token()
        if not auth_data:
            return None
        
        access_token = auth_data.get("access_token")
        refresh_token = auth_data.get("refresh_token")
        expires_at = auth_data.get("expires_at")
        if not access_token or not expires_at:
            return None
        
        # Refresh if expiring within 120 seconds
        now_ts = int(time.time())
        if now_ts >= int(expires_at) - 120:
            if not refresh_token:
                self.clear_token()
                return None
            try:
                refreshed = self._refresh_tokens(refresh_token)
                self.store_token(
                    refreshed["access_token"],
                    refreshed["refresh_token"],
                    refreshed.get("user") or auth_data.get("user_info") or {},
                    refreshed["expires_at"],
                )
                access_token = refreshed["access_token"]
            except Exception:
                self.clear_token()
                return None
        
        return access_token
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Get stored user information
        
        Returns:
            User information dict or None if not available
        """
        auth_data = self.get_stored_token()
        if not auth_data:
            return None
        
        access_token = auth_data.get("access_token")
        refresh_token = auth_data.get("refresh_token")
        expires_at = auth_data.get("expires_at")
        user_info = auth_data.get("user_info")
        if not access_token or not expires_at:
            return None
        # Attempt refresh if expired to keep status accurate
        now_ts = int(time.time())
        if now_ts >= int(expires_at):
            if not refresh_token:
                return None
            try:
                refreshed = self._refresh_tokens(refresh_token)
                self.store_token(
                    refreshed["access_token"],
                    refreshed["refresh_token"],
                    refreshed.get("user") or user_info or {},
                    refreshed["expires_at"],
                )
                return refreshed.get("user") or user_info
            except Exception:
                return None
        return user_info
    
    def extract_user_from_token(self, token: str) -> Dict[str, Any]:
        """
        Extract user information from JWT token without verification
        
        Args:
            token: JWT token
            
        Returns:
            User information from token
        """
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            
            return {
                "clerk_id": payload.get("sub"),
                "email": payload.get("email"),
                "name": payload.get("name", payload.get("given_name", "")),
                "exp": payload.get("exp")
            }
            
        except Exception as e:
            raise ValueError(f"Failed to extract user from token: {str(e)}")
    
    def create_auth_header(self, token: str) -> Dict[str, str]:
        """
        Create authorization header for API requests
        
        Args:
            token: JWT token
            
        Returns:
            Dict containing authorization header
        """
        return {"Authorization": f"Bearer {token}"}
    
    def initiate_browser_login(self, force_login: bool = False) -> str:
        """
        Browser-based OAuth login flow
        
        Returns:
            Authentication token
        """
        console.print(Panel.fit(
            "[bold blue]Sentient Web Platform Authentication[/bold blue]\n\n"
            "We'll open your browser to authenticate with Clerk.\n"
            "After authentication, the browser will redirect back to complete the process.",
            title="🔐 Authentication"
        ))
        
        # Find available port for callback server
        callback_port = self._find_available_port()
        callback_url = f"http://localhost:{callback_port}/callback"
        
        # Store the received token
        received_token = {"token": None, "error": None}
        
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path.startswith('/callback'):
                    # Parse query parameters
                    parsed_url = urllib.parse.urlparse(self.path)
                    params = urllib.parse.parse_qs(parsed_url.query)
                    
                    if 'token' in params:
                        received_token["token"] = params['token'][0]
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        success_html = """
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Authentication Successful</title>
                            <meta charset="utf-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1">
                            <style>
                                :root {
                                    color-scheme: dark;
                                }
                                * {
                                    box-sizing: border-box;
                                }
                                body {
                                    margin: 0;
                                    min-height: 100vh;
                                    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                                    background: #000;
                                    color: #e5e7eb;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                }
                                .shell {
                                    width: 100%;
                                    max-width: 420px;
                                    padding: 1.75rem;
                                    border-radius: 0.75rem;
                                    border: 1px solid rgba(55,65,81,0.95);
                                    background: radial-gradient(circle at top, rgba(34,197,94,0.18), transparent 55%), #020617;
                                    box-shadow:
                                        0 0 0 1px rgba(15,23,42,0.7),
                                        0 22px 70px rgba(0,0,0,0.85);
                                    text-align: center;
                                }
                                .success-icon {
                                    font-size: 2.4rem;
                                    color: #22c55e;
                                    margin-bottom: 0.75rem;
                                    text-shadow: 0 0 18px rgba(34,197,94,0.7);
                                }
                                h1 {
                                    margin: 0 0 0.5rem 0;
                                    font-size: 1.4rem;
                                    font-weight: 600;
                                    color: #f9fafb;
                                }
                                p {
                                    margin: 0;
                                    font-size: 0.95rem;
                                    color: #9ca3af;
                                }
                                .secondary {
                                    margin-top: 0.5rem;
                                    font-size: 0.8rem;
                                    color: #6b7280;
                                }
                            </style>
                        </head>
                        <body>
                            <main class="shell" aria-label="Sentient CLI authentication success">
                                <div class="success-icon">✓</div>
                                <h1>Authentication successful</h1>
                                <p>You can now close this window and return to your terminal.</p>
                                <p class="secondary">This tab will close automatically in a few seconds.</p>
                            </main>
                            <script>setTimeout(() => window.close(), 2800);</script>
                        </body>
                        </html>
                        """
                        self.wfile.write(success_html.encode())
                    elif 'error' in params:
                        received_token["error"] = params['error'][0]
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        error_html = """
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Authentication Failed</title>
                            <meta charset="utf-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1">
                            <style>
                                :root {
                                    color-scheme: dark;
                                }
                                * {
                                    box-sizing: border-box;
                                }
                                body {
                                    margin: 0;
                                    min-height: 100vh;
                                    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                                    background: #000;
                                    color: #e5e7eb;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                }
                                .shell {
                                    width: 100%;
                                    max-width: 420px;
                                    padding: 1.75rem;
                                    border-radius: 0.75rem;
                                    border: 1px solid rgba(127,29,29,0.9);
                                    background: radial-gradient(circle at top, rgba(248,113,113,0.22), transparent 55%), #111827;
                                    box-shadow:
                                        0 0 0 1px rgba(15,23,42,0.8),
                                        0 22px 70px rgba(0,0,0,0.9);
                                    text-align: center;
                                }
                                .error-icon {
                                    font-size: 2.4rem;
                                    color: #f97373;
                                    margin-bottom: 0.75rem;
                                }
                                h1 {
                                    margin: 0 0 0.5rem 0;
                                    font-size: 1.4rem;
                                    font-weight: 600;
                                    color: #fee2e2;
                                }
                                p {
                                    margin: 0;
                                    font-size: 0.95rem;
                                    color: #fecaca;
                                }
                                .secondary {
                                    margin-top: 0.5rem;
                                    font-size: 0.8rem;
                                    color: #fca5a5;
                                }
                            </style>
                        </head>
                        <body>
                            <main class="shell" aria-label="Sentient CLI authentication error">
                                <div class="error-icon">✕</div>
                                <h1>Authentication failed</h1>
                                <p>Please return to your terminal and run the login again.</p>
                                <p class="secondary">This tab will close automatically in a few seconds.</p>
                            </main>
                            <script>setTimeout(() => window.close(), 2800);</script>
                        </body>
                        </html>
                        """
                        self.wfile.write(error_html.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                # Suppress server logs
                pass
        
        # Start callback server
        server = HTTPServer(('localhost', callback_port), CallbackHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        try:
            # Build auth URL with callback
            auth_url = f"{self.api_base_url}/api/auth/cli-login?callback_url={urllib.parse.quote(callback_url)}"
            if force_login:
                auth_url += "&force_login=true"
            
            console.print(f"\n[yellow]Opening browser to authenticate...[/yellow]")
            console.print(f"[dim]If browser doesn't open automatically, visit: {auth_url}[/dim]")
            
            try:
                # Force open in new tab to avoid reusing existing localhost tabs
                webbrowser.open_new_tab(auth_url)
            except Exception:
                console.print("[yellow]Could not open browser automatically.[/yellow]")
                console.print(f"[cyan]Please visit: {auth_url}[/cyan]")
            
            # Wait for callback with timeout
            console.print("\n[cyan]Waiting for authentication...[/cyan]")
            
            timeout = 300  # 5 minutes
            start_time = time.time()
            
            while received_token["token"] is None and received_token["error"] is None:
                if time.time() - start_time > timeout:
                    raise TimeoutError("Authentication timed out after 5 minutes")
                time.sleep(0.5)
            
            if received_token["error"]:
                raise ValueError(f"Authentication failed: {received_token['error']}")
            
            clerk_token = received_token["token"]
            
            # Validate token format (Clerk)
            if not self._validate_token_format(clerk_token):
                raise ValueError("Invalid token format received")
            
            # Exchange for platform tokens
            exchanged = self._exchange_clerk_token(clerk_token)
            access_token = exchanged["access_token"]
            refresh_token = exchanged["refresh_token"]
            expires_at = exchanged["expires_at"]
            user_info = exchanged.get("user") or self.extract_user_from_token(clerk_token)
            # Normalize user display for messaging and storage
            display_user = (
                (user_info or {}).get("email")
                or (user_info or {}).get("name")
                or (user_info or {}).get("clerk_id")
                or "Unknown"
            )
            
            # Store platform tokens and user info
            self.store_token(access_token, refresh_token, user_info, expires_at)
            
            console.print(Panel.fit(
                f"[green]✅ Successfully authenticated as {display_user}[/green]",
                title="Success"
            ))
            
            return access_token
            
        finally:
            server.shutdown()
            server.server_close()
    
    def _find_available_port(self) -> int:
        """Find an available port for the callback server"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    

    
    def logout(self) -> None:
        """Logout and clear stored authentication"""
        self.clear_token()
    
    def get_auth_status(self) -> Dict[str, Any]:
        """
        Get current authentication status
        
        Returns:
            Dict with authentication status information
        """
        token = self.get_valid_token()
        user_info = self.get_user_info()
        
        if token and user_info:
            # Normalize user_info fields for downstream display/use
            user_info = {
                "email": user_info.get("email") or user_info.get("name") or user_info.get("clerk_id"),
                "name": user_info.get("name") or user_info.get("email") or user_info.get("clerk_id"),
                "clerk_id": user_info.get("clerk_id"),
            }
            return {
                "authenticated": True,
                "user": user_info,
                "token_valid": True
            }
        else:
            return {
                "authenticated": False,
                "user": None,
                "token_valid": False
            }
    
    def _validate_token_format(self, token: str) -> bool:
        """
        Validate that token has correct JWT format
        
        Args:
            token: Token to validate
            
        Returns:
            True if token has valid JWT format
        """
        if not token:
            return False
        
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        # Each part should be base64 encoded
        try:
            for part in parts:
                # Add padding if needed
                padded = part + '=' * (4 - len(part) % 4)
                import base64
                base64.urlsafe_b64decode(padded)
            return True
        except Exception:
            return False


# Global CLI auth manager instance
cli_auth_manager = CLIAuthManager()


def get_cli_auth_token() -> Optional[str]:
    """
    Convenience function to get CLI authentication token
    
    Returns:
        Valid JWT token or None
    """
    return cli_auth_manager.get_valid_token()


def get_cli_user_info() -> Optional[Dict[str, Any]]:
    """
    Convenience function to get CLI user information
    
    Returns:
        User information dict or None
    """
    return cli_auth_manager.get_user_info()


def is_cli_authenticated() -> bool:
    """
    Check if CLI is currently authenticated
    
    Returns:
        True if authenticated with valid token
    """
    return get_cli_auth_token() is not None


def require_authentication() -> str:
    """
    Decorator/function to require authentication
    
    Returns:
        Valid authentication token
        
    Raises:
        click.ClickException: If not authenticated
    """
    import click
    
    token = get_cli_auth_token()
    if not token:
        console.print("[red]❌ Not authenticated. Please run 'sen auth login' first.[/red]")
        raise click.ClickException("Authentication required")
    
    return token


def get_authenticated_session() -> requests.Session:
    """
    Get a requests session with authentication headers
    
    Returns:
        Configured requests session
    """
    token = require_authentication()
    
    session = requests.Session()
    session.headers.update(cli_auth_manager.create_auth_header(token))
    
    return session