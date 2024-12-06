from flask import Flask, render_template
from flask_cors import CORS
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)
    
    # Initialize Firebase Admin
    from .firebase_admin import firebase_admin
    firebase_admin.init_app(app)
    
    # Register blueprints
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app
