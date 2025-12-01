# app.py
import os
import time
import uuid
import logging
from functools import wraps
from urllib.parse import urlencode, urlparse

from flask import Flask, render_template, request, redirect, jsonify, session, url_for, abort
from dotenv import load_dotenv
import msal
import jwt  # PyJWT
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

load_dotenv()

# ---------- Config ----------
APP_NAME = "Central Auth Gateway - WoW Demo Lab"
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or "dev_secret_key_change_me"
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_REDIRECT_URI = os.getenv("AZURE_REDIRECT_URI")  # must match Azure AD registration
AZURE_AUTHORITY = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}" if AZURE_TENANT_ID else None
AZURE_SCOPES = ["openid", "profile", "email"]

# Internal JWT (RS256) settings
JWT_ISSUER = os.getenv("JWT_ISSUER", "https://auth.wow-demo-lab.internal")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "wow-demo-lab")
JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", "3600"))

# Key paths (optional). If not provided, app generates an ephemeral keypair (dev only).
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH", "")
PUBLIC_KEY_PATH = os.getenv("PUBLIC_KEY_PATH", "")

# Allowed downstream targets (whitelist) - comma separated in .env
TARGET_WHITELIST = [u.strip() for u in os.getenv("TARGET_WHITELIST", "").split(",") if u.strip()]

# HTTPS enforcement (set to "true" in env to force)
ENFORCE_HTTPS = os.getenv("ENFORCE_HTTPS", "true").lower() in ("1", "true", "yes")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

# ---------- Flask app ----------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = FLASK_SECRET_KEY

# ---------- Key management ----------
if PRIVATE_KEY_PATH and os.path.exists(PRIVATE_KEY_PATH) and PUBLIC_KEY_PATH and os.path.exists(PUBLIC_KEY_PATH):
    with open(PRIVATE_KEY_PATH, "rb") as f:
        PRIVATE_KEY = f.read()
    with open(PUBLIC_KEY_PATH, "rb") as f:
        PUBLIC_KEY = f.read()
    logger.info("Loaded RSA keypair from disk.")
else:
    # Generate ephemeral RSA keypair (dev). For production, provide files and set PRIVATE_KEY_PATH/PUBLIC_KEY_PATH.
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    PRIVATE_KEY = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    PUBLIC_KEY = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    logger.warning("No RSA keypair provided; generated ephemeral keys (dev only).")

# ---------- MSAL client factory ----------
def _build_msal_app(cache=None):
    if not AZURE_CLIENT_ID or not AZURE_CLIENT_SECRET or not AZURE_AUTHORITY or not AZURE_REDIRECT_URI:
        raise RuntimeError("Azure AD configuration missing. Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID, AZURE_REDIRECT_URI.")
    return msal.ConfidentialClientApplication(
        AZURE_CLIENT_ID,
        authority=AZURE_AUTHORITY,
        client_credential=AZURE_CLIENT_SECRET,
        token_cache=cache,
    )

# ---------- Helpers ----------
def is_valid_target(target_url):
    if not TARGET_WHITELIST:
        # If no whitelist configured, be conservative and reject unless target is same host (not recommended)
        return False
    try:
        parsed = urlparse(target_url)
        if parsed.scheme not in ("https",):
            return False
        # match host + optional path prefix
        for allowed in TARGET_WHITELIST:
            if target_url.startswith(allowed):
                return True
        return False
    except Exception:
        return False

