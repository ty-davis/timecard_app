from flask import Flask
from flask_cors import CORS
from config import Config
from database import db, jwt, migrate
import click
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from sqlalchemy import event
        @event.listens_for(db.engine, 'connect')
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()

    from models.user import User
    from models.time_record import TimeRecord
    from models.jira import JiraConnection, JiraSyncLog

    from routes.auth import auth_bp
    from routes.time_records import time_records_bp
    from routes.jira import jira_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(time_records_bp, url_prefix='/api')
    app.register_blueprint(jira_bp, url_prefix='/api')

    @app.cli.command()
    def init_db():
        """Initialize the database."""
        if 'y' in input("Are you sure you want to do this? (y to proceed) ").lower():
            db.drop_all()
            db.create_all()
            print("Database tables created successfully!")


    @app.cli.command("reset-password")
    @click.argument("username")
    @click.argument("password")
    def reset_password(username, password):
        """Resets a user's password."""
        user = User.query.filter_by(username=username).first()
        if user:
            user.set_password(password)
            db.session.commit()
            print(f"Password for user '{username}' has been reset.")
        else:
            print(f"User '{username}' not found.")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
