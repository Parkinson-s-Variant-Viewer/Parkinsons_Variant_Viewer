# Parkinsons Variant Viewer

[![codecov](https://codecov.io/gh/Parkinson-s-Variant-Viewer/Parkinsons_Variant_Viewer/branch/main/graph/badge.svg)](https://codecov.io/gh/Parkinson-s-Variant-Viewer/Parkinsons_Variant_Viewer)

<img src="docs/images/PVV_logo.png" alt="PVV Logo" width="500">

## 📖 About

---

**Parkinsons Variant Viewer** is a web-based application designed to help Clinical Scientists analyze and annotate genetic variants associated with Parkinson's disease. The tool integrates data from multiple sources to provide comprehensive variant information for users.

Parkinson's disease is a progressive neurodegenerative disorder affecting movement, and genetic factors play a significant role in both familial and sporadic cases. Understanding the clinical significance of potentially pathogenic variants is crucial for accurate diagnosis, prognosis, potential therapeutic interventions and future research.

This tool was developed by second year STP students at the University of Manchester as part of the Software Development module.

**External Resources:**

- [**ClinVar**](https://www.ncbi.nlm.nih.gov/clinvar/) - NCBI's public archive of variant interpretations and clinical significance
- [**HGNC**](https://www.genenames.org/) - HUGO Gene Nomenclature Committee's standardized gene naming database
- [**OMIM**](https://www.omim.org/) - Online Mendelian Inheritance in Man catalog of human genes and genetic disorders

### ✨ Key Features

---

-  **VCF File Processing**: Load and parse VCF files containing genetic variant data
-  **ClinVar Integration**: Automatically fetch clinical significance, review status, and associated conditions from ClinVar
-  **HGNC Gene Nomenclature**: Retrieve standardized gene symbols and HGNC IDs
-  **Interactive Web Interface**: Search, filter, and explore variants through an intuitive table view
-  **Database Storage**: SQLite database for efficient variant data management
-  **Detailed Annotations**: View chromosome position, reference/alternate alleles, HGVS nomenclature, transcript information, and more

### 🎯 Use Cases

---

This tool is designed for researchers and clinicians studying Parkinson's disease, 
It aims to enable them to:
-  Quickly assess the clinical significance of variants in Parkinson's-associated genes
-  Compare variants across multiple patients
-  Access direct links to external databases (ClinVar, OMIM, HGNC)
-  Generate annotated variant reports

## 🚀 Installation

---

**Step 1: Clone the repository**
```bash
git clone git@github.com:patricklahert/Parkinsons_Variant_Viewer.git
```

**Step 2: Create the conda environment**
```bash
conda env create -f environment.yml 
conda activate pvv_conda
```

**Step 3: Install requirements**
```bash
pip install -r requirements.txt
```

**Step 4: Install Parkinsons Variant Viewer**
```bash
python -m pip install -e . 
```

For detailed installation instructions, see `Installation_manual.md`

## 📚 User Guide

---

See User_manual.md

## 👥 Authors

---

- **Ruqayyah Peerbhai**
- **Rebekah Embers**
- **Patrick Lahert** 

## 📄 License

---

This project is licensed under the MIT License:

```
MIT License

Copyright (c) 2025 Parkinsons Variant Viewer Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<img src="https://github.com/i3hsInnovation/resources/blob/master/images/UoM_logo.jpg?raw=true" width="10%" align="left"/>
