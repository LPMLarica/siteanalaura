from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"

DATABASE_DIR = BASE_DIR / "storage"

LOG_DIR = DATABASE_DIR / "logs"

BACKUP_DIR = DATABASE_DIR / "backups"

CREDENTIALS_DIR = BASE_DIR / "credentials"