from flask import Flask
from .routes import main

def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(main)
    
    #Upload PDF Size
    app.config['MAX_SIZE']=12*1024*1024 #up to 12 MB only
    return app
