# ------------------------------------------------
# P-value heatmap 
# ------------------------------------------------

import pandas as pd
import numpy as np
from scipy.stats import pearsonr, f_oneway, ttest_ind, chi2_contingency
import plotly.express as px


def plot_pvalue_heatmap(df, list_var_num=[], list_var_cat=[],
                        show_fig=True, categorical_threshold=20,
                        significance_level=0.05):
    """
    Draws a p-value heatmap and returns:
      (1) Plotly figure
      (2) p-value matrix
      (3) A table of significant pairs (p < significance_level)
    """
    # If both list_var_num are empty or the number of variables in both list 
    # are less than 2, raise an error and return None
    if len(list_var_num) + len(list_var_cat) < 2:
        raise ValueError("At least two variables are required to compute p-values")
        return None, None, None

    # ---------------------------------------------------------------------
    # Warn if user treats continuous variables as categorical
    # ---------------------------------------------------------------------
    for var in list_var_cat:
        if var in df.columns:
            col_dtype = df[var].dtype
            if pd.api.types.is_numeric_dtype(col_dtype):
                if df[var].nunique() > categorical_threshold:
                    print(
                        f"Warning: variable '{var}' is numeric with {df[var].nunique()} "
                        "unique values but is placed in list_var_cat. "
                        "Ensure it is truly categorical."
                    )

    # ---------------------------------------------------------------------
    # Function to compute pairwise p-value
    # ---------------------------------------------------------------------
    def calculate_p_value(df, var1, var2):
        df_pair = df[[var1, var2]].dropna()

        # Numeric vs Numeric
        if var1 in list_var_num and var2 in list_var_num:
            # Force conversion to numeric (safe)
            s1 = pd.to_numeric(df_pair[var1], errors="coerce")
            s2 = pd.to_numeric(df_pair[var2], errors="coerce")

            mask = s1.notna() & s2.notna()

            if mask.sum() < 3:  # not enough data to compute Pearson
                return 1.0, "Pearson (insufficient data)"

            _, p = pearsonr(s1[mask], s2[mask])
            method = "Pearson"
            return p, method

        # Numeric vs Categorical
        if (var1 in list_var_num and var2 in list_var_cat) or \
        (var2 in list_var_num and var1 in list_var_cat):

            num_var = var1 if var1 in list_var_num else var2
            cat_var = var2 if num_var == var1 else var1

            # Ensure numeric conversion
            df_pair[num_var] = pd.to_numeric(df_pair[num_var], errors="coerce")
            df_pair = df_pair.dropna()

            # Build groups
            groups = [
                df_pair[num_var][df_pair[cat_var] == c]
                for c in df_pair[cat_var].unique()
            ]

            # Remove empty groups
            groups = [g for g in groups if len(g) > 0]

            if len(groups) < 2:
                return 1.0, "T-test/ANOVA (skipped - only 1 group)"

            if len(groups) == 2:
                # Two groups → t-test
                g1, g2 = groups
                if len(g1) < 2 or len(g2) < 2:
                    return 1.0, "T-test (skipped - small group)"
                _, p = ttest_ind(g1, g2)
                return p, "T-test"

            # More than 2 groups → ANOVA
            if any(len(g) < 2 for g in groups):
                return 1.0, "ANOVA (skipped - empty/small group)"
            _, p = f_oneway(*groups)
            return p, "ANOVA"

        # Categorical vs Categorical
        if var1 in list_var_cat and var2 in list_var_cat:
            table = pd.crosstab(df_pair[var1], df_pair[var2])
            if table.shape[0] > 1 and table.shape[1] > 1:
                _, p, _, _ = chi2_contingency(table)
                method = "Chi-square"
            else:
                p = 1.0  # Cannot test if insufficient unique values
                method = "Chi-square (skipped)"
            return p, method

        return np.nan, "N/A"

    # ---------------------------------------------------------------------
    # Build p-value matrix
    # ---------------------------------------------------------------------
    var_all = list_var_num + list_var_cat
    p_matrix = pd.DataFrame(
        np.ones((len(var_all), len(var_all))),
        index=var_all, columns=var_all
    )
    method_matrix = pd.DataFrame("", index=var_all, columns=var_all)

    # Compute only upper triangle for speed
    for i, v1 in enumerate(var_all):
        for j, v2 in enumerate(var_all[i+1:], i+1):
            # print(f"Calculating p-value for {v1} vs {v2}")
            p, method = calculate_p_value(df, v1, v2)
            p_matrix.loc[v1, v2] = p
            p_matrix.loc[v2, v1] = p
            method_matrix.loc[v1, v2] = method
            method_matrix.loc[v2, v1] = method

    # ---------------------------------------------------------------------
    # Plot heatmap
    # ---------------------------------------------------------------------
    fig = px.imshow(
        p_matrix,
        color_continuous_scale="Oryel_r",
        zmin=0, zmax=1,
        title="P-value Heatmap",
        labels={"color": "P-value"}
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>"
                      "p-value = %{z}<br>"
                      "test = %{customdata}",
        customdata=method_matrix.values
    )

    fig.update_layout(width=1000, height=800)

    if show_fig:
        fig.show()

    # ---------------------------------------------------------------------
    # Build significant-pair table
    # ---------------------------------------------------------------------
    records = []
    for i, var1 in enumerate(var_all):
        for j, var2 in enumerate(var_all[i+1:], i+1):

            p = p_matrix.loc[var1, var2]
            if p < significance_level:
                method = method_matrix.loc[var1, var2]
                records.append({
                    "var1": var1,
                    "var2": var2,
                    "method": method,
                    "pvalue": p
                })

    df_significant = pd.DataFrame(records)

    return fig, p_matrix, df_significant

