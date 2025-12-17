IndelPrimerMapper
=================


IndelPrimerMapper is an automated pipeline for **indel-based marker development** and
**QTL fine mapping** in recombinant plant populations (e.g. F2:3).


Features
--------
- Indel extraction from VCF / CSV
- Primer design using Primer3
- Genome-wide specificity validation using BLAST
- Visualization of recombinant vs non-recombinant gel patterns


Installation
------------
```
pip install indelprimermapper
```


Usage
-----
```
indelprimermapper --variants variants.csv \
--reference genome.fa \
--blast-db genome_db \
--out primers.xlsx
```


Citation
--------
See CITATION.cff
