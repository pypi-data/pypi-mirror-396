# epi2hit

`epi2hit` is a Python package for **integrative methylation / expression analysis** and detection of **epigenetically deregulated CpGs (eCpGs)**

---

## Features
  
- Filtering of probes to **open chromatin** using ATAC-seq peaks  
- Mapping probes to genes  
- Preliminary QC / filtering of probes  
- Annotation with chromatin state (Pomerantz / chromHMM states)  
- Correlation-based probe selection and duplicate resolution  
- Annotation of probes with **3D chromatin loops**  
- Preparation of TCGA-like expression dictionaries  
- Linear regression between methylation and expression  
- Peak-based methylation categorisation and detection of eCpGs

All steps are available as individual functions, but they are designed to run in a simple end-to-end script or notebook.

---

## Installation

pip install epi2hit

