from flask import Flask
from .routes import main
from flask_cors import CORS
from dotenv import load_dotenv
import os
def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(main)

    #Upload PDF size
    #app.config['MAX_SIZE'] = int(os.getenv('MAX_SIZE', 12*1024*1024)) #made a size.env for this
    return app
