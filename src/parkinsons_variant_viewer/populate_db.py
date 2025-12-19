import sqlite3
import time
from parkinsons_variant_viewer.hgvs_variant import HGVSVariant
from parkinsons_variant_viewer.clinvar_api import fetch_clinvar_variant, get_variant_info
from parkinsons_variant_viewer.web import create_app
from parkinsons_variant_viewer.web.db import get_db_path
from parkinsons_variant_viewer.utils.logger import logger


def populate_database():
    """
    Populate the outputs table for all variants in the inputs table.
    Intended to be called programmatically (e.g. from run.py).
    """
    app = create_app()

    with app.app_context():
        db_path = get_db_path()
        logger.info(f"Using database: {db_path}")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Fetch all variants from the inputs table
        cur.execute("SELECT patient_id, variant_number, chrom, pos, ref, alt FROM inputs")
        variants = cur.fetchall()

        logger.info(f"Found {len(variants)} variants to process.")

        for v in variants:
            patient_id = v["patient_id"]
            variant_number = v["variant_number"]
            chrom = v["chrom"]
            pos = v["pos"]
            ref = v["ref"]
            alt = v["alt"]

            logger.info(f"Processing Patient {patient_id}, Variant {variant_number}")

            try:
                # Step 1: Get HGVS notation
                hgvs_variant = HGVSVariant(chrom, pos, ref, alt)
                hgvs_data = hgvs_variant.fetch()
                hgvs_genomic = hgvs_data.get("hgvs_genomic") if hgvs_data else None

                if not hgvs_genomic:
                    logger.warning(f"No HGVS found for {chrom}:{pos} {ref}>{alt}")
                    continue

                # Step 2: Query ClinVar for details
                clinvar_raw = fetch_clinvar_variant(hgvs_genomic)
                variant_info = get_variant_info(clinvar_raw)

                # Step 3: Insert results into outputs table
                cur.execute("""
                    INSERT OR REPLACE INTO outputs (
                        patient_id, variant_number, 
                        hgvs, clinvar_id, clinical_significance,
                        star_rating, review_status, conditions_assoc,
                        transcript, ref_seq_id, hgnc_id, omim_id,
                        gene_symbol, g_change, c_change, p_change
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    patient_id, variant_number,
                    variant_info.hgvs,
                    variant_info.clinvar_id,
                    variant_info.clinical_significance,
                    variant_info.star_rating,
                    variant_info.review_status,
                    variant_info.conditions_assoc,
                    variant_info.transcript,
                    variant_info.ref_seq_id,
                    variant_info.hgnc_id,
                    variant_info.omim_id,
                    variant_info.gene_symbol,
                    variant_info.g_change,
                    variant_info.c_change,
                    variant_info.p_change
                ))
                conn.commit()
                logger.info(f"Added ClinVar data for Patient {patient_id}, Variant {variant_number}")

            except Exception as e:
                logger.error(f"Error processing Patient {patient_id}, Variant {variant_number}: {e}")

            # Respect API rate limits
            time.sleep(0.5)

        conn.close()
        logger.info("🎉 Database population complete.")


if __name__ == "__main__":
    populate_database()