from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

limiter = Limiter(default_limits=["5/second"], key_func=get_remote_address)
migrate = Migrate()
db = SQLAlchemy()