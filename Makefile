# Makefile for Parkinsons Variant Viewer

IMAGE = parkinsons-viewer
DB_DIR = parkinsons-data/instance
VCF_DIR = data/input

.PHONY: build init reset load annotate web

# Build the Docker image
build:
	docker build -t $(IMAGE) .

# Initialise the database (safe: will refuse if DB already exists)
init:
	docker run --rm \
	  -v $(PWD)/$(DB_DIR):/app/instance \
	  $(IMAGE) \
	  init-db

# Reset the database (destructive: wipes and recreates schema)
reset:
	docker run --rm \
	  -v $(PWD)/$(DB_DIR):/app/instance \
	  $(IMAGE) \
	  reset-db

# Load VCFs from data/input into the DB
load:
	docker run --rm \
	  -v $(PWD)/$(DB_DIR):/app/instance \
	  -v $(PWD)/$(VCF_DIR):/app/data/input \
	  $(IMAGE) \
	  load-vcfs

# Run the annotation pipeline (VariantValidator + ClinVar)
annotate:
	docker run --rm \
	  -v $(PWD)/$(DB_DIR):/app/instance \
	  $(IMAGE) \
	  annotate

# Run the web app on http://localhost:5000
web:
	docker run \
	  -p 5000:5000 \
	  -v $(PWD)/$(DB_DIR):/app/instance \
	  $(IMAGE) \
	  web