def require_https(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if ENFORCE_HTTPS and request.scheme != "https":
            # Redirect to https equivalent
            url = request.url.replace("http://", "https://", 1)
            return redirect(url, code=301)
        return f(*args, **kwargs)
    return decorated

def issue_internal_jwt(user_email, target):
    now = int(time.time())
    payload = {
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "sub": user_email,
        "email": user_email,
        "iat": now,
        "exp": now + JWT_EXP_SECONDS,
        "target": target,
        "jti": str(uuid.uuid4())
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
    return token

# ---------- Routes ----------
@app.route("/")
@require_https
def index():
    # Simple UI: user can paste target app URL (or it can be provided by the app as ?target=...)
    target = request.args.get("target", "")
    return render_template("index.html", app_name=APP_NAME, target=target)

@app.route("/login", methods=["GET"])
@require_https
def login():
    # Start Azure AD auth flow. Expect a 'target' query param (downstream app URL).
    target = request.args.get("target", "").strip()
    if not target or not is_valid_target(target):
        return render_template("index.html", app_name=APP_NAME, error="Invalid or missing target URL. Contact admin."), 400

    session["target"] = target
    msal_app = _build_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        scopes=AZURE_SCOPES,
        redirect_uri=AZURE_REDIRECT_URI,
        state=str(uuid.uuid4())
    )
    return redirect(auth_url)

@app.route("/oauth/callback")
@require_https
def oauth_callback():
    # Azure AD redirects here with ?code=...&state=...
    error = request.args.get("error")
    if error:
        return render_template("complete.html", success=False, message=f"Azure AD error: {error}")

    code = request.args.get("code")
    if not code:
        return render_template("complete.html", success=False, message="Missing authorization code from Azure AD.")

    # Exchange code for tokens
    try:
        msal_app = _build_msal_app()
        result = msal_app.acquire_token_by_authorization_code(
            code,
            scopes=AZURE_SCOPES,
            redirect_uri=AZURE_REDIRECT_URI
        )
    except Exception as e:
        logger.exception("Token exchange failed")
        return render_template("complete.html", success=False, message="Token exchange failed.")

    if "error" in result:
        logger.error("Token exchange error: %s", result.get("error_description"))
        return render_template("complete.html", success=False, message="Token exchange error: " + result.get("error_description", "unknown"))

    # Extract email from id_token claims
    id_claims = result.get("id_token_claims", {})
    user_email = id_claims.get("email") or id_claims.get("preferred_username") or id_claims.get("upn")
    if not user_email:
        return render_template("complete.html", success=False, message="Could not extract email from Azure id_token.")

    # Build internal JWT and redirect to target
    target = session.pop("target", None)
    if not target or not is_valid_target(target):
        return render_template("complete.html", success=False, message="Invalid or missing target URL after auth.")

    token = issue_internal_jwt(user_email, target)
    # For demo: append token as query param. In production prefer POST handoff or header injection via proxy.
    redirect_url = target.rstrip("/") + "/?auth_token=" + token
    logger.info("Issued token jti=%s for %s -> %s", jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"], options={"verify_signature": False}).get("jti"), user_email, target)
    return redirect(redirect_url)

@app.route("/public-key")
def public_key():
    # Expose public key for downstream apps to validate RS256 tokens
    return PUBLIC_KEY, 200, {"Content-Type": "text/plain"}

@app.route("/introspect", methods=["POST"])
def introspect():
    # Optional: simple introspection endpoint for downstream apps to validate token server-side
    data = request.json or {}
    token = data.get("token")
    if not token:
        return jsonify({"active": False}), 400
    try:
        decoded = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"], audience=JWT_AUDIENCE, issuer=JWT_ISSUER)
        return jsonify({"active": True, "claims": decoded})
    except jwt.ExpiredSignatureError:
        return jsonify({"active": False, "reason": "expired"}), 200
    except Exception as e:
        return jsonify({"active": False, "reason": "invalid"}), 200

# Health check
@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": int(time.time())})

# ---------- Run ----------
if __name__ == "__main__":
    # Enforce HTTPS in dev by running with a local cert if present; otherwise warn and run without SSL (not recommended).
    host = "0.0.0.0"
    port = int(os.getenv("PORT", "5000"))
    cert = os.getenv("SSL_CERT_PATH", "cert.pem")
    key = os.getenv("SSL_KEY_PATH", "key.pem")
    if os.path.exists(cert) and os.path.exists(key):
        logger.info("Starting with HTTPS on port %s", port)
        app.run(host=host, port=port, ssl_context=(cert, key), debug=True)
    else:
        if ENFORCE_HTTPS:
            logger.warning("SSL cert/key not found. ENFORCE_HTTPS is true but no certs present. For local dev, generate cert.pem/key.pem or set ENFORCE_HTTPS=false (not recommended).")
        logger.info("Starting without HTTPS (dev).")
        app.run(host=host, port=port, debug=True)