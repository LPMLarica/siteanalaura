import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


def init_firebase_app():
    # Prefer explicit FIREBASE_CREDENTIALS env var, else use GOOGLE_APPLICATION_CREDENTIALS
    cred_path = os.getenv("FIREBASE_CREDENTIALS") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise RuntimeError(
            "Firebase credentials not found. Set FIREBASE_CREDENTIALS or GOOGLE_APPLICATION_CREDENTIALS to the service account JSON path."
        )

    cred_path = Path(cred_path)
    if not cred_path.exists():
        raise RuntimeError(f"Firebase credentials file not found: {cred_path}")

    cred = credentials.Certificate(str(cred_path))

    # Avoid reinitializing app
    try:
        app = firebase_admin.get_app()
    except ValueError:
        app = firebase_admin.initialize_app(cred)

    return firestore.client(app=app)


_client = None


def get_firestore_client():
    global _client
    if _client is None:
        _client = init_firebase_app()
    return _client
