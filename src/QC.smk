

rule phantom:
    input:
        t=PATH_BAM+'{sample}.mq20.bam',
        c=lambda wildcards: PATH_BAM+PeakCall.loc[PeakCall.Signal == wildcards.sample].Input +'.mq20.bam'
    output:
        PATH_QC + '{sample}.phantom'
    log:
        PATH_LOG+'{sample}.phantom.log'
    conda:
        '../env/phantom.yaml'
    params:
        path=srcdir('..')+'/'+config['phantompeak']['path']
    shell:
        """
            Rscript {params.path}run_spp.R -rf -c={input.t} -i={input.c} -savp -out={output} &> {log}
        """

rule fastqc_fastq:
    input:
        PATH_BAM+"{sample}.bam"
    output:
        html=PATH_QC+"{sample}_fastqc.html",
        zip=PATH_QC+"{sample}_fastqc.zip"
    wrapper:
        "0.17.0/bio/fastqc"


rule multiqc:
    input:
        expand(PATH_QC+"{sample}_fastqc.html", sample=ALLID)
    output:
        PATH_OUT + "/multiqc_report.html"
    log:
        "logs/multiqc.log"
    wrapper:
        "0.27.1/bio/multiqc"


