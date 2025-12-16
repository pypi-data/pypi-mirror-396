# ----------------------------------------------
# Table profiling: missing rate, column type (cat, num, date, datetime, key),
# column info (cat: relative frequency; num: summary), outlier exist ind
# ----------------------------------------------

import duckdb
import pandas as pd
import polars as pl
import pyarrow as pa
import math
from typing import Any, Dict, Optional


def profile_table(table: Any, num_to_cat_threshold=20, cat_to_key_threshold=100) -> pd.DataFrame:
    """
    Produce a rich profiling summary for each column in a dataset using DuckDB.

    Returns a Pandas DataFrame with columns:
        column, missing_rate, col_type, n_levels, col_info, outlier_exist_ind
    """

    # --- 1) Normalize input into a DuckDB-friendly format ---------------------
    if isinstance(table, pl.DataFrame):
        table = table.to_pandas()
    elif isinstance(table, pa.Table):
        table = table.to_pandas()
    elif isinstance(table, dict):
        table = pd.DataFrame(table)

    con = duckdb.connect()
    con.register("tmp_table", table)

    # --- 2) Extract schema info (DuckDB versions differ) ----------------------
    info = con.execute("PRAGMA table_info('tmp_table')").fetchdf()
    columns = info["name"].tolist()

    # Type column may vary across DuckDB versions
    if "column_type" in info.columns:
        dtypes = info["column_type"].tolist()
    elif "type" in info.columns:
        dtypes = info["type"].tolist()
    elif "data_type" in info.columns:
        dtypes = info["data_type"].tolist()
    else:
        raise ValueError(f"Unknown DuckDB PRAGMA table_info schema: {info.columns}")

    results = []

    # Helper for SQL-safe quoting of column names
    def q(col):
        return f'"{col}"'

    # --- 3) Process each column ------------------------------------------------
    total_rows = con.execute("SELECT COUNT(*) FROM tmp_table").fetchdf().iloc[0, 0]
    if total_rows == 0:
        total_rows = 1  # avoid division-by-zero
    for col, dtype in zip(columns, dtypes):
        col_q = q(col)
        missing_rate = con.execute(f"""
            SELECT
                SUM(CASE WHEN {col_q} IS NULL THEN 1 ELSE 0 END) * 1.0
                / COUNT(*) AS mr
            FROM tmp_table
        """).fetchdf()["mr"][0]

        # --- 3a) Column type detection ----------------------------------------
        col_lower = col.lower()
        dtype_lower = dtype.lower()

        if col_lower.endswith("id") or col_lower.endswith("key"):
            col_type = "key"
        elif "date" in col_lower:
            col_type = "date"
        elif "timestamp" in dtype_lower or "time" in dtype_lower:
            col_type = "datetime"
        elif dtype_lower in ["varchar", "char", "string", "text"]:        
            n_unique_values = int( con.execute(f"""
                SELECT COUNT(DISTINCT {col_q}) FROM tmp_table
            """).fetchdf().iloc[0, 0] )
            if (n_unique_values > 0) and (total_rows / n_unique_values < cat_to_key_threshold):
                col_type = "key"
            else:
                col_type = "cat"
        elif dtype_lower in ["int", "integer", "bigint", "smallint", "decimal", "numeric",
                             "double", "float", "real"]:
            n_unique_values = int( con.execute(f"""
                SELECT COUNT(DISTINCT {col_q}) FROM tmp_table
            """).fetchdf().iloc[0, 0] )
            if n_unique_values <= num_to_cat_threshold:
                col_type = "cat"
            else: 
                col_type = "num"
        else:
            col_type = "cat"

        n_levels = None
        col_summary: Dict[str, Any] = {}
        outlier_exist = None

        # --- 3b) Categorical column summary -----------------------------------
        if col_type == "cat":
            outlier_exist = None
            n_levels = int( con.execute(f"""
                SELECT COUNT(DISTINCT {col_q}) FROM tmp_table
            """).fetchdf().iloc[0, 0] )

            freq_df = con.execute(f"""
                SELECT 
                    {col_q} AS val,
                    COUNT(*) AS cnt,
                    ROUND(COUNT(*) * 1.0 / {total_rows}, 4) AS freq
                FROM tmp_table
                GROUP BY {col_q}
                ORDER BY cnt DESC
            """).fetchdf()

            if n_levels <= 5:
                col_summary = {
                    str(v): float(f)
                    for v, f in zip(freq_df["val"], freq_df["freq"])
                }
            else:
                top5 = freq_df.head(5)
                top_dict = {
                    str(v): float(f)
                    for v, f in zip(top5["val"], top5["freq"])
                }
                top_dict["other_values"] = float(freq_df["freq"].iloc[5:].sum())
                col_summary = top_dict

        # --- 3c) Numeric column summary ---------------------------------------
        elif col_type == "num":
            n_levels = None
            stats = con.execute(f"""
                SELECT
                    MIN({col_q}) AS min,
                    APPROX_QUANTILE({col_q}, 0.25) AS q1,
                    APPROX_QUANTILE({col_q}, 0.5) AS median,
                    APPROX_QUANTILE({col_q}, 0.75) AS q3,
                    MAX({col_q}) AS max
                FROM tmp_table
            """).fetchdf().iloc[0]

            q1 = stats["q1"]
            q3 = stats["q3"]
            median = stats["median"]
            mn = stats["min"]
            mx = stats["max"]

            # If column is constant or all-null, quantiles return None
            if pd.isna(q1) or pd.isna(q3):
                col_summary = {
                    "min": mn,
                    "q1": None,
                    "median": median,
                    "q3": None,
                    "max": mx,
                    "outlier_bound_lower": None,
                    "outlier_bound_upper": None,
                }
                outlier_exist = 0

            else:
                iqr = q3 - q1
                lb = q1 - 1.5 * iqr
                ub = q3 + 1.5 * iqr

                col_summary = {
                    "min": float(mn) if mn is not None else None,
                    "q1": float(q1),
                    "median": float(median),
                    "q3": float(q3),
                    "max": float(mx) if mx is not None else None,
                    "outlier_bound_lower": float(lb),
                    "outlier_bound_upper": float(ub),
                }

                outlier_exist = con.execute(f"""
                    SELECT CASE WHEN EXISTS (
                        SELECT 1 FROM tmp_table
                        WHERE {col_q} < {lb} OR {col_q} > {ub}
                    ) THEN 1 ELSE 0 END
                """).fetchdf().iloc[0, 0]
        else:
            n_levels = None
            col_summary = None
            outlier_exist = None

        # --- 4) Store result row ----------------------------------------------
        results.append({
            "column": col,
            "missing_rate": missing_rate,
            "col_type": col_type,
            "n_levels": n_levels,
            "col_info": col_summary,
            "outlier_exist_ind": outlier_exist
        })

    return pd.DataFrame(results)

   

