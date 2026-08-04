import os
import json
from pathlib import Path

# Prefer environment variables, fall back to credentials/google_credentials.json
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
    cred_path = Path(__file__).resolve().parents[1] / "credentials" / "google_credentials.json"
    if cred_path.exists():
        try:
            data = json.loads(cred_path.read_text())
            web = data.get("web", {})
            GOOGLE_CLIENT_ID = GOOGLE_CLIENT_ID or (web.get("client_id") or None)
            GOOGLE_CLIENT_SECRET = GOOGLE_CLIENT_SECRET or (web.get("client_secret") or web.get("client_secret_id") or None)
            # Try to pull redirect URI from file if missing in env
            if not GOOGLE_REDIRECT_URI:
                uris = web.get("redirect_uris") or []
                if uris:
                    GOOGLE_REDIRECT_URI = uris[0]
        except Exception:
            # keep None values if parsing fails
            pass

# Default redirect URI if still missing
if not GOOGLE_REDIRECT_URI:
    GOOGLE_REDIRECT_URI = "http://localhost:8501"