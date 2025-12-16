#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import ipaddress
import os
import secrets
import ssl
import sys
import tempfile
import time
import threading
import socket
from datetime import datetime, timedelta, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from https_login import __version__


# ──────────────────────────────────────────────────────────────
# Cookie Session
# ──────────────────────────────────────────────────────────────

COOKIE_NAME = "HLS"
COOKIE_TTL_SECONDS = 8 * 60 * 60  # 8h


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64u_dec(s: str) -> bytes:
    return base64.urlsafe_b64decode((s + "=" * (-len(s) % 4)).encode("ascii"))


def make_cookie(secret: bytes) -> str:
    ts = str(int(time.time())).encode("ascii")
    nonce = os.urandom(16)
    payload = ts + b"." + _b64u(nonce).encode("ascii")
    sig = hmac.new(secret, payload, hashlib.sha256).digest()
    return _b64u(payload) + "." + _b64u(sig)


def verify_cookie(secret: bytes, cookie_value: str) -> bool:
    try:
        p, s = cookie_value.split(".", 1)
        payload = _b64u_dec(p)
        sig = _b64u_dec(s)

        expected = hmac.new(secret, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            return False

        ts = int(payload.split(b".", 1)[0])
        return (time.time() - ts) <= COOKIE_TTL_SECONDS
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────
# Password Hashing (PBKDF2)
# ──────────────────────────────────────────────────────────────

def hash_password(password: str, iterations: int = 200_000) -> str:
    """
    Format: pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>
    """
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${_b64u(salt)}${_b64u(dk)}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, it_s, salt_b64, hash_b64 = stored.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False

        iterations = int(it_s)
        salt = _b64u_dec(salt_b64)
        expected = _b64u_dec(hash_b64)

        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────
# HTML Login Page
# ──────────────────────────────────────────────────────────────

LOGIN_PAGE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Login</title>
</head>
<body>
  <h2>Login</h2>

  <form method="POST" action="/__login">
    <input type="password" name="password" placeholder="Passwort">
    <br><br>
    __ERROR__
    <br>
    <button type="submit">Login</button>
  </form>
</body>
</html>
"""


# ──────────────────────────────────────────────────────────────
# Request Handler
# ──────────────────────────────────────────────────────────────

class LoginHandler(SimpleHTTPRequestHandler):
    pw_hash: str = ""   # PBKDF2 string
    secret: bytes = b""

    def _authed(self) -> bool:
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            part = part.strip()
            if part.startswith(COOKIE_NAME + "="):
                return verify_cookie(self.secret, part.split("=", 1)[1])
        return False

    def _send_login(self, error: str = "") -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        err_html = f"<p style='color:red'>{error}</p>" if error else ""
        html = LOGIN_PAGE.replace("__ERROR__", err_html)
        self.wfile.write(html.encode("utf-8"))

    def do_GET(self):
        if self.path.startswith("/__login"):
            return self._send_login()

        if not self._authed():
            return self._send_login()

        return super().do_GET()

    def do_POST(self):
        if self.path != "/__login":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        pw = (parse_qs(body).get("password") or [""])[0]

        if not verify_password(pw, self.pw_hash):
            # Track failed attempts by IP address
                        client_ip = self.client_address[0]
                        if not hasattr(LoginHandler, '_failed_attempts'):
                            LoginHandler._failed_attempts = {}
                        
                        LoginHandler._failed_attempts[client_ip] = LoginHandler._failed_attempts.get(client_ip, 0) + 1
                        
                        if LoginHandler._failed_attempts[client_ip] >= 5:
                            self.send_error(403, "Too many failed login attempts. Access blocked.")
                            return
                        
                        attempts_left = 5 - LoginHandler._failed_attempts[client_ip]
                        return self._send_login(f"Wrong password. {attempts_left} attempts left.")
        # Reset failed attempts on successful login
        client_ip = self.client_address[0]
        if hasattr(LoginHandler, '_failed_attempts') and client_ip in LoginHandler._failed_attempts:
            del LoginHandler._failed_attempts[client_ip]


        cookie_val = make_cookie(self.secret)
        self.send_response(302)
        self.send_header("Location", "/")
        self.send_header(
            "Set-Cookie",
            # Secure is correct for HTTPS, HttpOnly prevents JS access
            f"{COOKIE_NAME}={cookie_val}; Path=/; HttpOnly; SameSite=Strict; Secure"
        )
        self.end_headers()


# ──────────────────────────────────────────────────────────────
# Temp self-signed Certificate (cryptography)
# ──────────────────────────────────────────────────────────────

def generate_cert(cert_path: str, key_path: str, host: str) -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, host),
    ])

    san_entries = []
    # DNSName is fine for "localhost" etc. For IPs, x509.IPAddress is actually needed.
    # To keep it robust, we always create DNSName. (Browser warning remains anyway due to self-signed.)
    # Add the provided host
    san_entries.append(x509.DNSName(host))
    
    # Add localhost and 127.0.0.1
    san_entries.append(x509.DNSName("localhost"))
    try:
        san_entries.append(x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")))
    except Exception:
        pass
    
    # Add network IP addresses
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            try:
                # Try IPv4
                san_entries.append(x509.IPAddress(ipaddress.IPv4Address(ip)))
            except Exception:
                try:
                    # Try IPv6
                    san_entries.append(x509.IPAddress(ipaddress.IPv6Address(ip)))
                except Exception:
                    pass
    except Exception:
        pass


    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc) - timedelta(minutes=1))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=1))
        .add_extension(x509.SubjectAlternativeName(san_entries), critical=False)
        .sign(key, hashes.SHA256())
    )

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_path, "wb") as f:
        f.write(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            )
        )


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        prog="https-login",
        description="HTTPS file server with temporary self-signed cert + simple login (PBKDF2 hash).",
    )
    ap.add_argument("-v","--version", action="version",
                    version=f"https-login {__version__} from {os.path.dirname(__file__)} (python {sys.version_info.major}.{sys.version_info.minor})")
    ap.add_argument("-b","--bind", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    ap.add_argument("-P","--port", type=int, default=8443, help="Port (default: 8443)")
    ap.add_argument("-d","--dir", default=".", help="Directory to serve (default: current)")
    ap.add_argument("-H","--host", default="localhost",
                    help="Hostname/IP used in printed URL and certificate CN/SAN (default: localhost)")

    ap.add_argument("-f","--passfile", default=".https_login_pass",
                    help="File containing password hash (default: .https_login_pass)")
    ap.add_argument("-sp","--set-password",
                    help="Set password and write hash into passfile, then exit.")
    ap.add_argument("-p", "--password",
                    help="Password used only if passfile does not exist (otherwise ignored). "
                         "If neither passfile exists nor -p is given, default is 'admin'.")

    args = ap.parse_args()

    # 1) Set-password mode
    if args.set_password:
        pw_hash = hash_password(args.set_password)
        with open(args.passfile, "w", encoding="utf-8") as f:
            f.write(pw_hash + "\n")
        print(f"OK: Passwort-Hash gespeichert in {args.passfile}")
        return

    # 2) Load hash from passfile if exists
    pw_hash = ""
    if os.path.exists(args.passfile):
        with open(args.passfile, "r", encoding="utf-8") as f:
            pw_hash = f.read().strip()

    # 3) If no hash file, derive from -p or default
    if not pw_hash:
        raw = args.password if args.password else "admin"
        pw_hash = hash_password(raw)

    LoginHandler.pw_hash = pw_hash
    LoginHandler.secret = os.urandom(32)

    def handler_factory(*h_args, **h_kwargs):
        return LoginHandler(*h_args, directory=args.dir, **h_kwargs)

    httpd = HTTPServer((args.bind, args.port), handler_factory)

    # Temp cert/key: auto cleanup
    with tempfile.TemporaryDirectory(prefix="https_login_") as td:
        cert_path = os.path.join(td, "cert.pem")
        key_path = os.path.join(td, "key.pem")
        generate_cert(cert_path, key_path, args.host)

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert_path, key_path)
        httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

        print(f"Serving on: https://{args.host}:{args.port}/")
        print(f"Directory:  {os.path.abspath(args.dir)}")
        if os.path.exists(args.passfile):
            print(f"Password:   (hashed, loaded from {args.passfile})")
        else:
            used = args.password if args.password else "admin"
            print(f"Password:   {used!r}  (no passfile found; consider --set-password)")
        print("self-signed cert => Browser warning is normal.")
        print("Press Ctrl+C to stop.")

        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping server...")
        finally:
            try:
                httpd.shutdown()
            except Exception:
                pass
            try:
                httpd.server_close()
            except Exception:
                pass


if __name__ == "__main__":
    main()