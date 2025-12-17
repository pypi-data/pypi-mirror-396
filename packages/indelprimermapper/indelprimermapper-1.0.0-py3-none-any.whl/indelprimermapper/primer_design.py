import primer3


PRIMER3_PARAMS = {
'PRIMER_OPT_SIZE': 20,
'PRIMER_MIN_SIZE': 18,
'PRIMER_MAX_SIZE': 25,
'PRIMER_OPT_TM': 60.0,
'PRIMER_MIN_TM': 57.0,
'PRIMER_MAX_TM': 63.0,
'PRIMER_MIN_GC': 30.0,
'PRIMER_MAX_GC': 70.0,
'PRIMER_PRODUCT_SIZE_RANGE': [[100, 300]],
}




def design_primers(seq, target_start, target_len):
res = primer3.bindings.designPrimers(
{
'SEQUENCE_TEMPLATE': seq,
'SEQUENCE_TARGET': [target_start, target_len]
},
PRIMER3_PARAMS
)
return res