# ---------------------------------------------
# Categorical variable bar plot
# ---------------------------------------------

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Any, Optional

def plot_cat_bar(
    table: Any,
    cat_col: str,
    target_col: Optional[str] = None,
    number_of_bars: Optional[int] = None,
):
    """
    Draw a bar plot for a categorical variable using DuckDB for aggregation
    and Plotly for visualization.

    Parameters
    ----------
    table : Any
        Input table (pandas, polars, Arrow, dict list, etc.)
    cat_col : str
        Name of the categorical column.
    target_col : str, optional
        Numeric or binary target variable. Default = None.
    number_of_bars : int, optional
        If None → include all categories (sorted alphabetically)
        If int → keep top-N by frequency; remaining combined into "other values".
    """

    con = duckdb.connect()
    con.register("tmp_table", table)

    # Extract category twice:
    # 1) category_num → numeric for sorting if possible
    # 2) category     → text for plotting
    if target_col is None:
        q = f"""
            SELECT 
                TRY_CAST({cat_col} AS DOUBLE) AS category_num,
                CAST({cat_col} AS TEXT) AS category,
                COUNT(*) AS count,
                ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS rel_freq,
                NULL AS avg_target
            FROM tmp_table
            GROUP BY category, category_num
        """
    else:
        q = f"""
            SELECT 
                TRY_CAST({cat_col} AS DOUBLE) AS category_num,
                CAST({cat_col} AS TEXT) AS category,
                COUNT(*) AS count,
                ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS rel_freq,
                ROUND(AVG({target_col}), 2) AS avg_target
            FROM tmp_table
            GROUP BY category, category_num
        """

    df = con.execute(q).fetchdf()

    # Decide on ordering
    if number_of_bars is None:
        # sort numerically when possible, fallback alphabetical
        df = df.sort_values(
            by=["category_num", "category"],
            na_position="last"
        ).reset_index(drop=True)

    else:
        # sort by count descending first to select top-K
        df_sorted = df.sort_values("count", ascending=False).reset_index(drop=True)

        if number_of_bars < len(df_sorted):
            top_df = df_sorted.iloc[:number_of_bars]
            others_df = df_sorted.iloc[number_of_bars:]

            # Weighted mean for target, if needed
            if target_col is None:
                avg_other = None
            else:
                avg_other = round(
                    (others_df["avg_target"] * others_df["count"]).sum()
                    / others_df["count"].sum(),
                    2
                )

            other_row = {
                "category_num": float("inf"),  # ensure it sorts last
                "category": "other values",
                "count": others_df["count"].sum(),
                "rel_freq": round(others_df["rel_freq"].sum(), 2),
                "avg_target": avg_other,
            }

            df = pd.concat([top_df, pd.DataFrame([other_row])], ignore_index=True)

            # Now sort top values numerically; "other values" stays last
            df_top = df[df["category"] != "other values"].sort_values(
                by=["category_num", "category"],
                na_position="last"
            )
            df_other = df[df["category"] == "other values"]

            df = pd.concat([df_top, df_other], ignore_index=True)

        else:
            df = df.sort_values(
                by=["category_num", "category"],
                na_position="last"
            ).reset_index(drop=True)

    # Plot
    fig = px.bar(
        df,
        x="category",
        y="count",
        text="count",
        title=f"Categorical Distribution: {cat_col}",
        labels={"category": cat_col, "count": "Count"}
    )    

    # Hover information
    hover_template = (
        "Group: %{x}<br>"
        "Count: %{y}<br>"
        "Relative Frequency: %{customdata[0]}%<br>"
    )

    if target_col is not None:
        hover_template += "Avg Target: %{customdata[1]}<br>"

    fig.update_traces(
        customdata=df[["rel_freq", "avg_target"]] if target_col else df[["rel_freq"]],
        hovertemplate=hover_template,
        textposition="none"
    )

    fig.update_layout(
        xaxis_tickangle=45,
        margin=dict(l=40, r=40, t=80, b=120)
    )


    fig.show()

    return df, fig

