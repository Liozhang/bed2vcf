bed2vcf="./src/bed2vcf.py"
clinvar="./data/clinvar_20211010.vcf.gz"
gff3="/data/human_genome/ensembl/Homo_sapiens.GRCh38.103.gff3.gz"
ref_fa="/data/human_genome/ensembl/Homo_sapiens.GRCh38.dna.primary_assembly.fa"


# All_isec.bed, no info
python $bed2vcf -f ./data/All_isec.bed  -r $ref_fa -c 1,3,4,5 -o ./test_out/All_isec.vcf

# All_isec.anno.bed, no header
python $bed2vcf -f ./data/All_isec.anno.bed  -r $ref_fa -c 1,3,4,5 -i 6,7 -t String,String -o ./test_out/All_isec.anno.vcf

# All_isec.anno.bed, give header
python $bed2vcf -f ./data/All_isec.anno.bed  -r $ref_fa -c CHROM,END,REF,ALT -i REGION,GENE_ID -t String,String -o ./test_out/All_isec.anno.vcf -H CHROM,START,END,REF,ALT,REGION,GENE_ID

# All_isec.header.bed, has header
python $bed2vcf -f ./data/All_isec.header.bed  -r $ref_fa -c CHROM,END,REF,ALT -o ./test_out/All_isec.header.vcf -i FEATURE,GENE_ID -t String,String --has_header True

# predict haplotype 
bcftools csq ./test_out/All_isec.header.vcf -f $ref_fa -g $gff3 -Ov --local-csq --threads 5 --force -o ./test_out/All_isec.header.csq.vcf

# annotate vcf by using SnpSift
cat ./test_out/All_isec.header.csq.vcf | SnpSift annotate $clinvar > ./test_out/All_isec.header.anno.vcf

# extract fields
cat ./test_out/All_isec.header.anno.vcf | SnpSift extractFields ./test_out/All_isec.header.anno.vcf CHROM POS REF ALT GENE_ID CLNSIG CLNVC BCSQ > ./test_out/All_isec.header.anno.xls

echo "Done !!"