# ---------------------------------------------------------------------
# Correlation heatmap
# ---------------------------------------------------------------------

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_corr_heatmap(
    df: pd.DataFrame,
    var_num: list,
    show_fig: bool = True,
    title: str = "Correlation Plot (Heatmap)",
    colorscale: str = "Oryel",
    round_decimals: int = 2,
    width: int = 900,
    height: int = 700,
    drop_na: bool = True,
    tickangle: int = 45,
    color_by_absolute: bool = True
):
    """
    Draw a correlation heatmap for selected numerical variables in a DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.
        var_num (list): Columns to compute correlations.
        show_fig (bool): Show the figure or return it.
        title (str): Heatmap title.
        colorscale (str): Plotly color scale.
        round_decimals (int): Round correlation values.
        width (int): Figure width.
        height (int): Figure height.
        drop_na (bool): Drop NA rows before computing corr.
        tickangle (int): X-axis tick rotation.
        color_by_absolute (bool): 
            If True: color uses |corr| but cell text shows raw corr.
            If False: normal signed correlation heatmap.

    Returns:
        fig (plotly Figure or None)
        corr_matrix (pd.DataFrame)
    """

    # Validate columns
    missing = set(var_num) - set(df.columns)
    if missing:
        raise ValueError(f"Columns not found in DataFrame: {missing}")

    # Handle missing values
    sub_df = df[var_num]
    na_summary = sub_df.isna().sum()

    if na_summary.sum() > 0:
        if drop_na:
            sub_df = sub_df.dropna()
        else:
            all_na_cols = na_summary[na_summary == len(df)].index.tolist()
            if all_na_cols:
                raise ValueError(
                    f"Columns contain only NA values: {all_na_cols}"
                )

    # Compute correlation
    corr = sub_df.corr()
    corr_rounded = corr.round(round_decimals)

    if color_by_absolute:
        # --------------------------------------------
        # COLOR BY ABSOLUTE VALUE, TEXT IS RAW VALUE
        # --------------------------------------------
        # corr_abs = corr.abs()
        corr_abs = corr.abs().iloc[::-1, :]
        corr_rounded = corr_rounded.iloc[::-1, :]

        fig = go.Figure(
            data=go.Heatmap(
                z=corr_abs,
                text=corr_rounded,
                texttemplate="%{text}",
                colorscale=colorscale,
                colorbar_title="|Correlation|"
            )
        )

        fig.update_layout(
            title=title,
            width=width,
            height=height,
            xaxis=dict(
                tickmode='array',
                tickangle=tickangle,
                tickvals=list(range(len(corr.columns))),
                ticktext=corr_rounded.columns
            ),
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(corr.index))),
                ticktext=corr_rounded.index
            )
        )

    else:
        # --------------------------------------------
        # DEFAULT BEHAVIOR: COLOR BY SIGNED CORRELATION
        # --------------------------------------------
        fig = px.imshow(
            corr_rounded,
            text_auto=True,
            color_continuous_scale=colorscale,
            labels=dict(x="Variables", y="Variables", color="Correlation"),
            title=title
        )

        fig.update_layout(
            xaxis=dict(showticklabels=True, tickangle=tickangle),
            yaxis=dict(showticklabels=True),
            width=width,
            height=height
        )

    if show_fig:
        fig.show()
        return None, corr

    return fig, corr


