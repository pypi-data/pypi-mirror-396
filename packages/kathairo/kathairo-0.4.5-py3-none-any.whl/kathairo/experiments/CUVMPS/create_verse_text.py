import polars as pl

df = pl.read_csv("nt_CUVMPS_minimum.tsv", separator='\t', infer_schema_length=0)

df = df.with_columns(pl.col("id").str.slice(0, 8))

result = df.group_by("id").agg([
    pl.col("text").str.concat("")
])

result = result.sort("id")

output_file_name = "nt_CUVMPS_verse.tsv"

result.write_csv(output_file_name, separator='\t')