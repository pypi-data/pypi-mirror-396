from pyfaidx import Fasta

def get_flanking_sequence(fasta_path, chrom, pos, flank=300):
fa = Fasta(fasta_path)
start = max(1, pos - flank)
end = pos + flank
return str(fa[chrom][start-1:end])
