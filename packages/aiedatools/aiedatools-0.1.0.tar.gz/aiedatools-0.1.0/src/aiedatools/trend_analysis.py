import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_trend(df, groupby_col, metrics_dict={}, 
    grouped_bar_chart=True, 
    title="Bar Plot"):
    """
    Flexible grouped bar plotting function.
    
    Parameters
    ----------
    df : pd.DataFrame
    groupby_col : str
        Column to group by. Must exist in df.columns.
    metrics_dict : dict
        Dictionary {target_col: metric}, where metric can be string ('mean', 'count', etc.) or callable.
        If None or empty, default to count of groupby_col.
    grouped_bar_chart : bool
        Whether to draw side-by-side grouped bar if metrics_dict has two items.
    title : str
        Plot title.
        
    Returns
    -------
    fig : plotly.graph_objects.Figure
    """
       
    # ---------------------------
    # Validate inputs
    # ---------------------------
    if (groupby_col is None) or (groupby_col not in df.columns):
        raise print(f"Error: groupby_col must be in df.columns, got {groupby_col}")
        return None
    
    if (metrics_dict is not None) and (len(metrics_dict) > 0):
        len0 = len(metrics_dict)
        # Filter metrics_dict to only include columns that exist
        metrics_dict = {k: v for k, v in metrics_dict.items() if k in df.columns}
        len1 = len(metrics_dict)
        if len1 < len0:
            print(f"Note: {len0 - len1} target columns are not in the columns of the given dataframe!")

    if (metrics_dict is None) or (len(metrics_dict) == 0):
        # Default: count per group
        grouped = df.groupby(groupby_col).size()
        fig = go.Figure(
            go.Bar(x=grouped.index, y=grouped.values, text=grouped.values, textposition="auto",
                hovertemplate="""
                Group: %{x}<br>
                Value: %{y}<br>
                <extra></extra>
                """)
        )
        fig.update_layout(title=title, yaxis_title="Count")
        return fig    
    
    
    grouped = df.groupby(groupby_col)
    grouped_size = grouped[groupby_col].size()
    
    # ---------------------------
    # Single metric
    # ---------------------------
    if len(metrics_dict) == 1:
        target_col, metric = list(metrics_dict.items())[0]
        # Compute value per group
        if isinstance(metric, str):
            y_vals = getattr(grouped[target_col], metric)()
        elif callable(metric):
            y_vals = grouped[target_col].apply(metric)
        else:
            raise TypeError("Metric must be str or callable")
        
        y_vals = y_vals.round(2)  # round

        fig = go.Figure(
            go.Bar(x=y_vals.index, y=y_vals.values, text=y_vals.values, textposition="auto",
                customdata=grouped_size.values, 
                hovertemplate="""
                Group: %{x}<br>
                Value: %{y}<br>
                Size: %{customdata}<br>
                <extra></extra>
                """
                )
        )
        fig.update_layout(title=title, yaxis_title=f"{metric}({target_col})")
        return fig
    
    

    # ---------------------------
    # Case 3: Two metrics → grouped bar + dual axes
    # ---------------------------
    elif (len(metrics_dict) == 2) and (grouped_bar_chart is True):
        (col1, met1), (col2, met2) = metrics_dict.items()

        # Compute metric 1
        if isinstance(met1, str):
            y1 = getattr(grouped[col1], met1)()
        else:
            y1 = grouped[col1].apply(met1)

        # Compute metric 2
        if isinstance(met2, str):
            y2 = getattr(grouped[col2], met2)()
        else:
            y2 = grouped[col2].apply(met2)

        y1 = y1.round(2)
        y2 = y2.round(2)

        fig = go.Figure()

        # FIRST BAR GROUP
        fig.add_trace(
            go.Bar(
                x=y1.index,
                y=y1.values,
                name=f"{met1}({col1})",
                text=y1.values,
                textposition="auto",
                offsetgroup="group1",      # <<< REQUIRED
                legendgroup="group1",                
                customdata=grouped_size.values, 
                hovertemplate="""
                Group: %{x}<br>
                Value: %{y}<br>
                Size: %{customdata}<br>
                <extra></extra>
                """
            )
        )

        # SECOND BAR GROUP
        fig.add_trace(
            go.Bar(
                x=y2.index,
                y=y2.values,
                name=f"{met2}({col2})",
                yaxis="y2",
                text=y2.values,
                textposition="auto",
                offsetgroup="group2",      # <<< REQUIRED
                legendgroup="group2",                
                customdata=grouped_size.values, 
                hovertemplate="""
                Group: %{x}<br>
                Value: %{y}<br>
                Size: %{customdata}<br>
                <extra></extra>
                """
            )
        )

        fig.update_layout(
            title=title,
            barmode='group',               # <<< important
            yaxis=dict(title=f"{met1}({col1})"),
            yaxis2=dict(
                title=f"{met2}({col2})",
                overlaying='y',
                side='right'
            )
        )

        fig.update_layout(
            margin=dict(
                l=60,   # left margin
                r=100,   # right margin (increased)
                t=60,   # title
                b=60    # x-axis tick labels
            )
        )

        return fig
    
    # ---------------------------
    # More than 2 metrics OR grouped_bar_chart=False
    # Vertical stacked subplots
    # ---------------------------
    elif (len(metrics_dict) >= 2) or (grouped_bar_chart is False):

        n = len(metrics_dict)
        # Reverse order so first metric goes to the bottom subplot
        items = list(metrics_dict.items())[::-1]

        fig = make_subplots(rows=n, cols=1, shared_xaxes=True, vertical_spacing=0.15,
                            subplot_titles=[f"{metric}({col})" for col, metric in items],
                            row_heights=[1]*n )
        
        for i, (col, metric) in enumerate(items, start=1):
            if isinstance(metric, str):
                y_vals = getattr(grouped[col], metric)()
            else:
                y_vals = grouped[col].apply(metric)
                
            y_vals = y_vals.round(2)

            fig.add_trace(
                go.Bar(x=y_vals.index, y=y_vals.values, text=y_vals.values, textposition="auto",
                    customdata=grouped_size.values, 
                    hovertemplate="""
                    Group: %{x}<br>
                    Value: %{y}<br>
                    Size: %{customdata}<br>
                    <extra></extra>
                    """),
                row=i, col=1
            )
        
        fig.update_layout(height=250*n, title=title)
        return fig

