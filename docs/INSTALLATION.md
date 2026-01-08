# Installation Guide

<img src="images/PVV_logo.png" alt="PVV Logo" width="500">

---

This guide outlines the installation process for both local and Dockerised installation of the Parkinsons Variant Viewer software.

## Local Installation Guide

#### Step 1: Clone the repository

```bash
git clone https://github.com/Parkinson-s-Variant-Viewer/Parkinsons_Variant_Viewer.git
```
#### Step 2: Change directory
```bash
cd Parkinsons_Variant_Viewer
```
#### Step 3: Create the conda environment

```bash
conda env create -f environment.yml
conda activate pvv_conda
```

#### Step 4: Install requirements

```bash
pip install -r requirements.txt
```

#### Step 5: Install Parkinsons Variant Viewer

```bash
python -m pip install -e .
```

---

## Docker Installation Guide

This project uses `make` commands to simplify building and running the Parkinson's Variant Viewer application.

All functionality, including building the Docker image, initiating and resetting the database, and running the web server, is wrapped in the Makefile.

#### Requirements

- Docker (latest version recommended)
- For Windows: Install GNU Make. [Download Here](https://gnuwin32.sourceforge.net/packages/make.htm) and install by following [these instructions.](https://leangaurav.medium.com/how-to-setup-install-gnu-make-on-windows-324480f1da69)

---
#### Clone the repository

Follow the same steps as the local installation guide to clone the repository and change directory. 

```bash
git clone https://github.com/Parkinson-s-Variant-Viewer/Parkinsons_Variant_Viewer.git
cd Parkinsons_Variant_Viewer
```

#### Build the Docker image

```bash
make build
```

This command:

- Builds the Docker image using the project's Dockerfile
- Tags the image as parkinsons-viewer

#### Initialise the database

```bash
make init
```

This command runs the `init-db` command to create the SQLite database inside the `instance/` directory.

Run this command when:

- You're setting up the app for the first time
- You've reset the environment
- You need a fresh database

This command will trigger a warning if a database already exists inside `instance/`, and ask you to run `make reset` if you need a fresh database.

#### Reset the database

```bash
make reset
```

This command completely **deletes and removes** the database located in the `instance/` directory. Use this only when needing a totally clean slate for the database.

#### Load in VCF files to the database

```bash
make load
```

**Important**: Before running this command, make sure to place your .vcf files in the filepath: Parkinsons_Variant_Viewer/data/input. `make load` looks in this specific location for the patient VCFs. Ensure that the filenames are formatted as "Patient[number].vcf", where [number] is a numerical value unique to the patient.

This command loads the VCFs into the database initialised with `make init`.

#### Annotate the variants in the database

```bash
make annotate
```

This command runs `run.py annotate` inside the Docker container to load variant information into the database using APIs.

#### Run the web application

```bash
make web
```

This command starts the Flask web server inside Docker and binds the app to `localhost:5000`

The local `instance/` directory is mounted for persistence.

Note: If port 5000 is already in use, close the existing process or adjust the port in the Makefile.

---

## Common Workflow

To start up the Parkinsons Variant Viewer app and database with Docker, run:

```bash
make build
make init
# Place the properly named VCFs in the Parkinsons_Variant_Viewer/data/input folder
make load
make annotate
make web
```

## Support & Documentation

- Installation Guide: see [Installation manual](INSTALLATION.md).
- User Guide: [User Manual](USER_MANUAL.md)
- For technical issues or bug reports, please contact the development team.
