import sqlite3
from pathlib import Path
from flask import g, current_app

# Return an open database connection (cached per request)
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

# Close the database connection when the request ends 
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialise the database using schema.sql 
def init_db():
    # Ensure instance folder exists
    db_path = Path(current_app.config['DATABASE'])
    db_path.parent.mkdir(parents=True, exist_ok=True)

    db = get_db()

    # Schema file relative to Flask app
    schema_path = Path(current_app.root_path) / 'schema.sql'
    if not schema_path.exists():
        raise FileNotFoundError(f"Cannot find {schema_path}")

    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())

# Helper so loader can get DB path
def get_db_path(): 
    """
    Return the absolute path to the SQLite database file.
    """
    return str(Path(current_app.config['DATABASE']).resolve())