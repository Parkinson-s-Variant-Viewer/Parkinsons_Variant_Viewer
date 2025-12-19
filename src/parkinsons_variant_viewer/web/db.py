import sqlite3
from pathlib import Path
from flask import g, current_app
from parkinsons_variant_viewer.utils.logger import logger

# Return an open database connection (cached per request)
def get_db():
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        logger.debug(f"Opening database connection: {db_path}")
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

# Close the database connection when the request ends 
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        logger.debug("Closing database connection")
        db.close()

# Initialise the database using schema.sql 
def init_db():
    # Ensure instance folder exists
    db_path = Path(current_app.config['DATABASE'])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Initializing database at: {db_path}")

    db = get_db()

    # Schema file relative to Flask app
    schema_path = Path(current_app.root_path) / 'schema.sql'
    if not schema_path.exists():
        logger.error(f"Schema file not found: {schema_path}")
        raise FileNotFoundError(f"Cannot find {schema_path}")

    logger.info(f"Executing schema from: {schema_path}")
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    
    logger.info("Database initialization complete")

# Helper so loader can get DB path
def get_db_path(): 
    """
    Return the absolute path to the SQLite database file.
    """
    return str(Path(current_app.config['DATABASE']).resolve())