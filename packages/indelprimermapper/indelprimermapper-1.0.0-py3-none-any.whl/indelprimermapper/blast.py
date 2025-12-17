import subprocess

def blast_primer(seq, blast_db):
"""Return number of BLAST hits for a primer sequence."""
cmd = [
'blastn', '-task', 'blastn-short',
'-db', blast_db,
'-query', '-',
'-outfmt', '6'
]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
out, _ = p.communicate(seq)
if not out.strip():
return 0
return len(out.strip().split('\n'))
