import pandas as pd
from .io import read_variants
from .indel import filter_indels
from .genome import get_flanking_sequence
from .primer_design import design_primers
from .blast import blast_primer




def run_pipeline(variants, reference, blast_db):
df = read_variants(variants)
df = filter_indels(df)
results = []


for _, row in df.iterrows():
seq = get_flanking_sequence(reference, row.chrom, row.pos)
target_start = 300
target_len = abs(len(row.ref) - len(row.alt))
primers = design_primers(seq, target_start, target_len)


if primers.get('PRIMER_PAIR_NUM_RETURNED', 0) > 0:
left = primers['PRIMER_LEFT_0_SEQUENCE']
right = primers['PRIMER_RIGHT_0_SEQUENCE']
left_hits = blast_primer(left, blast_db)
right_hits = blast_primer(right, blast_db)
results.append({
'chrom': row.chrom,
'pos': row.pos,
'left_primer': left,
'right_primer': right,
'left_blast_hits': left_hits,
'right_blast_hits': right_hits
})


return pd.DataFrame(results)
