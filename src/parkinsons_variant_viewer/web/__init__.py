from flask import Flask
from .db import close_db
from parkinsons_variant_viewer.utils.logger import logger

def create_app():  # pragma: no cover
    app = Flask(__name__)

    # Database lives in root-level instance folder
    app.config['DATABASE'] = 'instance/parkinsons.db'
    
    logger.info("Starting Parkinsons Variant Viewer application")  # pragma: no cover
    logger.info(f"Database location: {app.config['DATABASE']}")  # pragma: no cover

    # Import and register routes
    from .routes import bp
    app.register_blueprint(bp)
    logger.info("Routes registered successfully")  # pragma: no cover

    # Close DB connection on teardown
    app.teardown_appcontext(close_db)

    return app
