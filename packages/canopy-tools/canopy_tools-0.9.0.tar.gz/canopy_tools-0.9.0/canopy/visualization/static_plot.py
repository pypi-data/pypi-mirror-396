from typing import Optional, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm

import canopy as cp
from canopy.visualization.multiple_figs import setup_figure_and_axes, create_wrapper_from_locals
from canopy.visualization.plot_functions import get_color_palette, make_dark_mode, handle_figure_output, select_sites
import warnings

def make_static_plot(field_a: cp.Field, field_b: cp.Field, kind: Optional[str] = 'scatter', 
                     output_file: Optional[str] = None, layers: Optional[List[str] | str] = None,
                     field_a_label: Optional[str] = None, field_b_label: Optional[str] = None,
                     unit_a: Optional[str] = None, unit_b: Optional[str] = None,
                     sites: Optional[bool | List[tuple]] = False,
                     scatter_size: Optional[float] = 6, scatter_alpha: Optional[float] = 0.5,
                     title: Optional[str] = None, palette: Optional[str] = None,
                     custom_palette: Optional[str] = None, move_legend: Optional[bool] = False, 
                     dark_mode: Optional[bool] = False, transparent: Optional[bool] = False, 
                     x_fig: Optional[float] = 10, y_fig: Optional[float] = 10, 
                     subfig=None, return_fig: Optional[bool] = False, **kwargs) -> Optional[plt.Figure]:
    """
    This function generates a scatter plot with regression lines and r-scores, a histogram or a kde plot,
    comparing two input fields (which can be reduced spatially, temporally or both).

    Parameters
    ----------
    field_a, field_b : cp.Field
        Input data Field to display.
    kind : str, optional
        Kind of plot to draw. Default is 'scatter', which uses `seaborn.regplot` (supports multiple layers).
        Option 'hist' uses `seaborn.histplot` (supports multiple layers). 
        Option 'kde' uses `seaborn.kdeplot` (supports multiple layers).
    output_file : str, optional
        File path for saving the plot.
    layers : List[str] or str, optional
        Layers to plot from the input data.
    field_a_label, field_b_label : str, optional
        Labels for the data series, if not provided canopy will try to retrieve the name of the variable in the metadata.
    unit_a, unit_b : str, optional
        Units for the data series, if not provided canopy will try to retrieve the unit of the variable in the metadata.
    sites : bool or List[Tuple], optional
        Control site-level plotting instead of spatial reduction. Default is False. True = all sites,
        if provided with a list, only select the sites in the list.
    scatter_size : float, optional
        Marker size for scatter points. Default is 6.
    scatter_alpha : float, optional
        Transparency (alpha) for scatter points. Default is 0.5.
    title : str, optional
        Title of the plot.
    palette : str, optional
        Seaborn color palette to use for the line colors (https://seaborn.pydata.org/tutorial/color_palettes.html, 
        recommended palette are in https://colorbrewer2.org).
    custom_palette : str, optional
        Path of custom color palette .txt file to use. Names should match label names.
    move_legend : bool, optional
        Location of the legend ('in' or 'out'). Default is False.
    dark_mode : bool, optional
        Whether to apply dark mode styling to the plot.
    transparent : bool, optional
        If True, makes the background of the figure transparent.
    x_fig : float, optional
        Width of the figure in inches. Default is 10.
    y_fig : float, optional
        Height of the figure in inches. Default is 10.
    subfig : matplotlib.figure.SubFigure, optional
        If provided, the plot will be created in this subfigure instead of creating a new figure.
        This is used by multiple_figs() to combine multiple plots.
    return_fig : bool, optional
        If True, return a callable wrapper function instead of creating the plot immediately.
        This wrapper can be used with multiple_figs(). Default is False.
    **kwargs
        Additional keyword arguments are passed directly to `seaborn.regplot` (if `kind='scatter'`)
        or `seaborn.histplot` (if `kind='hist'`). This allows customization of plot features.
    """
    # If return_fig is True, create a wrapper function and return it
    if return_fig:
        return create_wrapper_from_locals(make_static_plot, locals())

    # Check for some initial conditions
    if layers and sites:
        raise ValueError("layers and sites argument cannot be used simultanuously. Only one layer for multiple sites.")

    # Force variables to be a list
    if isinstance(layers, str):
        layers = [layers]
    if not isinstance(sites, bool) and not isinstance(sites, list):
        sites = [sites]

    # Retrieve metadata
    field_a_label = field_a_label or field_a.metadata['name']
    field_b_label = field_b_label or field_b.metadata['name']
    unit_a = field_a.metadata['units'] if unit_a is None else unit_a
    unit_b = field_b.metadata['units'] if unit_b is None else unit_b
    layers = layers or field_a.layers

    df_a = cp.make_lines(field_a)
    df_b = cp.make_lines(field_b)

    if sites: # If sites, flatten data
        df_a = select_sites(df_a, sites)
        df_b = select_sites(df_b, sites)
        layers = df_a.columns

    # Prepare axis labels (used by both paths)
    xlabel = f"{field_a_label} (in {unit_a})" if unit_a != "[no units]" else field_a_label
    ylabel = f"{field_b_label} (in {unit_b})" if unit_b != "[no units]" else field_b_label

    # Set up the figure and axes
    fig, ax = setup_figure_and_axes(subfig=subfig, x_fig=x_fig, y_fig=y_fig)

    # Colour palette
    colors, _ = get_color_palette(len(layers), palette=palette, custom_palette=custom_palette)

    # Filter kwargs to remove subfig
    filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'subfig'}
    
    # Initialize axis limits
    min_val = np.inf
    max_val = -np.inf

    # Loop through layers
    for i, layer in enumerate(tqdm(layers, desc="Processing layers")):
        # Align the data to handle multiple layers
        x1d, y1d = _to_aligned_1d(df_a[layer], df_b[layer])
        if len(x1d) < 2:
            warnings.warn(f"Skipping {layer}: insufficient valid data")
            continue

        # Track axis limits
        layer_min = min(x1d.min(), y1d.min())
        layer_max = max(x1d.max(), y1d.max())
        min_val = min(min_val, layer_min)
        max_val = max(max_val, layer_max)

        color = colors[i]   # from get_color_palette (already computed above)

        plot_kwargs = {"x": x1d, "y": y1d, "ax": ax, "color": color}

        if kind == 'scatter':
            # Calculate R-squared
            r_val = np.corrcoef(x1d.values, y1d.values)[0, 1]

            # Add label to plot and scatter kwargs
            plot_kwargs["label"] = f"{layer} (R={r_val:.2f})"
            plot_kwargs["scatter_kws"] = {"s": scatter_size, "alpha": scatter_alpha}
            
            plot_kwargs.update(filtered_kwargs)
            sns.regplot(**plot_kwargs)

        elif kind == 'hist':
            plot_kwargs.update(filtered_kwargs)
            sns.histplot(**plot_kwargs)

        elif kind == 'kde':
            plot_kwargs.update(filtered_kwargs)
            sns.kdeplot(**plot_kwargs)

        else:
            raise ValueError(f"Unsupported kind: {kind}, must be 'scatter', 'hist' or 'kde'.")
    
    # Annotate counts for histograms 
    if kind == "hist":
        _annotate_hist_counts(ax)
    
    # Create legend for hist/kde
    if kind in ("hist", "kde"):
        from matplotlib.patches import Patch
        handles = [
            Patch(facecolor=colors[i], edgecolor="none", label=f"{layer}")
            for i, layer in enumerate(layers)
        ]
        ax.legend(handles=handles, loc="best", frameon=False, fontsize=14)
    
    # Legend options
    if kind == "scatter":
        leg = ax.legend(loc='best', frameon=False, fontsize=14)
    else:
        leg = ax.get_legend()
    
    # Set alpha on handles before moving legend
    if leg is not None:
        for handle in leg.legend_handles:
            if hasattr(handle, 'set_alpha'):
                handle.set_alpha(1.0)
    
    if move_legend:
        sns.move_legend(ax, "center left", bbox_to_anchor=(1, 0.95))
        # Get the legend again after moving (move_legend creates a new legend)
        leg = ax.get_legend()
    
    # Handle axis limits, labels and title
    ax.set_xlim([min_val, max_val])
    if kind == 'scatter':
        ax.set_ylim([min_val, max_val])
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    if title:
        ax.set_title(title, fontsize=18)
    
    # Remove the top and right spines
    sns.despine(ax=ax)

    # Apply dark mode if requested
    if dark_mode:
        fig, ax = make_dark_mode(fig, ax, legend_style=None)
    
    # Adjust figure layout to accommodate moved legend (only for standalone figures)
    if move_legend and subfig is None:
        fig.tight_layout()

    return handle_figure_output(fig, output_file=output_file, transparent=transparent, subfig=subfig)

