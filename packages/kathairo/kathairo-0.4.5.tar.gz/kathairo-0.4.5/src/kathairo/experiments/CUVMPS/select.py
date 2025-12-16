import polars as pl

df = pl.read_csv("nt_CUVMPS.tsv", separator='\t', infer_schema_length=0)

results = df.select([pl.col("id"), pl.col("text")])

results.write_csv("nt_CUVMPS_minimum.tsv", separator='\t')