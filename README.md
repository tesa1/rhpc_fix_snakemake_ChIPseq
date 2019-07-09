# This is a fix for an RHPC patch Monday (July 1, 2019) which destroyed all pipeline environmental hardlink for ChIP-seq analysis pipeline based on snakemake


This fix contains the same snakemake-based Peak calling pipeline as previously but with  some minor changes to download and run the enviroment in conda v4.7.5. Versions of major softwares such as MACS2, MACS, DFilter, samtools, bedtools, etc. remain the same. 
##
Taken from Yongsoo Kim, (ttps://github.com/anoyaro84): This is an snakemake-based Peak calling pipeline used in Zwart lab at the Netherlands Cancer Institute.
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


The pipeline is preliminary used in linux environment with conda/singularity available. Singularity is used  only for DFilter (one of two peak callers used) within the pipeline. Currently, the pipeline is tested with conda version 4.7.5 and singularity version 2.4.2-master.g91881f7.

For downloading repository & creating evnironment:

```bash
git clone https://github.com/tesa1/rhpc_fix_snakemake_ChIPseq
cd rhpc_fix_snakemake_ChIPseq
conda env create --file env/rhpc_fix_snakemake.yaml

# install package bioepic, which no longer can be installed via pip with conda v4.5.7
pip install -t /home/your_user_name/.conda/envs/conda_fix3_SnakeMake/lib/python3.6/site-packages/ bioepic==0.2.5


source activate rhpc_fix_SnakeMake

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
