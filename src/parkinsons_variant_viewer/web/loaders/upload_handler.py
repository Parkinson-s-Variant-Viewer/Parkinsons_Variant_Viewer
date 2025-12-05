import os
import csv
import sqlite3  #*** added for catching IntegrityError
from ..db import get_db
from parkinsons_variant_viewer.hgvs_variant import HGVSVariant
from parkinsons_variant_viewer.clinvar_api import fetch_clinvar_variant, get_variant_info
from parkinsons_variant_viewer.utils.logger import logger
import time


def handle_uploaded_file(file_path):
    """
    Handle VCF or CSV upload, parse variants, insert into DB,
    fetch HGVS IDs, call ClinVar API, and populate outputs table.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    db = get_db()
    variants = []

    # --- Parse uploaded file with exception handling ---
    try:  #*** added
        if ext == ".vcf":
            # Extract patient_id from filename like Patient99.vcf
            stem = os.path.basename(file_path).split(".")[0]
            try:
                patient_id = int(stem.replace("Patient", "").replace("patient", ""))
            except ValueError:
                raise ValueError("Cannot determine patient_id from VCF filename")

            with open(file_path) as f:
                variant_number = 1
                for line in f:
                    if line.startswith("#"):
                        continue
                    parts = line.strip().split("\t")
                    if len(parts) < 5:
                        raise ValueError(f"Invalid VCF line format: {line}")  #***
                    chrom, pos, vid, ref, alt = parts[:5]
                    variants.append({
                        "chrom": chrom,
                        "pos": int(pos),
                        "ref": ref,
                        "alt": alt,
                        "variant_number": variant_number,
                        "patient_id": patient_id,
                        "id": vid
                    })
                    variant_number += 1

        elif ext == ".csv":
            with open(file_path, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not all(k in row for k in ["chrom", "pos", "ref", "alt", "patient_id", "variant_number"]):
                        raise ValueError(f"CSV missing required columns: {row}")  #***
                    variants.append({
                        "chrom": row["chrom"],
                        "pos": int(row["pos"]),
                        "ref": row["ref"],
                        "alt": row["alt"],
                        "patient_id": int(row["patient_id"]),
                        "variant_number": int(row["variant_number"]),
                        "id": row.get("id")
                    })
        else:
            raise ValueError("Unsupported file type")  #*** catches wrong extension

    except Exception as e:  #*** catch parsing/file type errors
        logger.error(f"Error parsing uploaded file: {e}")
        return  # stop further processing

    # --- Insert into inputs table with duplicate handling ---
    for var in variants:
        try:  #*** added
            db.execute(
                """
                INSERT INTO inputs (patient_id, variant_number, chrom, pos, id, ref, alt)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    var["patient_id"],
                    var["variant_number"],
                    var["chrom"],
                    var["pos"],
                    var.get("id"),
                    var["ref"],
                    var["alt"],
                ),
            )
        except sqlite3.IntegrityError as e:  #*** catch duplicates
            logger.warning(f"Duplicate entry for Patient {var['patient_id']}, Variant {var['variant_number']}: {e}")
            continue  # skip duplicate

    db.commit()
    logger.info(f"Inserted {len(variants)} variants into inputs table")

    # --- Fetch HGVS IDs and ClinVar data, populate outputs ---
    for var in variants:
        try:
            # 1. HGVS
            hgvs_obj = HGVSVariant(var["chrom"], var["pos"], var["ref"], var["alt"])
            hgvs_id = hgvs_obj.get_hgvs()
            if not hgvs_id:
                logger.warning(f"Could not fetch HGVS for variant {var}")
                continue

            # 2. ClinVar
            clinvar_raw = fetch_clinvar_variant(hgvs_id)
            variant_info = get_variant_info(clinvar_raw)

            # 3. Insert into outputs table
            db.execute("""
                INSERT INTO outputs (
                    patient_id, variant_number, hgvs, clinvar_id,
                    clinical_significance, star_rating, review_status,
                    conditions_assoc, transcript, ref_seq_id, hgnc_id,
                    omim_id, gene_symbol, g_change, c_change, p_change
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                var["patient_id"],
                var["variant_number"],
                variant_info.hgvs,
                variant_info.clinvar_id,
                variant_info.clinical_significance,
                variant_info.star_rating,
                variant_info.review_status,
                getattr(variant_info, "conditions_assoc", None),
                getattr(variant_info, "transcript", None),
                getattr(variant_info, "ref_seq_id", None),
                getattr(variant_info, "hgnc_id", None),
                getattr(variant_info, "omim_id", None),
                getattr(variant_info, "gene_symbol", None),
                getattr(variant_info, "g_change", None),
                getattr(variant_info, "c_change", None),
                getattr(variant_info, "p_change", None)
            ))
            db.commit()
            logger.info(f"Added ClinVar data for Patient {var['patient_id']}, Variant {var['variant_number']}")

            # 4. Respect API rate limits
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"Error processing Patient {var['patient_id']}, Variant {var['variant_number']}: {e}", exc_info=True)