def _to_aligned_1d(x_obj, y_obj):
    """
    Return pairwise-valid, aligned 1D Series for x and y (handles Series/DataFrame)
    """
    # Stack the data to handle multiple layers
    xs = x_obj.stack(future_stack=True) if isinstance(x_obj, pd.DataFrame) else x_obj
    ys = y_obj.stack(future_stack=True) if isinstance(y_obj, pd.DataFrame) else y_obj
    xs, ys = xs.align(ys, join='inner')

    # Unstack the data to handle multiple layers
    if isinstance(xs, pd.DataFrame):
        xs = xs.stack(future_stack=True)
    if isinstance(ys, pd.DataFrame):
        ys = ys.stack(future_stack=True)

    # Get valid data
    valid = xs.notna() & ys.notna()

    # Convert to numpy arrays
    if isinstance(valid, pd.DataFrame):
        valid = valid.to_numpy().ravel()
        xs = pd.Series(xs.to_numpy().ravel())
        ys = pd.Series(ys.to_numpy().ravel())
        
    return xs[valid], ys[valid]

def _annotate_hist_counts(ax):
    """
    Annotate each rectangle in a histogram plot with the count of points in that bin.
    """
    # Process all collections (seaborn histplot uses collections for 2D histograms)
    for collection in ax.collections:
        # Get array/data from collection
        try:
            array = collection.get_array()
        except:
            continue
        
        # Get paths from collection
        try:
            paths = collection.get_paths()
        except:
            continue
        
        if array is None or len(paths) == 0:
            continue
        
        # Get the array values (counts)
        counts = array.data if hasattr(array, 'data') else array
        if counts is None:
            continue
        
        # Convert to numpy array and flatten for easier indexing
        counts = np.asarray(counts).flatten()
        
        # Find max count for text color threshold
        valid_counts = counts[~np.isnan(counts) & (counts > 0)]
        if len(valid_counts) == 0:
            continue
        max_count = np.max(valid_counts)
        
        # Annotate each path (rectangle/polygon)
        for idx, path in enumerate(paths):
            if idx >= len(counts):
                break
            
            count = counts[idx]
            if count <= 0 or np.isnan(count):
                continue
            
            # Get the center of the shape from the path
            vertices = path.vertices
            if len(vertices) == 0:
                continue
            
            x_center = np.mean(vertices[:, 0])
            y_center = np.mean(vertices[:, 1])
            
            # Use white text for bins with counts above 50% of max
            text_color = 'white' if count > max_count * 0.5 else 'black'
            
            # Add text annotation
            ax.text(x_center, y_center, f'{int(count)}',
                    ha='center', va='center', fontsize=8,
                    color=text_color, weight='bold')
