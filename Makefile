# Makefile for Parkinsons Variant Viewer (Windows + Linux safe)

IMAGE = parkinsons-viewer
DB_DIR = parkinsons-data/instance
VCF_DIR = data/input

# Convert Windows backslashes to forward slashes for Docker
HOST_DB = $(subst \,/,$(CURDIR)/$(DB_DIR))
HOST_VCF = $(subst \,/,$(CURDIR)/$(VCF_DIR))

.PHONY: build init reset load annotate web fresh

# Build the Docker image
build:
	docker build -t $(IMAGE) .

# Initialise the database (safe: refuses if DB exists)
init:
	docker run --rm \
	  -v $(HOST_DB):/app/instance \
	  $(IMAGE) \
	  init-db

# Reset the database (destructive)
reset:
	docker run --rm \
	  -v $(HOST_DB):/app/instance \
	  $(IMAGE) \
	  reset-db

# Load VCFs into the DB
load:
	docker run --rm \
	  -v $(HOST_DB):/app/instance \
	  -v $(HOST_VCF):/app/data/input \
	  $(IMAGE) \
	  load-vcfs

# Run annotation pipeline
annotate:
	docker run --rm \
	  -v $(HOST_DB):/app/instance \
	  $(IMAGE) \
	  annotate

# Run the web app
web:
	docker run \
	  -p 5000:5000 \
	  -v $(HOST_DB):/app/instance \
	  $(IMAGE) \
	  web

