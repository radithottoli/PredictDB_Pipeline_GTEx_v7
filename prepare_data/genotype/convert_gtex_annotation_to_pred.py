#!/usr/bin/env python
__author__ = "alvaro barbeira"

import os
import gzip

SNP_LIST="/group/im-lab/nas40t2/abarbeira/data/hapmapSnpsCEU_f.list.gz"
SNP_FREQUENCIES="gtex_v8_freq.txt.gz"
ANNOTATION="/group/gtex-group/v8/60111/gtex/exchange/GTEx_phs000424/exchange/analysis_releases/GTEx_Analysis_2017-06-05_v8/genotypes/WGS/variant_calls/GTEx_Analysis_2017-06-05_v8_WholeGenomeSeq_838Indiv_Analysis_Freeze.lookup_table.txt.gz"
OUTPUT_FOLDER = "."
OUTPUT_PREFIX = "gtex_v8_eur_shapeit2_phased_maf01_snp_annot"
MAF=0.01

def read_snp_list(path):
    r=[]
    with gzip.open(path) as f:
        for l in f:
            r.append(l.decode().strip())
    return r

def filter_snp_frequencies(path, snps, maf):
    k = set()
    with gzip.open(path) as f:
        #discard header
        f.readline()
        for i,line in enumerate(f):
            comps = line.decode().strip().split()
            f = float(comps[1])
            snp = comps[0]
            if maf<f and f<1-maf:
                if snp in snps:
                    k.add(snp)
    return k

def read_snp_frequencies(path, maf):
    k = {}
    with gzip.open(path) as f:
        f.readline()
        for line in f:
            comps = line.decode().strip().split()
            f = float(comps[1])
            if maf<f and f< 1-maf:
                snp = comps[0]
                k[snp] = f
    return k


def _v7pipelineformat(comps):
    c = comps[0:5] + ["NA", "NA", "NA"] + [comps[6]]
    return "{}\n".format("\t".join(c))

def run():
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)

    print("reading snp list")
    snps = {x for x in read_snp_list(SNP_LIST)}

    print("processing gtex snp frequencies")
    snp_frequencies = read_snp_frequencies(SNP_FREQUENCIES, MAF)
    #snps = filter_snp_frequencies(SNP_FREQUENCIES, snps, MAF)

    print("processing annotation")
    last_chr = None
    chromosomes = {str(i) for i in range(1,23)}
    alleles = {"C","G", "T", "A"}
    o = None
    with gzip.open(ANNOTATION) as f:
        header = f.readline().decode()
        for i,line in enumerate(f):
            line = line.decode()
            comps = line.strip().split()

            if not comps[6] in snps: continue

            chr_ = comps[0].split("chr")[1]
            if not chr_ in chromosomes: continue

            if not comps[3] in alleles or not comps[4] in alleles: continue

            if chr_ != last_chr:
                print(chr_)
                if o: o.close()
                last_chr = chr_
                o = open(os.path.join(OUTPUT_FOLDER, OUTPUT_PREFIX + ".chr{}.txt".format(chr_)), "w")

                #ideally, we keep the original header. But no. Never the right thing.
                #o.write(header)
                o.write("chromosome\tpos\tvarID\tref_vcf\talt_vcf\tR2\tMAF\trsid\trsid_dbSNP150\n")
            #Ugh.
            line = _v7pipelineformat(comps)
            o.write(line)
        o.close()

if __name__ == "__main__":
    run()