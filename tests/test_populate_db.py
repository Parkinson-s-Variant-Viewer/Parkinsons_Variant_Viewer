"""Tests for populate_db.py module."""
from flask import Flask
import pytest
import sqlite3
import sys
import types

@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database with inputs and outputs tables."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)

    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE inputs (
            patient_id INTEGER NOT NULL,
            variant_number INTEGER NOT NULL,
            chrom TEXT NOT NULL,
            pos INTEGER NOT NULL,
            id TEXT,
            ref TEXT NOT NULL,
            alt TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (patient_id, variant_number)
        );

        CREATE TABLE outputs (
            patient_id INTEGER NOT NULL,
            variant_number INTEGER NOT NULL,
            hgvs TEXT,
            clinvar_id TEXT,
            clinical_significance TEXT,
            star_rating INTEGER,
            review_status TEXT,
            conditions_assoc TEXT,
            transcript TEXT,
            ref_seq_id TEXT,
            hgnc_id TEXT,
            omim_id TEXT,
            gene_symbol TEXT,
            g_change TEXT,
            c_change TEXT,
            p_change TEXT,
            analysed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (patient_id, variant_number),
            FOREIGN KEY (patient_id, variant_number)
                REFERENCES inputs (patient_id, variant_number)
                ON DELETE CASCADE
        );
        """
    )

    conn.execute(
        """
        INSERT INTO inputs
        VALUES (1, 1, '1', 12345, 'rs1', 'A', 'G', CURRENT_TIMESTAMP)
        """
    )

    conn.commit()
    conn.close()
    return db_path


def test_populate_db_inserts_output(temp_db, monkeypatch):
    """Test that the populate_database function inserts outputs correctly."""
    # ----------------------------------------------------
    # 1. Fake web.create_app
    # ----------------------------------------------------
    fake_web = types.ModuleType("parkinsons_variant_viewer.web")

    def fake_create_app():
        app = Flask(__name__)
        app.config["DATABASE"] = str(temp_db)
        return app

    fake_web.create_app = fake_create_app
    sys.modules["parkinsons_variant_viewer.web"] = fake_web

    # ----------------------------------------------------
    # 2. Fake web.db.get_db_path
    # ----------------------------------------------------
    fake_web_db = types.ModuleType("parkinsons_variant_viewer.web.db")

    def fake_get_db_path():
        return str(temp_db)

    fake_web_db.get_db_path = fake_get_db_path
    sys.modules["parkinsons_variant_viewer.web.db"] = fake_web_db

    # ----------------------------------------------------
    # 3. Import MODULE
    # ----------------------------------------------------
    import parkinsons_variant_viewer.populate_db as populate_db

    # ----------------------------------------------------
    # 4. Mock HGVSVariant
    # ----------------------------------------------------
    class MockHGVSVariant:
        def __init__(self, *args, **kwargs):
            pass

        def fetch(self):
            return {"hgvs_genomic": "NC_000001.11:g.12345A>G"}

    monkeypatch.setattr(populate_db, "HGVSVariant", MockHGVSVariant)

    # ----------------------------------------------------
    # 5. Mock ClinVar
    # ----------------------------------------------------
    monkeypatch.setattr(populate_db, "fetch_clinvar_variant", lambda _: {})
    monkeypatch.setattr(
        populate_db,
        "get_variant_info",
        lambda _: types.SimpleNamespace(
            hgvs="NC_000001.11:g.12345A>G",
            clinvar_id="123",
            clinical_significance="Benign",
            star_rating=1,
            review_status="single submitter",
            conditions_assoc="None",
            transcript="NM_000001.1",
            ref_seq_id="NC_000001.11",
            hgnc_id="HGNC:1",
            omim_id="1",
            gene_symbol="GENE1",
            g_change="g.12345A>G",
            c_change="c.123A>G",
            p_change="p.Lys41Arg",
        ),
    )

    # ----------------------------------------------------
    # 6. Disable sleep to speed up test
    # ----------------------------------------------------
    monkeypatch.setattr(populate_db.time, "sleep", lambda _: None)

    # ----------------------------------------------------
    # 7. Run populate_database
    # ----------------------------------------------------
    populate_db.populate_database()

    # ----------------------------------------------------
    # 8. Assert output was inserted
    # ----------------------------------------------------
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row  # enable dict-style access
    row = conn.execute("SELECT * FROM outputs").fetchone()
    conn.close()

    assert row is not None
    assert row["patient_id"] == 1
    assert row["variant_number"] == 1
