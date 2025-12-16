import argparse
import json
import os
import random
import socket
import string
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional, Tuple


DEFAULT_PLATFORM_URL = os.environ.get("HEAPTREE_PLATFORM_URL", "https://heaptree.com")
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".heaptree")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def _generate_state(length: int = 30) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class _CallbackState:
    def __init__(self, expected_state: str):
        self.expected_state = expected_state
        self.api_key: Optional[str] = None
        self.error: Optional[str] = None
        self._event = threading.Event()

    def set_result(self, api_key: Optional[str], error: Optional[str]):
        self.api_key = api_key
        self.error = error
        self._event.set()

    def wait(self, timeout: int) -> bool:
        return self._event.wait(timeout)


def _success_html() -> bytes:
    return """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Heaptree CLI Login</title>
    <style>
      body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', Arial, sans-serif; padding: 2rem; }
      .card { max-width: 560px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 12px; padding: 24px; }
      h1 { margin: 0 0 8px; font-size: 20px; }
      p { margin: 8px 0 0; color: #374151; }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>You're all set ✅</h1>
      <p>You can close this tab and return to your terminal.</p>
    </div>
  </body>
</html>
""".encode("utf-8")


def _error_html(message: str) -> bytes:
    escaped = message.replace("<", "&lt;").replace(">", "&gt;")
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Heaptree CLI Login - Error</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', Arial, sans-serif; padding: 2rem; }}
      .card {{ max-width: 560px; margin: 0 auto; border: 1px solid #fee2e2; background: #fef2f2; border-radius: 12px; padding: 24px; }}
      h1 {{ margin: 0 0 8px; font-size: 20px; color: #991b1b; }}
      p {{ margin: 8px 0 0; color: #7f1d1d; }}
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Login failed</h1>
      <p>{escaped}</p>
    </div>
  </body>
</html>
""".encode("utf-8")


def _make_handler(state: _CallbackState):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            try:
                parsed = urllib.parse.urlparse(self.path)
                if parsed.path != "/callback":
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Not found")
                    return

                qs = urllib.parse.parse_qs(parsed.query)
                got_state = (qs.get("state") or [""])[0]
                api_key = (qs.get("api_key") or [""])[0]
                error = (qs.get("error") or [""])[0]

                if not got_state or got_state != state.expected_state:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(_error_html("State mismatch. Please retry `heaptree login`."))
                    state.set_result(None, "state_mismatch")
                    return

                if error:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(_error_html(error))
                    state.set_result(None, error)
                    return

                if not api_key:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(_error_html("Missing API key."))
                    state.set_result(None, "missing_api_key")
                    return

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(_success_html())
                state.set_result(api_key, None)
            except Exception as e:
                try:
                    self.send_response(500)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(_error_html(f"Unexpected error: {e}"))
                finally:
                    state.set_result(None, str(e))

        def log_message(self, fmt, *args):  # silence default logging
            return

    return Handler


def _write_config(api_key: str) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = {
        "api_key": api_key,
        "created_at": int(time.time()),
        "source": "cli_login",
        "platform_url": DEFAULT_PLATFORM_URL,
    }
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def _update_shell_profile(api_key: str) -> Tuple[Optional[str], Optional[str]]:
    shell = os.environ.get("SHELL", "")
    # sensible defaults for mac (zsh) and bash; otherwise fall back to ~/.profile
    if shell.endswith("zsh"):
        profile = os.path.join(os.path.expanduser("~"), ".zshrc")
    elif shell.endswith("bash"):
        profile = os.path.join(os.path.expanduser("~"), ".bashrc")
    else:
        profile = os.path.join(os.path.expanduser("~"), ".profile")

    line = f'export HEAPTREE_API_KEY="{api_key}"\n'

    try:
        # Read existing if present and filter out previous definitions
        existing = ""
        if os.path.exists(profile):
            with open(profile, "r") as f:
                existing = f.read()
        new_content_lines = [
            l for l in existing.splitlines(keepends=True)
            if not l.lstrip().startswith("export HEAPTREE_API_KEY=")
        ]
        new_content_lines.append(line)
        with open(profile, "w") as f:
            f.writelines(new_content_lines)
        return profile, None
    except Exception as e:
        return None, str(e)


def cmd_login(args: argparse.Namespace) -> int:
    port = _find_free_port()
    state = _generate_state()
    callback = f"http://127.0.0.1:{port}/callback"
    st = _CallbackState(state)

    server = ThreadingHTTPServer(("127.0.0.1", port), _make_handler(st))

    # Serve in a background thread
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    try:
        # Construct platform login URL
        params = {
            "callback": callback,
            "state": state,
        }
        query = urllib.parse.urlencode(params)
        url = f"{DEFAULT_PLATFORM_URL}/cli/login?{query}"

        print(f"Opening browser for login at: {url}")
        opened = webbrowser.open(url, new=2)
        if not opened:
            print("Please open this URL manually to continue:", url)

        # Wait for callback
        if not st.wait(timeout=300):  # 5 minutes
            print("Login timed out. Please try again.")
            return 1

        if st.error:
            print(f"Login failed: {st.error}")
            return 1

        if not st.api_key:
            print("Login failed: no API key received.")
            return 1

        api_key = st.api_key
        _write_config(api_key)
        profile_path, profile_err = _update_shell_profile(api_key)

        print("Login successful.")
        print(f"API key saved to: {CONFIG_PATH}")
        if profile_path:
            # We cannot modify parent shell env; best we can do is update profile and instruct to source
            print(f"Added HEAPTREE_API_KEY to {profile_path}")
            shell = os.environ.get("SHELL", "")
            if shell.endswith("zsh"):
                print('Run `source ~/.zshrc` or open a new terminal to apply now.')
            elif shell.endswith("bash"):
                print('Run `source ~/.bashrc` or open a new terminal to apply now.')
            else:
                print('Open a new terminal to apply environment changes.')
        else:
            print("Could not update shell profile automatically.", file=sys.stderr)
            if profile_err:
                print(f"Reason: {profile_err}", file=sys.stderr)
            print('You can set it for this session with:', file=sys.stderr)
            print(f'  export HEAPTREE_API_KEY="{api_key}"', file=sys.stderr)

        return 0
    finally:
        try:
            server.shutdown()
        except Exception:
            pass
        try:
            server.server_close()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(prog="heaptree", description="Heaptree SDK CLI")
    sub = parser.add_subparsers(dest="command")

    # login command
    p_login = sub.add_parser("login", help="Authenticate via browser and configure your API key")
    p_login.set_defaults(func=cmd_login)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

