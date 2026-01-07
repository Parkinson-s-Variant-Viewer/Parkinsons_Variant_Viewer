"""
Flask routes for the Parkinson's Variant Viewer web app.

Provides endpoints for viewing variants, adding new variants, and
uploading variant files. Handles rendering templates and database
interactions.
"""

import os

from flask import Blueprint, render_template, request, redirect, url_for
from .db import get_db

from parkinsons_variant_viewer.utils.logger import logger

bp = Blueprint("web", __name__)


@bp.route("/")
def index():
    """
    Display the home page with a list of all variants.
    """
    logger.debug("Index page accessed")
    db = get_db()

    rows = db.execute("""
        SELECT 
            i.patient_id,
            i.variant_number,
            i.chrom,
            i.pos,
            i.id,
            i.ref,
            i.alt,
            o.hgvs,
            o.clinvar_id,
            o.clinical_significance,
            o.star_rating,
            o.review_status,
            o.conditions_assoc,
            o.transcript,
            o.ref_seq_id,
            o.hgnc_id,
            o.omim_id,
            o.gene_symbol,          
            o.g_change,
            o.c_change,
            o.p_change
        FROM inputs AS i
        LEFT JOIN outputs AS o
        ON i.patient_id = o.patient_id
           AND i.variant_number = o.variant_number
        ORDER BY i.patient_id, i.variant_number
    """).fetchall()

    logger.info(f"Displaying {len(rows)} variants on index page")
    return render_template("variants.html", variants=rows)


@bp.route("/add", methods=["GET", "POST"])
def add_variant():
    """
    Add a new input variant manually via a form.
    """
    db = get_db()

    if request.method == "POST":
        logger.info("Received POST request to add new variant")
        patient_id = request.form["patient_id"]
        variant_number = request.form["variant_number"]
        chrom = request.form["chrom"]
        pos = request.form["pos"]
        vid = request.form["id"]
        ref = request.form["ref"]
        alt = request.form["alt"]

        db.execute(
            """
            INSERT INTO inputs 
            (patient_id, variant_number, chrom, pos, id, ref, alt)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (patient_id, variant_number, chrom, pos, vid, ref, alt),
        )

        db.commit()
        logger.info(
            f"Added variant: Patient {patient_id}, Variant {variant_number}, "
            f"{chrom}:{pos} {ref}>{alt}"
        )
        return redirect(url_for("web.index"))

    logger.debug("Add variant form accessed (GET)")
    return render_template("add_variant.html")


@bp.route("/inputs")
def view_inputs():
    """
    Display a table of manually added input variants.
    """
    logger.debug("Inputs page accessed")
    db = get_db()

    rows = db.execute("""
        SELECT patient_id, variant_number, chrom, pos, id, ref, alt
        FROM inputs
        ORDER BY patient_id, variant_number
    """).fetchall()

    logger.info(f"Displaying {len(rows)} input variants")
    return render_template("inputs.html", inputs=rows)


@bp.route("/upload", methods=["POST"])
def upload_data():
    """
    Handle file uploads via AJAX and process them.
    """
    logger.info("File upload request received")

    file = request.files.get("file")
    if not file:
        logger.warning("Upload failed: No file provided in request")
        return "No file uploaded", 400

    filename = file.filename
    logger.info(f"Processing uploaded file: {filename}")

    try:
        # create uploads directory
        save_dir = "data/uploads"
        os.makedirs(save_dir, exist_ok=True)

        save_path = os.path.join(save_dir, filename)
        file.save(save_path)

        logger.info(f"File saved to: {save_path}")

        # Call handler to insert into DB and fetch ClinVar
        from .loaders.upload_handler import handle_uploaded_file
        handle_uploaded_file(save_path)

        logger.info(f"Successfully processed file: {filename}")
        return "OK", 200

    except Exception as e:
        logger.error(
            f"Error processing uploaded file {filename}: {e}",
            exc_info=True
        )
        return f"Error processing file: {str(e)}", 500
