import pytest
from unittest.mock import patch
from flask import Flask
from io import BytesIO
from parkinsons_variant_viewer.web.routes import bp

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_index_route_mock(client):
    """Test index route without requiring a real template or DB."""
    with patch("parkinsons_variant_viewer.web.routes.get_db") as mock_get_db, \
         patch("parkinsons_variant_viewer.web.routes.render_template") as mock_render:
        mock_get_db.return_value.execute.return_value.fetchall.return_value = []
        mock_render.return_value = "mocked html"

        response = client.get("/")
        assert response.status_code == 200
        assert response.data == b"mocked html"

def test_add_variant_get(client):
    """Test GET /add returns the add_variant template."""
    with patch("parkinsons_variant_viewer.web.routes.render_template") as mock_render, \
         patch("parkinsons_variant_viewer.web.routes.get_db") as mock_get_db:
        mock_render.return_value = "mocked add_variant html"
        mock_get_db.return_value = None

        response = client.get("/add")
        assert response.status_code == 200
        assert response.data == b"mocked add_variant html"

def test_add_variant_post(client):
    """Test POST /add inserts data (DB mocked)."""
    with patch("parkinsons_variant_viewer.web.routes.get_db") as mock_get_db, \
         patch("parkinsons_variant_viewer.web.routes.redirect") as mock_redirect:
        mock_db = mock_get_db.return_value
        mock_db.execute.return_value = None
        mock_db.commit.return_value = None
        mock_redirect.return_value = "redirected"

        data = {
            "patient_id": "P001",
            "variant_number": "1",
            "chrom": "1",
            "pos": "12345",
            "id": "rs123",
            "ref": "A",
            "alt": "T"
        }

        response = client.post("/add", data=data)
        assert response.data == b"redirected"
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

def test_upload_data_route(client):
    """Test POST /upload route with a file without writing to disk."""
    with patch("parkinsons_variant_viewer.web.loaders.upload_handler.handle_uploaded_file") as mock_handler, \
         patch("werkzeug.datastructures.FileStorage.save") as mock_save:

        data = {
            "file": (BytesIO(b"test content"), "testfile.csv")
        }

        response = client.post("/upload", data=data, content_type="multipart/form-data")

        assert response.status_code == 200
        assert response.data == b"OK"
        mock_handler.assert_called_once()
        mock_save.assert_called_once()  # confirm save() was "called"
