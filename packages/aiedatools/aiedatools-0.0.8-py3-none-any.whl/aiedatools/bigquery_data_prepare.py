from typing import Optional
import pyarrow as pa
from google.cloud import bigquery
import duckdb
import pandas as pd
import polars as pl

def clean_arrow_for_polars(
    arrow_table: pa.Table,
    decimal_to: str = "float64",  # "float64" or "string"
    unsafe_int_to: str = "string" # fallback type for large ints that overflow int64
) -> pa.Table:
    """
    Convert Arrow Table types to be fully compatible with Polars.
    
    Parameters
    ----------
    arrow_table : pa.Table
        The input Arrow table.
    decimal_to : str
        How to handle DECIMAL types: "float64" (fast) or "string" (safe).
    unsafe_int_to : str
        How to handle integers larger than 64-bit that cannot safely cast to int64.
    
    Returns
    -------
    pa.Table
        Arrow table with all types compatible with Polars.
    """
    new_fields = []

    for field in arrow_table.schema:
        ftype = field.type

        # Handle large integers (>64 bit)
        if pa.types.is_integer(ftype) and ftype.bit_width > 64:
            # Try casting to int64
            try:
                cast_table = arrow_table.cast(pa.field(field.name, pa.int64()))
                new_fields.append(pa.field(field.name, pa.int64()))
            except pa.ArrowInvalid:
                # fallback
                if unsafe_int_to.lower() == "string":
                    new_fields.append(pa.field(field.name, pa.string()))
                else:
                    raise ValueError(f"Cannot cast {field.name} to unsafe type {unsafe_int_to}")

        # Handle decimals
        elif pa.types.is_decimal(ftype):
            if decimal_to.lower() == "float64":
                new_fields.append(pa.field(field.name, pa.float64()))
            elif decimal_to.lower() == "string":
                new_fields.append(pa.field(field.name, pa.string()))
            else:
                raise ValueError(f"Invalid decimal_to value: {decimal_to}")

        # Keep everything else
        else:
            new_fields.append(field)

    new_schema = pa.schema(new_fields)

    # Attempt cast
    try:
        return arrow_table.cast(new_schema)
    except pa.ArrowInvalid:
        # If casting fails, convert all unsafe types to string as last resort
        fallback_fields = []
        for field in arrow_table.schema:
            ftype = field.type
            if (pa.types.is_integer(ftype) and ftype.bit_width > 64) or pa.types.is_decimal(ftype):
                fallback_fields.append(pa.field(field.name, pa.string()))
            else:
                fallback_fields.append(field)
        fallback_schema = pa.schema(fallback_fields)
        return arrow_table.cast(fallback_schema)


def bq_to_polars(query: str) -> pl.DataFrame:
    """
    Run a BigQuery SQL query and return a Polars DataFrame,
    automatically fixing unsupported Arrow types.
    """
    client = bigquery.Client()
    result = client.query(query).result()
    arrow_table = result.to_arrow()

    arrow_table = clean_arrow_for_polars(
        arrow_table,
        decimal_to="float64",   # or "string" for precise decimals
        unsafe_int_to="string"  # fallback for huge integers
    )

    return pl.from_arrow(arrow_table)



