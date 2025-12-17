def filter_indels(df):
"""Keep only indels."""
return df[df['ref'].str.len() != df['alt'].str.len()].copy()
