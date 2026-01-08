"""
Database utility functions for the Parkinson's Variant Viewer web app.

Provides helpers to get and close a database connection, initialize
the database from schema.sql, and return the database path.
"""

import sqlite3
from pathlib import Path
from flask import g, current_app

from parkinsons_variant_viewer.utils.logger import logger

def get_db():
    """
    Get a SQLite database connection for the current Flask request.

    If no connection exists in the request context, a new connection
    is created and cached in `g.db`. The connection uses `sqlite3.Row`
    for row access.

    Returns
    -------
    sqlite3.Connection
        Open SQLite connection for the current request.
    """
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        logger.debug(f"Opening database connection: {db_path}")
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    Close the SQLite database connection for the current Flask request.

    If a connection exists in the request context (`g.db`), it is closed
    and removed from `g`. Intended to be registered with Flask's
    `teardown_appcontext`.

    Parameters
    ----------
    e : Exception or None, optional
        Optional exception argument provided by Flask during teardown.
        Defaults to None.
    """
    db = g.pop('db', None)
    if db is not None:
        logger.debug("Closing database connection")
        db.close()

def init_db():
    """
    Initialize the SQLite database by executing schema.sql.

    Ensures that the parent folder for the database exists. Reads and
    executes the SQL statements from `schema.sql` located in the Flask
    app root. Raises a `FileNotFoundError` if the schema file is missing.

    Returns
    -------
    None
    """
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

def get_db_path(): 
    """
    Helper so loader can get the DB path. 
    Return the absolute path to the SQLite database file.

    Returns
    -------
    str
        Absolute path to the database file.
    """
    return str(Path(current_app.config['DATABASE']).resolve())