# run.py
import sys
import os

from src.parkinsons_variant_viewer.web import create_app
from src.parkinsons_variant_viewer.web.db import init_db, get_db_path
from src.parkinsons_variant_viewer.web.loaders.vcf_loader import load_vcf_into_db
from src.parkinsons_variant_viewer.populate_db import main as annotate_main


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py [web | init-db | load-vcfs | annotate]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    # Create Flask app (many commands need the config + app context)
    app = create_app()

    if cmd == "web":
        app.run(host="0.0.0.0", port=5000)

    elif cmd == "init-db":
        with app.app_context():
            init_db()
        print("Database initialised.")

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
        annotate_main()
        print("Annotation complete.")

    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python run.py [web | init-db | load-vcfs | annotate]")


if __name__ == "__main__":
    main()
