from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from flask_migrate import Migrate

# database config
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
