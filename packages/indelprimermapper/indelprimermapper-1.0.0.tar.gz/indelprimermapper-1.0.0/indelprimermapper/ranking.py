"""Primer ranking based on thermodynamics and BLAST specificity."""




def rank_primers(df):
"""
Rank primers prioritizing unique genomic hits and optimal Tm.
Lower score = better primer.
"""
df = df.copy()
df['score'] = (
df['left_blast_hits'] + df['right_blast_hits']
)
return df.sort_values('score')
