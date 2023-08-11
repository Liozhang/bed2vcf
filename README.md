# bed2vcf
Convert BED or TSV formatted files to VCF files using a reference genome.

## Installation

1. **Directly install by using conda.**

```git clone https://github.com/Liozhang/bed2vcf.git
cd bed2vcf```

```conda install -c bioconda -c conda-forge --file requirement.txt```

or

```conda install -c bioconda -c conda-forge bcftools=1.15 snpsift=4.3 pandas tabix=1.11 samtools=1.15```

## Prepare Reference File

* Download file

Clinvar: [clinvar_20211010.vcf.gz](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar_20211010.vcf.gz)

hg38: [FASTA](http://ftp.ensembl.org/pub/release-103/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz) | [GFF3](http://ftp.ensembl.org/pub/release-103/gff3/homo_sapiens/Homo_sapiens.GRCh38.103.gff3.gz)

* Index reference file

```samtools faidx Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
tabix clinvar_20211010.vcf.gz```

## Test and output

```bash bed2vcf_anno.sh```

* Input format

Must have specify `CHROM` `POS` `REF` `ALT` columns in TSV file.

* Output format

Like [VCFv4.2](https://samtools.github.io/hts-specs/VCFv4.2.pdf), but without `FORMAT` field.
