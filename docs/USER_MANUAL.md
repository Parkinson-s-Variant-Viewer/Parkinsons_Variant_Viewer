# Parkinsons Variant Viewer – User Manual

<img src="docs/images/PVV_logo.png" alt="PVV Logo" width="500">

---

## 📖 Introduction

Parkinsons Variant Viewer (PVV) is a web-based application designed to assist clinical scientists and researchers in analysing genetic variants associated with Parkinson’s disease.  

It allows users to load patient VCF and CSV files, annotate variants using external databases, and explore results through a web interface.  

PVV can be used via a **local installation** on your machine or using a **Docker container**. 

---

## 👥 Intended Users

- Clinical scientists  
- Researchers  

> Note: Basic familiarity with command line tools is recommended.

---

## 💻 System Requirements

- Operating System: Linux, macOS, or Windows  
- Python 3.10+  
- Conda (for local installation) **or** Docker (for containerised deployment)  
- Internet connection (for ClinVar and HGNC annotation)

---

## 🔄 Application Overview

The PVV workflow involves:

1. Initialising the database  
2. Loading patient VCF files  
3. Annotating variants using external APIs  
4. Viewing and filtering results through a web interface

---

## 📁 1. Input Data Folder Setup (Important)

-  Patient VCF files must be placed in the `data/input/`directory. 
- Files must follow the naming convention: `Patient[number].vcf` (e.g. `Patient1.vcf`)

> **Note:** Only **one VCF file** is initially required  to configure the database.  
> Once the database and web interface are set up, additional patient VCF or CSV files can be uploaded directly through the **Upload** feature in the web interface.
---
## 🗄️ 2. Database Initialisation

### Local 

```bash
python run.py init-db
```

### Docker 

```bash
make init
```


## 📂 3. Loading VCF Files

> 🚨  Note: a minimum of 1 VCF file needs to be present in the `data/input/`directory. 

### Local
```bash
python run.py load-vcfs
```
### Docker  
```bash
make load
```
## 🧩 4. Annotating Variants 

### Local  
```bash
python run.py annotate
```

### Docker 
```bash
make annotate
```

## 🌐 5. Launching the Web Interface

### Local 
```bash
python run.py web
```
### Docker 
```bash
make web
```

## ⚡ 6. Common Workflow Example
### Local 
```bash
python run.py init-db   # Initialise database
python run.py load-vcfs # Load VCF files
python run.py annotate  # Annotate variants
python run.py web       # Run web interface
```
### Docker 
```bash
make build 
make init                # Initialise database
make load                # Load VCF files
make annotate            # Annotate variants
make web                 # Run web interface
```

## 📚 7. Support & Documentation

- Installation Guide: INSTALLATION.md
- User Guide: USER_MANUAL.md
- For technical issues or bug reports, please contact the development team.