def plot_trend_num(df, num_col, n_bins=20, metrics_dict={},
    grouped_bar_chart=True, 
    title="Bar Plot"):

    # ---------------------------
    # Validate inputs
    # ---------------------------
    if (num_col is None) or (num_col not in df.columns):
        raise print(f"Error: groupby_col must be in df.columns, got {num_col}")
        return None

    # ---------------------------
    # Add bin column and bin_code column
    # ---------------------------
    df[f'bin_{num_col}'] = pd.cut(df[num_col], bins=n_bins) 
    df[f'bin_{num_col}_code'] = df[f'bin_{num_col}'].cat.codes + 1 

    # ---------------------------
    # Draw the plot
    # ---------------------------
    fig = plot_trend(df, f'bin_{num_col}_code', 
            metrics_dict=metrics_dict,
            grouped_bar_chart=grouped_bar_chart, 
            title=title)
    
    df_bin_info = df[[f'bin_{num_col}', f'bin_{num_col}_code']].drop_duplicates().sort_values(f'bin_{num_col}_code').reset_index(drop=True)

    # Determine the total number of subplots/traces in the figure
    num_subplots = len(fig.data) 

    # # Determine the internal name of the last x-axis  
    # if (num_subplots == 2) and (grouped_bar_chart is True):
    #     axis_name = 'xaxis'
    # else:   
    #     axis_name = f'xaxis{num_subplots}' if num_subplots > 1 else 'xaxis'
    # print(f"axis_name is {axis_name}")

    # Create a configuration dictionary for the update
    axis_config = dict(       
        ticktext=df_bin_info[f'bin_{num_col}'].astype(str),  
        tickvals=df_bin_info[f'bin_{num_col}_code'],         
        tickangle=-45,    
    )

    # Use update_layout to apply changes to the specific dynamic axis name  
    for i in range(1, num_subplots+1):
        if i==1:
            axis_name = 'xaxis'  
        else:
            axis_name = f'xaxis{i}'

        fig.update_layout({axis_name: axis_config}) 

    return fig
    
