import os
from dotenv import load_dotenv

load_dotenv()
base = os.path.abspath(os.path.dirname(__file__))

def get_env_bool(value, default):
    env = os.environ.get(value)

    if not env:
        return default

    return env[0].lower() in ("1", "t")

class Config(object):
    DEBUG = False
    TESTING = False

    APPLICATION_NAME = os.getenv("APPLICATION_NAME", "Space")

    # Security
    CSRF_ENABLED = True
    RATELIMIT_ENABLED = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "testing")
    INVITE_ONLY = get_env_bool("INVITE_ONLY", False)
    ANONYMOUS_UPLOADS = get_env_bool("ANONYMOUS_UPLOADS", True)

    RECAPTCHA_ENABLED = get_env_bool("RECAPTCHA_ENABLED", False)
    RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY", None)
    RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY", None)

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:////space.db")

    # File Related
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "./files/")
    FILE_UPLOAD_BASE = os.environ.get("FILE_UPLOAD_BASE", None)
    API_URL_BASE = os.environ.get("API_URL_BASE", None)

    EXTENSIONS_ALLOWED = []
    EXTENSIONS_DISALLOWED = ["exe", "bin", "sh", "bat", "vbs", "pdf", "php"]
    EXTENSIONS_TWO = [".tar.gz", ".tar.bz2"]

    FILE_NAME_LENGTH = 10
    FILE_EXT_MAX_LENGTH = 7

class Production(Config):
    DEBUG = False
    RATELIMIT_ENABLED = True
    JSONIFY_PRETTYPRINT_REGULAR = False
    MAX_CONTENT_LENGTH = 128 * 1024 * 1024

class Staging(Config):
    DEVELOPMENT = True
    DEBUG = True

class Development(Config):
    DEVELOPMENT = True
    DEBUG = True

class Testing(Config):
    TESTING = True
