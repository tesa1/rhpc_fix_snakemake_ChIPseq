# ChIP-seq analysis pipeline based on snakemake


This is an snakemake-based Peak calling pipeline used in Zwart lab at the Netherlands Cancer Institute.
The pipeline obtains ChIP-seq data from diverse sources (remote/local path or GEO) and process them accordingly to produce peak lists in bed format and coverage profiles in tdf format.

Roughly, the pipeline takes the following steps to produce the outcome:

- Downloading raw data (either bam/fastq files) from the specified locations (local, remote, or GEO) in DataList.csv
- Alignment with bwa-mem (in case of fastq files)
- Marking duplicate reads with picard
- Removing low-quality reads (retain reads with mapping quality > 20)
- Peak calling with MACS1.4/MACS2/DFilter (support more than one peak callers)
- Taking intersection between the peaks

Note that PeakPairs.csv is used to specify ChIP-seq vs input pairs, and config.yaml is used for specifiying optional parameters in softwares.

## Installation ##


The pipeline is preliminary used in linux environment with conda/singularity available. Singularity is used  only for DFilter (one of two peak callers used) within the pipeline. Currently, the pipeline is tested with conda version 4.5.4 and singularity version 2.5.1.

For downloading repository & creating evnironment:

```bash
git clone https://github.com/anoyaro84/snakemake_ChIPseq
cd snakemake_ChIPseq
conda env create --file env/snakemake.yaml

# install phantompeak tools
git submodule init
git submodule update
```

The most of softwares used in the pipeline is installed by conda or excuted in wrapper.
Only exception is the phantompeak, the software used for estimating the fragment length that can be used by MACS2.
Phantompeak tools is included as a submodule, for which you can install with the last two commands.

We recommend to run the pipeline from a different location than pipeline path, like below:

```bash
snakemake -s PATH_TO_PIPELINE/Snakefile --use-conda --use-singularity --cores=24
```

With --use-conda option, the pipeline will create environments to run rules based on .yaml files in env/.
The --use-singulairty option applies only to DFilter peak caller. The singularity container holds a virtual environment of Ubuntu with DFilter installed.


Note that the pipeline assumes that there is the following three files available at the location where the pipeline is executed:
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



