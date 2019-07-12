# This is a fix for RHPC conda update and clean that destroyed all hardlinks for ChIP-seq analysis pipeline based on snakemake



This is a fix for the original snakemake-based Peak calling pipeline from Yongsoo Kim 
(https://github.com/anoyaro84/snakemake_ChIPseq) used in Zwart lab at the Netherlands Cancer Institute.



There have been minor changes to the pipeline, but the versions of major software such as MACS, MACS2, DFilter, samtools, bedtools, python, etc remain the same. The output of the fix pipeline has been compared and with previously analyzed data and there are no differences. The html document in this repository shows the results of that analysis.

##

The pipeline obtains ChIP-seq data from diverse sources (remote/local path or GEO) and process them accordingly to produce peak lists in bed format and coverage profiles in tdf format.

Roughly, the pipeline takes the following steps to produce the outcome:

- Downloading raw data (either bam/fastq files) from the specified locations (local, remote, or GEO) in DataList.csv
- Alignment with bwa-mem (in case of fastq files)
- Marking duplicate reads with picard
- Removing low-quality reads (retain reads with mapping quality > 20)
- Basic QC output (phantompeaktools and fastqc/multiqc)
- Peak calling with MACS1.4/MACS2/DFilter (supports more than one peak caller and is controlled by config.yaml file)
- Taking intersection between the peaks

Note that PeakPairs.csv is used to specify ChIP-seq vs input pairs, and config.yaml is used for specifiying optional parameters in softwares.

## Installation ##


The fix for the pipeline is preliminary used in linux environment with conda/singularity available. Singularity is used  only for DFilter (one of two peak callers used) within the pipeline. Currently, the pipeline is tested with *conda version 4.7.5* and singularity version 2.4.2-master.g91881f7 on July 9th, 2019. Note, if you are on harris, you will need to use conda version 4.7.5 in /opt/anaconda/bin/ and if you are on darwin you will need to use conda version 4.7.5 in /opt/anaconda3/bin/

For downloading repository & creating environment:

```bash
# Download enviroment for running pipeline somewhere into your ~/ directory.
git clone https://github.com/tesa1/rhpc_fix_snakemake_ChIPseq/
cd rhpc_fix_snakemake_ChIPseq

# install enviroment for running pipeline on ** harris **:
/opt/anaconda/bin/conda env create --file env/rhpc_fix_snakemake.yaml

# install enviroment for running pipeline on ** darwin **:
/opt/anaconda3/bin/conda env create --file env/rhpc_fix_snakemake.yaml

# Activate phantompeakqualtools and go back to original directory
cd Softwares/phantompeakqualtools
chmod 777 run_spp.R
cd ../..

# Separately download and install bioepic package into the conda environment just created. 
# This package could not be installed after the conda update/clean with pip from within the conda enviroment it must be installed explicitly
# Replace YOUR_USER_NAME with your server name (eg. t.severson)
pip install -t /home/YOUR_USER_NAME/.conda/envs/rhpc_fix_SnakeMake/lib/python3.6/site-packages/ bioepic==0.2.5
# You might get this warning when you run the pip command below: 
# You are using pip version 9.0.1, however version 19.1.1 is available. You should consider upgrading pip via the 'pip install --upgrade pip' command. 
# DO NOT UPGRADE PIP


# Activate your conda environment
source activate rhpc_fix_SnakeMake
```


Most software used in the pipeline is installed by conda or excuted in wrapper.
Only exceptions are phantompeak, the software used for estimating the fragment length that can be used by MACS2, and the bioepic python package.
Both are included as separate software.


For running the pipeline on your bam files, we recommend to run the pipeline from a different location than pipeline path, like below:

```bash
snakemake -s PATH_TO_PIPELINE/Snakefile --use-singularity --use-conda --cores=20 -p --singularity-args="-B /DATA:/DATA" &> run.log
```

With --use-conda option, the pipeline will create environments to run rules based on .yaml files in env/.
The --use-singulairty option applies only to DFilter peak caller. The singularity container which holds a virtual environment of Ubuntu with DFilter was no longer available due to the singularity hub site being down. The image has been saved and put into a shared enviroment and is now called explicitly in the src/peakcalling.smk file. The --singularity-args allows singularity image to be in the correct enviroment (/DATA/YOUR_USER_NAME).


Note that the pipeline assumes that there is the following three files available at the location where the pipeline is executed. A set of example files is included with the repository:
- config.yaml
- DataList.csv
- PeakPairs.csv

See below for more details on how to prepare these input files.

## Preparing Input files ##

For DatList.csv, it is expected to have the following structure (in csv format):


| ID | Source | Path | Format |
| ------------- | ------------- | ------------- | ------------- |
| Identifier of each sequencing data | Source of the files, can either be remote (forge), local, or GEO | (local/remote) path to the file. (ignored if Source is GEO) | Either fastq or bam (ignored if Source is GEO) |


The pipeline will take either fastq/bam files from GEO, remote/local locations based on the table above.

For GEO, GSM ID is required for ID, which will be used as an quiry to GEO database. For remote/local files, ID should be a part of the file name. The pipeline greps bam/fastq files with ID on the specified path. The pipeline grabs bam/fastq files with ID on the specified path. If there is none or multiple files with the specified ID on the path, it will give an error.


For PeakPairs.csv, signal and input pairs need to be specified in the following format (in csv):

| Signal | Input |
| ------------- | ------------- |
| ID of ChIP-seq data | ID of Input data |


Note that IDs used in the PeakPairs.csv should be available in ID column of DataList.csv.


For config.yaml, you can copy it from this repository and modify the parameters based on your need.



