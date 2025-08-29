from flask import Flask
from flask_cors import CORS
from config import Config
from database import db, jwt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from sqlalchemy import event
        @event.listens_for(db.engine, 'connect')
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()

    from models.user import User
    from models.time_record import TimeRecord

    from routes.auth import auth_bp
    from routes.time_records import time_records_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(time_records_bp, url_prefix='/api')

    @app.cli.command()
    def init_db():
        """Initialize the database."""
        if 'y' in input("Are you sure you want to do this? (y to proceed) ").lower():
            db.drop_all()
            db.create_all()
            print("Database tables created successfully!")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
