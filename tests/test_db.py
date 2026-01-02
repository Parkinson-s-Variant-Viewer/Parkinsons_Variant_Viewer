"""Tests for db.py module."""
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from flask import Flask, g

from parkinsons_variant_viewer.web.db import get_db, close_db, init_db, get_db_path

# ----------------------
# Global patch for sqlite3.connect
# ----------------------
@pytest.fixture(autouse=True)
def mock_sqlite_connect():
    # Patch sqlite3.connect everywhere in the module
    with patch('parkinsons_variant_viewer.web.db.sqlite3.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        yield mock_connect

# ----------------------
# Flask app fixture
# ----------------------
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['DATABASE'] = 'test.db'
    app.config['TESTING'] = True
    with app.app_context():
        yield app

# ----------------------
# get_db() tests
# ----------------------
def test_get_db_creates_connection(app):
    db = get_db()
    assert db is not None
    assert g.db is db

    # calling again returns same object
    db2 = get_db()
    assert db2 is db

# ----------------------
# close_db() tests
# ----------------------
def test_close_db_closes_connection(app):
    db = get_db()
    close_db()
    assert 'db' not in g
    db.close.assert_called_once()

def test_close_db_no_connection(app):
    close_db()
    assert 'db' not in g

# ----------------------
# init_db() tests
# ----------------------
def test_init_db_runs_script(app):
    with patch('parkinsons_variant_viewer.web.db.Path.mkdir') as mock_mkdir, \
         patch('parkinsons_variant_viewer.web.db.Path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data='CREATE TABLE test(id int);')), \
         patch('parkinsons_variant_viewer.web.db.get_db') as mock_get_db:

        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        init_db()

        # Ensure folder creation attempted
        mock_mkdir.assert_called()
        # Ensure schema SQL executed
        mock_db.executescript.assert_called_once_with('CREATE TABLE test(id int);')

def test_init_db_schema_missing(app):
    with patch('parkinsons_variant_viewer.web.db.Path.exists', return_value=False):
        import pytest
        with pytest.raises(FileNotFoundError):
            init_db()

# ----------------------
# get_db_path() test
# ----------------------
def test_get_db_path(app):
    path = get_db_path()
    assert Path(path).is_absolute()
    assert path.endswith('test.db')
