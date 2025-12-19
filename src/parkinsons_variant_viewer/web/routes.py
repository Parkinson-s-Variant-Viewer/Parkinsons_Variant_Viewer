from flask import Blueprint, render_template, request, redirect, url_for
from .db import get_db
from parkinsons_variant_viewer.utils.logger import logger

bp = Blueprint("web", __name__)


# Home page: list all variants (input + output if present)
@bp.route("/")
def index():  # pragma: no cover
    logger.debug("Index page accessed")  # pragma: no cover
    db = get_db()

    # Join the inputs and outputs tables on the composite key
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
    
    logger.info(f"Displaying {len(rows)} variants on index page")  # pragma: no cover
    return render_template("variants.html", variants=rows)


# Add a new *input* variant manually
@bp.route("/add", methods=["GET", "POST"])
def add_variant():  # pragma: no cover
    db = get_db()

    if request.method == "POST":
        logger.info("Received POST request to add new variant")  # pragma: no cover
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
        logger.info(f"Added variant: Patient {patient_id}, Variant {variant_number}, {chrom}:{pos} {ref}>{alt}")  # pragma: no cover
        return redirect(url_for("web.index"))
    
    logger.debug("Add variant form accessed (GET)")  # pragma: no cover
    return render_template("add_variant.html")


# Route to view the table of input data
@bp.route("/inputs")
def view_inputs():  # pragma: no cover
    logger.debug("Inputs page accessed")  # pragma: no cover
    db = get_db()

    rows = db.execute("""
        SELECT patient_id, variant_number, chrom, pos, id, ref, alt
        FROM inputs
        ORDER BY patient_id, variant_number
    """).fetchall()
    
    logger.info(f"Displaying {len(rows)} input variants")  # pragma: no cover
    return render_template("inputs.html", inputs=rows)


# Route to handle AJAX file upload from main page
@bp.route("/upload", methods=["POST"])
def upload_data():  # pragma: no cover
    logger.info("File upload request received")  # pragma: no cover
    
    file = request.files.get("file")
    if not file:
        logger.warning("Upload failed: No file provided in request")  # pragma: no cover
        return "No file uploaded", 400

    filename = file.filename
    logger.info(f"Processing uploaded file: {filename}")  # pragma: no cover
    
    try:
        save_path = f"data/uploads/{filename}"  # ensure this folder exists
        file.save(save_path)
        logger.info(f"File saved to: {save_path}")  # pragma: no cover

        # Call handler to insert into DB and fetch ClinVar
        from .loaders.upload_handler import handle_uploaded_file
        handle_uploaded_file(save_path)
        
        logger.info(f"Successfully processed file: {filename}")  # pragma: no cover
        return "OK", 200
    except Exception as e:
        logger.error(f"Error processing uploaded file {filename}: {e}", exc_info=True)  # pragma: no cover
        return f"Error processing file: {str(e)}", 500
