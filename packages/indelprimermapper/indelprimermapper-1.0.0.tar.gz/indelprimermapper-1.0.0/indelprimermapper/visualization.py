"""
Visualization of expected agarose gel banding patterns for indel markers
in F2:3 recombinant populations.
"""


import matplotlib.pyplot as plt




def _bands_for_genotype(allele_sizes, genotype):
"""Return fragment sizes for a given genotype (AA, AB, BB)."""
if genotype == 'AA':
return [allele_sizes['A']]
if genotype == 'BB':
return [allele_sizes['B']]
if genotype == 'AB':
return [allele_sizes['A'], allele_sizes['B']]
raise ValueError('Genotype must be AA, AB, or BB')




def plot_gel(marker1_sizes, marker2_sizes, f2_genotype, title=None, outfile=None):
lanes = ['Marker1', 'Marker2']
genotypes = [f2_genotype['marker1'], f2_genotype['marker2']]
size_maps = [marker1_sizes, marker2_sizes]


fig, ax = plt.subplots(figsize=(4, 6))


for i, (geno, sizes) in enumerate(zip(genotypes, size_maps), start=1):
bands = _bands_for_genotype(sizes, geno)
for band in bands:
ax.hlines(y=band, xmin=i-0.25, xmax=i+0.25, linewidth=6)


ax.set_xticks([1, 2])
ax.set_xticklabels(lanes)
ax.set_ylabel('Fragment size (bp)')
ax.invert_yaxis()


if title:
ax.set_title(title)


ax.set_xlim(0.5, 2.5)
ax.set_ylim(
max(marker1_sizes.values() | marker2_sizes.values()) + 20,
min(marker1_sizes.values() | marker2_sizes.values()) - 20
)


plt.tight_layout()


if outfile:
plt.savefig(outfile, dpi=300)
else:
plt.show()
