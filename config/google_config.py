import os
import json
from pathlib import Path

# Load .env from project root if present so env vars can be defined there
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

project_root = Path(__file__).resolve().parents[1]
dotenv_path = project_root / ".env"
if load_dotenv:
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
    else:
        # fallback to default search
        load_dotenv()

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
            # If the JSON uses placeholder tokens like ${GOOGLE_CLIENT_ID}, treat them as missing
            def _clean(val):
                if not val:
                    return None
                if isinstance(val, str) and "${" in val:
                    return None
                return val

            GOOGLE_CLIENT_ID = GOOGLE_CLIENT_ID or _clean(web.get("client_id") or None)
            GOOGLE_CLIENT_SECRET = GOOGLE_CLIENT_SECRET or _clean(web.get("client_secret") or web.get("client_secret_id") or None)
            # Try to pull redirect URI from file if missing in env
            if not GOOGLE_REDIRECT_URI:
                uris = web.get("redirect_uris") or []
                if uris:
                    # ignore placeholder-style entries
                    first = uris[0]
                    if isinstance(first, str) and "${" in first:
                        pass
                    else:
                        GOOGLE_REDIRECT_URI = first
        except Exception:
            # keep None values if parsing fails
            pass

# Default redirect URI if still missing
if not GOOGLE_REDIRECT_URI:
    GOOGLE_REDIRECT_URI = "http://localhost:8501"