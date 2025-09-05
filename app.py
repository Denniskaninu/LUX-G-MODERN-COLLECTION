import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    # Create the app
    app = Flask(__name__)
    
    # Configure app
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration
    database_url = os.environ.get("DATABASE_URL", "sqlite:///kubwa_closet.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Additional config
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB max file size
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['ADMIN_PATH_SLUG'] = os.environ.get("ADMIN_PATH_SLUG", "hummingbird-42")
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure SQLite for WAL mode and foreign keys
    if database_url.startswith('sqlite'):
        from sqlalchemy import event
        from sqlalchemy.engine import Engine
        
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
    
    # Import models and create tables
    with app.app_context():
        import models
        db.create_all()
        
        # Create uploads directories
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'original'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'web'), exist_ok=True)
        
        # Create admin user if not exists
        from models import AdminUser
        from werkzeug.security import generate_password_hash
        
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
        
        if not AdminUser.query.filter_by(username=admin_username).first():
            admin_user = AdminUser(
                username=admin_username,
                password_hash=generate_password_hash(admin_password)
            )
            db.session.add(admin_user)
            db.session.commit()
            logging.info(f"Created admin user: {admin_username}")
    
    # Register blueprints
    from routes.public import public_bp
    from routes.admin import admin_bp
    from routes.auth import auth_bp
    from routes.reports import reports_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix=f'/admin/{app.config["ADMIN_PATH_SLUG"]}')
    app.register_blueprint(auth_bp, url_prefix='/admin')
    app.register_blueprint(reports_bp, url_prefix=f'/admin/{app.config["ADMIN_PATH_SLUG"]}/reports')
    
    return app

# Create the app instance
app = create_app()
