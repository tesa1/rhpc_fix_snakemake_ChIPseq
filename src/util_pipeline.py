from subprocess import PIPE, Popen
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import urllib.request
import os, glob
from pathlib import Path
import subprocess as sp

def query_SRX(GSM_ACC, path_ncbitoolkit='/home/NFS/users/yo.kim/lib/softwares/edirect/'):
    p1 = Popen([path_ncbitoolkit + "esearch", "-db", "gds", "-query", '"' + GSM_ACC  +'"'],stdout=PIPE)
    p2 = Popen([path_ncbitoolkit + "efetch", "-format", "docsum"], stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    p3 = Popen([path_ncbitoolkit + "xtract", "-pattern", "ExtRelations", "-element", "TargetObject"],
                stdin = p2.stdout, stdout = PIPE)
    p2.stdout.close()
    tmp = p3.communicate()[0].decode("utf-8").split('\n')
    return tmp[len(tmp)-2]

def query_SRR(GSM_ACC, path_ncbitoolkit='/home/NFS/users/yo.kim/lib/softwares/edirect/', db="sra"):
    p1 = Popen([path_ncbitoolkit + "esearch", "-db", db, "-query", '"' + GSM_ACC  +'"'],stdout=PIPE)
    p2 = Popen([path_ncbitoolkit + "efetch", "-format", "docsum"], stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    p3 = Popen([path_ncbitoolkit + "xtract", "-pattern", "DocumentSummary", "-element", "Run@acc"],
                stdin = p2.stdout, stdout = PIPE)
    p2.stdout.close()
    tmp = p3.communicate()[0].decode("utf-8").split('\t')
    return list(set(tmp)-set(['']))


def get_paths(IDs, PATH_DATA, ext="bam"):
    # open specified URL
    Files = dict()
    FullPath = dict()

    if isinstance(PATH_DATA, str):
        PATH_DATA = PATH_DATA.split()

    for ID in IDs:
        Files[ID] = []
        FullPath[ID] = []

#    for PATH in list(PATH_DATA):
#        print("reading path:")
#        print(PATH)

#        response = Request(PATH)
#        html = urlopen(response)

#        print("..success")
#        print("")

        # find the link for files
#        print("find specified files...")
#        soup = BeautifulSoup(html.read(), "html.parser")

#        for link in soup.find_all('a'):
#            name = link.get('href')
#            for ID in IDs:
#                if ID.lower() in name.lower() and name.endswith(ext):
#                    Files[ID] = list(set(Files[ID]).union(set([name])))
#                    FullPath[ID] = list(set([PATH + name]).union(set(FullPath[ID])))

    for ID, PATH in zip(list(IDs), list(PATH_DATA)):
        print("reading path:")
        print(PATH)

        response = Request(PATH)
        html = urlopen(response)

        print("..success")
        print("")

        # find the link for files
        print("find specified files...")
        soup = BeautifulSoup(html.read(), "html.parser")

        for link in soup.find_all('a'):
            name = link.get('href')
            if ID.lower() in name.lower() and name.endswith(ext):
                Files[ID] = list(set(Files[ID]).union(set([name])))
                FullPath[ID] = list(set([PATH + name]).union(set(FullPath[ID])))
    # check if all specified files can be found
    for ID in IDs:
        if len(Files[ID]) == 0:
            raise Exception(str(ID) + " is not found at the path!")
        if len(Files[ID]) > 1:
            raise Exception("Multiple files with the pattern (ID): " + str(ID) + "!!")

    return Files, FullPath

def fastq_dump(sample, PATH_FASTQ, PATH_LOG, PATH_EDIRECT, PATH_SRATOOL):
    print(sample)
    SRRs = query_SRR(str(sample), path_ncbitoolkit=PATH_EDIRECT) # get SRR accession from GSM ID

    for i in range(len(SRRs)):
        SRRs[i] = SRRs[i].split("\n")[0]

    print(SRRs)
    if not os.path.exists(PATH_LOG):
        os.makedirs(PATH_LOG)

    for SRR in SRRs:
        stdout_fn = Path(PATH_LOG + SRR + ".fastq_dump.log")
        if not os.path.isfile(PATH_FASTQ+SRR+'.fastq.gz'):
            print('fastq-dump : ' + SRR)
            with stdout_fn.open('w') as stdout_f:
                p = sp.run([PATH_SRATOOL+'fastq-dump', '--split-3', '--skip-technical',
                            '-I', '--gzip', '-O', PATH_FASTQ, SRR], stderr=stdout_f)

    if len(SRRs)>1:
        isSE = len(glob.glob(PATH_FASTQ + "/" + SRRs[0] + '*.fastq.gz'))  == 1
        if isSE: #in case of single-end
            outfile = Path(PATH_FASTQ+str(sample)+'.fastq.gz')
            command = ['cat']
            for SRR in SRRs:
                command.append(PATH_FASTQ+SRR+'.fastq.gz')
            with outfile.open('w') as out:
                print(command)
                p = sp.run(command, stdout=out)
        else: #in case of paired-end
            outfile1 = Path(PATH_FASTQ + str(sample) + '_1.fastq.gz')
            outfile2 = Path(PATH_FASTQ + str(sample) + '_2.fastq.gz')
            command1 = ['cat']
            command2 = ['cat']
            for SRR in SRRs:
                command1.append(PATH_FASTQ+SRR+'_1.fastq.gz')
                command2.append(PATH_FASTQ+SRR+'_2.fastq.gz')
                with outfile1.open('w') as out:
                    print(command1)
                    p = sp.run(command1, stdout=out)
                with outfile2.open('w') as out:
                    print(command2)
                    p = sp.run(command2, stdout=out)
    else:
        isSE = len(glob.glob(PATH_FASTQ + '/' + SRRs[0] + '*.fastq.gz')) == 1
        if isSE:
            p = sp.run(['mv', PATH_FASTQ + SRRs[0] + '.fastq.gz', PATH_FASTQ + str(sample) + '.fastq.gz'])
        else:
            p = sp.run(['mv', PATH_FASTQ + SRRs[0] + '_1.fastq.gz', PATH_FASTQ + str(sample) + '_1.fastq.gz'])
            p = sp.run(['mv', PATH_FASTQ + SRRs[0] + '_2.fastq.gz', PATH_FASTQ + str(sample) + '_2.fastq.gz'])

