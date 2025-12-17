import pandas as pd




def read_variants(path):
"""Read variants from CSV or VCF."""
if path.endswith('.csv'):
df = pd.read_csv(path, header=None)
df.columns = ['chrom', 'pos', 'ref', 'alt']
elif path.endswith('.vcf'):
records = []
with open(path) as f:
for line in f:
if line.startswith('#'):
continue
chrom, pos, _, ref, alt, *_ = line.strip().split('\t')
records.append((chrom, int(pos), ref, alt))
df = pd.DataFrame(records, columns=['chrom', 'pos', 'ref', 'alt'])
else:
raise ValueError('Unsupported variant format')
return df

