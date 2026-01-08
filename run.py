"""
Command-line entry point for the Parkinson's Variant Viewer application.

This script provides commands for running the web application, initialising
and resetting the database, loading VCF files, and running the annotation
pipeline.
"""

import os
import sys

from parkinsons_variant_viewer.web import create_app
from parkinsons_variant_viewer.web.db import init_db, get_db_path
from parkinsons_variant_viewer.web.loaders.vcf_loader import load_vcf_into_db
from parkinsons_variant_viewer.populate_db import populate_database

def main():
    """Parse command-line arguments and dispatch application commands."""
    if len(sys.argv) < 2:
        print("Usage: python run.py [web | init-db | reset-db | load-vcfs | annotate]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    # Create Flask app (many commands need the config + app context)
    app = create_app()

    if cmd == "web":
        app.run(host="0.0.0.0", port=5000)

    elif cmd == "init-db":
        # Safe init: only create if database does not already exist. 
        with app.app_context():
            db_path = get_db_path()

        if os.path.exists(db_path):
            print(f"Database already exists at: {db_path}")
            print("If you want to wipe and recreate it, run:")
            print("python run.py reset-db")
            sys.exit(1)
        
        with app.app_context():
            init_db()
        print(f"Database initialised at {db_path}.")

    elif cmd == "reset-db":
        # Always recreate database even if one exists already
        with app.app_context():
            db_path = get_db_path()

        print(f"WARNING: This will erase all data in {db_path}")

        if sys.stdin.isatty():
            confirm = input("Type 'yes' to continue:")
            if confirm.lower() != "yes":
                print("Aborting reset.")
                sys.exit(1)
        
        with app.app_context():
            init_db()
            print(f"Database reset at {db_path}.")

    elif cmd == "load-vcfs":
        vcf_dir = "data/input"

        if not os.path.isdir(vcf_dir):
            print(f"VCF directory '{vcf_dir}' does not exist.")
            sys.exit(1)

        with app.app_context():
            db_path = get_db_path()

        print(f"Using database: {db_path}")
        print(f"Loading VCFs from: {vcf_dir}")

        for fn in os.listdir(vcf_dir):
            if fn.lower().endswith(".vcf"):
                path = os.path.join(vcf_dir, fn)
                print(f"Loading {path}")
                load_vcf_into_db(path, db_path)

        print("All VCFs loaded into database.")

    elif cmd == "annotate":
        print("Running annotation pipeline... (this may take time)")
        populate_database()
        print("Annotation complete.")

    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python run.py [web | init-db | load-vcfs | annotate]")


if __name__ == "__main__": # pragma: no cover
    main()
