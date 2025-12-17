"""
Integrate primer design results with visualization logic.
"""


from .visualization import plot_gel




def visualize_primer_pair(primer_row, genotype_pattern, outfile=None):
"""
Generate gel visualization for a selected primer pair.


primer_row : pandas.Series
Must contain product_size_A, product_size_B for two markers
genotype_pattern : dict
{'marker1': 'AA|AB|BB', 'marker2': 'AA|AB|BB'}
"""
marker1_sizes = {
'A': primer_row['marker1_A'],
'B': primer_row['marker1_B']
}
marker2_sizes = {
'A': primer_row['marker2_A'],
'B': primer_row['marker2_B']
}


plot_gel(
marker1_sizes,
marker2_sizes,
genotype_pattern,
title='Simulated F2:3 gel pattern',
outfile=outfile
)
