import pytest
from parkinsons_variant_viewer.web import create_app
from parkinsons_variant_viewer.web.routes import bp
from parkinsons_variant_viewer.web.db import close_db
from flask import Flask

def test_create_app():
    """Test that create_app sets up the Flask app correctly."""
    app = create_app()

    # 1. Check app is Flask instance
    assert isinstance(app, Flask)

    # 2. Check DATABASE config
    assert app.config['DATABASE'] == 'instance/parkinsons.db'

    # 3. Check the blueprint is registered
    assert bp.name in app.blueprints

    # 4. Check teardown function is registered
    assert close_db in app.teardown_appcontext_funcs