# # ----------------------------------------------------
# # Bar|Box plot horizontal arrangement
# # ----------------------------------------------------

# import plotly.graph_objects as go
# from plotly.subplots import make_subplots

# def plot_bar_box_grouped(df, groupby_col, target_col):
#     categories = sorted(df[groupby_col].astype(str).unique())
    
#     fig = make_subplots(
#         rows=1,
#         cols=1,
#         specs=[[{"type": "xy"}]]
#     )

#     # Bar trace: count per category
#     counts = df.groupby(groupby_col).size().reindex(categories)
#     fig.add_trace(
#         go.Bar(
#             x=categories,
#             y=counts,
#             name="Count",
#             marker_color="steelblue",
#             yaxis="y1"
#         )
#     )

#     # Box trace: target_col per category
#     fig.add_trace(
#         go.Box(
#             x=df[groupby_col].astype(str),
#             y=df[target_col],
#             name=target_col,
#             marker_color="darkorange",
#             boxmean=True,
#             yaxis="y2"
#         )
#     )

#     fig.update_layout(
#         title=f"{groupby_col}: Count (left) and {target_col} (right)",
#         xaxis=dict(title=groupby_col, categoryorder="array", categoryarray=categories),
#         yaxis=dict(
#             title="Count",
#             side="left"
#         ),
#         yaxis2=dict(
#             title=target_col,
#             side="right",
#             overlaying="y",
#             anchor="x",
#             position=1.0
#         ),
#         barmode="group",
#         width=max(900, 80*len(categories)),
#         height=500
#     )

#     fig.show()

# ----------------------------------------------------
# Boxplot by group
# ----------------------------------------------------

import plotly.express as px
import pandas as pd

def boxplot_by_group(df, groupby_col, target_col):
    # Compute group sizes
    counts = df.groupby(groupby_col).size()
    df["_group_size"] = df[groupby_col].map(counts)

    # Sorted categories (alphabetical)
    sorted_categories = sorted(df[groupby_col].unique())

    # Create box plot
    fig = px.box(
        df,
        x=groupby_col,
        y=target_col,
        points="all"  # optional: show individual points
    )

    # Add group size to hover text while keeping default hover info
    fig.update_traces(
        hovertemplate=(            
            "Group size: %{customdata[0]}"
        ),
        customdata=df[["_group_size"]]
    )

    fig.update_layout(
        title=f"{target_col} distribution by {groupby_col}",
        xaxis=dict(
            title=groupby_col,
            categoryorder="array",
            categoryarray=sorted_categories   # alphabetical order
        ),
        yaxis_title=target_col,
        width=max(800, 60*df[groupby_col].nunique()),
        height=500
    )

    return fig

def boxplot_by_group_num(df, num_col, target_col, n_bins=10):

    # ---------------------------
    # Validate inputs
    # ---------------------------
    if (num_col is None) or (num_col not in df.columns):
        raise print(f"Error: num_col must be in df.columns, got {num_col}")
        return None

    if (target_col is None) or (target_col not in df.columns):
        raise print(f"Error: target_col must be in df.columns, got {target_col}")
        return None

    # ---------------------------
    # Add bin column and bin_code column
    # ---------------------------
    df[f'bin_{num_col}'] = pd.cut(df[num_col], bins=n_bins) 
    df[f'bin_{num_col}_code'] = df[f'bin_{num_col}'].cat.codes + 1 

    # ---------------------------
    # Draw the plot
    # ---------------------------
    fig = boxplot_by_group(df, f'bin_{num_col}_code', target_col)
    
    df_bin_info = df[[f'bin_{num_col}', f'bin_{num_col}_code']].drop_duplicates().sort_values(f'bin_{num_col}_code').reset_index(drop=True)

    # Create a configuration dictionary for the update
    axis_config = dict(       
        ticktext=df_bin_info[f'bin_{num_col}'].astype(str),  
        tickvals=df_bin_info[f'bin_{num_col}_code'],         
        tickangle=-45,    
    )

    # Use update_layout to apply changes to the specific axis name 
    axis_name = 'xaxis' 
    fig.update_layout({axis_name: axis_config}) 

    return fig