# Parkinsons_Variant_Viewer
STP Software module project - Designing a platform to view variants for a Parkinson's study

Installation guide 

Step 1: clone the repository 
```
git clone git@github.com:patricklahert/Parkinsons_Variant_Viewer.git
```

Step 2: create the conda environment
```
conda env create -f environment.yml 
conda activate pvv_conda
```

Step 3: Install requirements
```
pip install -r requirements.txt
```

Step 4: Install Parkinsons Variant Viewer
```
python -m pip install -e . 
```
