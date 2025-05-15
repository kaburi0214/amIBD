# Versions
Current version: 1.0.0 Date: May 12, 2025

# Features
amIBD provides a guided web-based interface that leads users sequentially through the complete ancient-modern IBD analysis workflow: (1) Upload modern individual file; (2) Update ancient individual files; (3) Run IBD calculating, and obtain the IBD analysis report at the final step: (4) Result. amIBD supports various input file formats, allows customization of file and computational resources, offers real-time operational feedback, and enables streamlined result previewing and downloading.

# Requirements
ancibd==0.7\
atlas=2.0.0\
bcftools=1.21\
glimpse-bio=2.0.1\
pandas>=2.2.3\
plink=1.90b7.7\
samtools=1.21\
seqkit=2.10.0\
snakemake=7.32.4\
streamlit==1.44.0

If have any problems with requirements, please check the file *ibd_env.yml*

# Datasets
ancient samples: user-uploaded BAM files, e.g. https://www.ebi.ac.uk/ena/browser/view/PRJEB11450 \
modern samples: user-upload 23andMe files\
data required by ancIBD pipeline included:\
hg19 reference genome FASTA file for calling genotypes (https://hgdownload.soe.ucsc.edu/goldenPath/hg19/bigZips/); genetic maps (https://github.com/odelaneau/GLIMPSE/tree/master/maps/genetic_maps.b37) and phased haplotypes from the 1000 Genomes dataset (https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/) for imputing and phasing; marker files (https://www.dropbox.com/scl/fo/x13ic2c5miangjd8r1zbe/ALF9R2tyXOI9xYaQ2wT5rcU/data/filters?rlkey=cx40wvvqxdzbkaixfpqmqbvb4&e=2&subfolder_nav_tracking=1&dl=0) and map file (https://www.dropbox.com/scl/fo/x13ic2c5miangjd8r1zbe/AO7UmIrpao6zBnm8gEvrAI4/data/map?rlkey=cx40wvvqxdzbkaixfpqmqbvb4&e=2&subfolder_nav_tracking=1&dl=0) for IBD detection.

# Quickstart
## 1. creat a working directory, move to that directory and clone the codes:
```
   git clone git@github.com:kaburi0214/amIBD.git
```
## 2. prepare all the required datasets at the correct folders
## 3. set the requirements:\
   for docker users:
   ```
   docker build -t amibd .
   docker run -p 8501:8501 amibd
   ```
   click the URL (and change 0.0.0.0 to localhost)\
   (p.s. users can also pull the image from dockerhub instead of building image:)
   docker pull tongrui214/ancibd:latest)\
   for conda users:
   ```
   conda env create -f ibd_env.yml
   conda activate ancibd_py310
   streamlit run app.py
   ```
   click the Local URL or Network URL
      
# Step-by-step usage
## 1. Upload modern individual file
User can choose either "valid 23andMe input file with details: rsid, chromosome, position and genotype" or "Original 23andMe file needs processing";\
Then just upload the corresponding 23andMe file
## 2. Update ancient individual files
User should first tick the box ("I need to change the Ancient Individuals file") if there's a need to update ancient individual files\
For add files:
- edit the anc_samples.tsv by adding the sample names and sample paths for expected upload files, save the table;
- upload the BAM files and choose correct sample name for the file;

For delete files:
- delete files from the list of uploaded bam files;
- modify the anc_samples.tsv and save the change;
## 3. Run IBD calculating
User can adjust the slider to set the suitable core number for running the workflow;
- click "dry run (for previewing)" to preview the workflow;
- click "run" to execute the actual IBD calculating workflow
## 4. Result
Preview and download the result\
result shows the detected IBD segments between modern individual and ancient populations, organized by genomic regions (chromosome, start base pair position, end base pair position) and sorted by the highest total shared IBD length (>8 cM)