# -------------------------------------------
# Numerical variable plot: histogram, or box plot 
# -------------------------------------------

from typing import Any, Union, List
import pandas as pd
import polars as pl
import numpy as np  
import duckdb
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

def plot_numeric(table: Any, num_col: str, plot_type: str = 'hist'):
    """
    Draw histogram or box plot of a numerical variable.

    Parameters
    ----------
    table : pandas.DataFrame | polars.DataFrame | str | pyarrow.Table
        Input table
    num_col : str
        Name of the numerical column
    plot_type : str, 'hist' or 'box'
    """
    # Normalize plot_type to list
    if isinstance(plot_type, str):
        plot_type = [plot_type]

    # Convert Polars to Pandas
    if isinstance(table, pl.DataFrame):
        table = table.to_pandas()

    # Register table in DuckDB for convenient aggregation if needed
    con = duckdb.connect()
    con.register("tmp_table", table)

    # Extract column as Pandas Series
    df = con.execute(f"SELECT {num_col} FROM tmp_table").fetchdf()

    for pt in plot_type:
        if pt == 'hist':
            fig = px.histogram(df, x=num_col, nbins=50, histnorm='probability density', title=f'Histogram of {num_col}')
            fig.update_traces(opacity=0.6)
            # Extract non-null values into a numpy array
            data = df[num_col].dropna().to_numpy()
            # Compute KDE
            # kde = gaussian_kde(data, bw_method='scott')
            kde = gaussian_kde(data, bw_method='silverman')
            x_range = np.linspace(data.min(), data.max(), 1000)
            y_kde = kde(x_range)

            fig.add_trace(go.Scatter(
                x=x_range,
                y=y_kde,
                mode='lines',
                name="KDE",
                line=dict(color='red', width=2)
            ))

            fig.update_layout(height=500)
            fig.show()
        elif pt == 'box':
            fig = px.box(df, y=num_col, points='all', title=f'Box plot of {num_col}')
            fig.update_layout(height=500)
            fig.show()
        else:
            raise ValueError(f"Invalid plot_type '{pt}', choose from 'hist','box'")
