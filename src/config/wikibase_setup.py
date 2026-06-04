import json
import sys
from pathlib import Path
from typing import Any

from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.wbi_login import Login


def _app_dir() -> Path:
    """Return the directory containing the application (works with PyInstaller)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


CONFIG_FILE = _app_dir() / "config.json"

DEFAULT_CONFIG = {
    "DEFAULT_LANGUAGE": "nl",
    "WIKIBASE_URL": "https://kg.kunsten.be",
    "MEDIAWIKI_API_URL": "https://kg.kunsten.be/w/api.php",
    "MEDIAWIKI_INDEX_URL": "https://kg.kunsten.be/w/index.php",
    "MEDIAWIKI_REST_URL": "https://kg.kunsten.be/w/rest.php",
    "SPARQL_ENDPOINT_URL": "https://kg.kunsten.be/query/proxy/wdqs/bigdata/namespace/wdq/sparql",
}


def load() -> dict[str, Any]:
    """Load config from the JSON file, or return defaults if the file doesn't exist."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            stored = json.load(f)
        # Merge: keep any keys the user may have added, fall back to defaults
        return {**DEFAULT_CONFIG, **stored}
    return dict(DEFAULT_CONFIG)


def sanitize(config: dict[str, Any]) -> dict[str, Any]:
    """Strip whitespace and trailing '/' for URL settings."""
    sanitized = {}
    for key, value in config.items():
        if isinstance(value, str):
            value = value.strip()
            if key.endswith("_URL"):
                value = value.rstrip("/")
        sanitized[key] = value
    return sanitized


def save(config: dict[str, Any]) -> None:
    """Save the given config dict to the JSON file."""
    CONFIG_FILE.write_text(json.dumps(config, indent=2) + "\n")


def apply(config: dict[str, Any]) -> None:
    """Apply the given config dict to the global wikibaseintegrator config."""
    for key in (
        "DEFAULT_LANGUAGE",
        "WIKIBASE_URL",
        "MEDIAWIKI_API_URL",
        "MEDIAWIKI_INDEX_URL",
        "MEDIAWIKI_REST_URL",
        "SPARQL_ENDPOINT_URL",
    ):
        if key in config:
            wbi_config[key] = config[key]


def create_login(user: str, password: str) -> Login:
    """Create and return a logged-in session for the given credentials."""
    return Login(user=user, password=password)
