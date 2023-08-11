# pyhon=3.7 or newer
import os
import argparse
import pandas as pd

def get_options():
    usage = (
        """
        Given a tab-separated value file, creates a VCF file.
        
        # if file has header
        python this.py -files file.bed -c CHROM,POS,REF,ALT -i INFO1,INFO2 -t String,String -r ref.fa -o output.vcf --has_header
        
        # if file has no header
        python this.py -files file.bed -c 1,3,4,5 -i 6,7 -t String,String -r ref.fa -o output.vcf
        
        # if file has no header and want to give header
        python this.py -files file.bed -c CHROM,POS,REF,ALT -i INFO1,INFO2 -t String,String -r ref.fa -o output.vcf -H CHROM,START,END,REF,ALT,INFO1,INFO2
        """
    )
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--tsv', type=str, help='Input tsv file', required=True)
    parser.add_argument('-c', '--required_cols', type=str, help='Input the chr, pos, ref, alt col names in order, split by comma', default='1,3,4,5',required=True)
    parser.add_argument('-i', '--info_cols', type=str, help='Input colnames to put in info column')
    parser.add_argument('-t', '--info_types', type=str, help='Input col types for the info columns, should match info cols in order. choose from Integer, Float, String')
    parser.add_argument('-r', '--ref_fa', type=str, help='Reference fasta file', required=None)
    parser.add_argument('-o', '--output', type=str, help='Output file', default='bed2vcf.vcf')
    parser.add_argument('-H', '--header', type=str, help='Header for each column, if None, use numeric index for info_cols', default=None)
    parser.add_argument('--has_header', type=bool, help='Has header', default=False)
    parser.add_argument('--fai', type=bool, help='Reference fasta index, can directly specify without -r', default=None)
    options = parser.parse_args()
    # Check parameters
    if not options.tsv or (not options.ref_fa and not options.fai) or not options.required_cols:
        raise ValueError(usage)
    # Check files
    if not os.path.exists(options.tsv):
        raise FileNotFoundError(f'Check {options.tsv} !')
    
    if options.ref_fa:
        options.fai = options.ref_fa + '.fai'
    if not os.path.exists(options.fai):
        raise FileNotFoundError(f'Check {options.fai} !')

    out_dir = os.path.dirname(options.output)
    if out_dir != '' and not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    # Configure columns
    if options.header:
        options.header = [ i.strip() for i in options.header.split(',')]
    if options.required_cols:
        options.required_cols = [ i.strip() for i in options.required_cols.split(',')]
        if not options.header and not options.has_header:
            options.required_cols = [int(i) - 1 for i in options.required_cols]
    if options.info_cols:
        options.info_cols = [ i.strip() for i in options.info_cols.split(',')]
        if not options.header and not options.has_header:
            options.info_cols = [int(i) - 1 for i in options.info_cols]
    if options.info_types:
        options.info_types = [ i.strip() for i in options.info_types.split(',')]
        
    print(f'header: {options.header}')
    print(f'required_cols: {options.required_cols}')
    print(f'info_cols: {options.info_cols}')
    print(f'info_types: {options.info_types}')
    return options


class vcfheader:
    def __init__(self):
        self.vcf_version = self.get_vcf_version()
        self.info = []
        self.contig = []
        self.columns = ['#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n']
        
    def get_vcf_version(self):
        return "##fileformat=VCFv4.2\n"
    
    def add_info(self, column, type):
        info = f'##INFO=<ID={column},Number=.,Type={type},Description="{column}">\n'
        self.info.append(info)
        return info
    
    def add_contig(self, contig, length):
        contig = f'##contig=<ID={contig},length={length}>\n'
        return contig
        
    def add_ref_contigs(self, ref_fai):
        contigs = []
        fai = pd.read_csv(ref_fai, sep='\t', header=None, usecols=[0,1], names=['contig', 'length'])
        for _, row in fai.iterrows():
            contig = row['contig']
            length = row['length']
            contigs.append(self.add_contig(contig, length))
        self.contig = contigs
        return contigs
            
    
    def get_vcf_header(self):
        header = [self.vcf_version] + self.info + self.contig + self.columns
        self.vcf_header = [i for i in header if i and i != '']
        return self.vcf_header


if __name__ == '__main__':
    options = get_options()
    # Load tsv file
    if options.has_header and not options.header:
        tsv = pd.read_csv(options.tsv, sep='\t')
        options.header = tsv.columns
    elif not options.header:
        tsv = pd.read_csv(options.tsv, sep='\t', header=None)
        options.header = tsv.columns
    else:
        tsv = pd.read_csv(options.tsv, sep='\t', header=None, names=options.header)
        
    # Select required columns
    if not options.info_cols:
        tsv = tsv[options.required_cols]
    else:
        tsv = tsv[options.required_cols + options.info_cols]
    tsv = tsv.fillna(0)
        
    print(f'Got file {tsv.shape}:\n{tsv.head()}')
        
    # create vcf header
    vcf_header = vcfheader()
    if options.info_cols:
        for i in options.info_cols:
            vcf_header.add_info(i, options.info_types[options.info_cols.index(i)])
    vcf_header.add_ref_contigs(options.fai)
    vcf_header = vcf_header.get_vcf_header()
    vcf_header = "".join(vcf_header)
    
    # TSV to VCF
    vcf = pd.DataFrame(columns = ['#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO'])
    vcf['#CHROM'] = tsv.iloc[:, 0]
    vcf['POS'] = tsv.iloc[:, 1]
    vcf['ID'] = ''
    vcf['REF'] = tsv.iloc[:, 2]
    vcf['ALT'] = tsv.iloc[:, 3]
    vcf['QUAL'] = 100
    vcf['FILTER'] = 'PASS'
    
    # Process INFO columns
    if options.info_cols:
        for col in options.info_cols:
            tsv[col] = tsv[col].apply(lambda x: f'{col}={x}')
        info = tsv[options.info_cols].apply(lambda x: ';'.join(x), axis=1)
        vcf['INFO'] = info
    else:
        vcf['INFO'] = ''
    
    print(f'Output : {options.output}\n{vcf.head()}')
    
    # Output
    with open(options.output, 'w') as f:
        f.write(vcf_header)
    vcf.to_csv(options.output, sep='\t', index=False, header=False, mode='a')
        
        
    
