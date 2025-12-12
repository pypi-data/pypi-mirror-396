import warnings
from typing import Optional, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import canopy as cp
from canopy.visualization.multiple_figs import setup_figure_and_axes, create_wrapper_from_locals
from canopy.visualization.plot_functions import handle_figure_output, get_color_palette, make_dark_mode
from canopy.visualization.time_series import _apply_legend_style

def make_latitudinal_plot(fields: cp.Field | List[cp.Field], output_file: Optional[str] = None,
                          layers: Optional[List[str] | str] = None, yaxis_label: Optional[str] = None,
                          field_labels: Optional[List[str]] = None, unit: Optional[str] = None,
                          title: Optional[str] = None, palette: Optional[str] = None,
                          custom_palette: Optional[str] = None, move_legend: Optional[bool] = False,
                          legend_style: Optional[str] = 'default', max_labels_per_col: Optional[int] = 15,
                          dark_mode: Optional[bool] = False, transparent: Optional[bool] = False,
                          x_fig: Optional[float] = 10, y_fig: Optional[float] = 10, subfig=None,
                          return_fig: Optional[bool] = False, **kwargs) -> Optional[plt.Figure]:
    """
    Create a latitudinal plot showing variable values as a function of latitude.
    The plot displays mean values averaged over time at each latitude.

    Parameters
    ----------
    fields : cp.Field or List[cp.Field]
        Input data Field or list of Fields to display.
    output_file : str, optional
        File path for saving the plot.
    layers : List[str] or str, optional
        List of layer names to display. If None, all layers from the first field are used.
    yaxis_label : str, optional
        Y-axis label, if not provided canopy will try to retrieve the name of the variable
        in the metadata.
    field_labels : List[str], optional
        List of labels for each field when multiple fields are provided. Required when
        multiple fields are used.
    unit : str, optional
        Unit of the variable, if not provided canopy will try to retrieve the unit of
        the variable in the metadata.
    title : str, optional
        Title of the plot.
    palette : str, optional
        Seaborn color palette to use for the line colors
        (https://seaborn.pydata.org/tutorial/color_palettes.html,
        recommended palette are in https://colorbrewer2.org).
    custom_palette : str, optional
        Path of custom color palette .txt file to use. Names should match label names.
    move_legend : bool, optional
        Move the legend outside of plot. Default is False.
    legend_style : str, optional
        Style of the legend ('default', 'highlighted', 'end-of-line', 'hidden').
        If 'hidden', the legend will not be shown. Default is 'default'.
    max_labels_per_col : int, optional
        Maximum number of labels per column in the legend. Default is 15.
    dark_mode : bool, optional
        If True, apply dark mode styling. Default is False.
    transparent : bool, optional
        If True, make the figure transparent. Default is False.
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
        Additional keyword arguments are passed directly to `seaborn.lineplot`. This allows
        customization of line aesthetics such as `linewidth`, `linestyle`, `alpha`, etc.
    """
    # If return_fig is True, create a wrapper function and return it
    if return_fig:
        return create_wrapper_from_locals(make_latitudinal_plot, locals())
    
    # Force variables to be a list
    if not isinstance(fields, list):
        fields = [fields]
    if isinstance(layers, str):
        layers = [layers]
    
    # Retrieve metadata
    yaxis_label = yaxis_label or str(fields[0].metadata.get('name', ''))
    unit = unit or str(fields[0].metadata.get('units', ''))
    layers = layers or fields[0].layers
    
    # Calculate latitude range from the first field's grid
    # If multiple fields, use the union of all latitude ranges
    lat_mins = []
    lat_maxs = []
    for field in fields:
        if hasattr(field.grid, 'lat_min') and hasattr(field.grid, 'lat_max'):
            if not field.grid.is_reduced('lat'):
                lat_mins.append(field.grid.lat_min)
                lat_maxs.append(field.grid.lat_max)
    
    if lat_mins and lat_maxs:
        lat_range = [min(lat_mins), max(lat_maxs)]
    else:
        # Fallback if grid doesn't have lat_min/lat_max
        lat_range = [-90, 90]
    
    # Check valid labels
    if len(fields) > 1 and field_labels is None:
        raise ValueError("field_labels must be defined when there are more than one field.")
    if len(fields) > 1 and field_labels is not None and len(field_labels) != len(fields):
        raise ValueError("field_labels should be of the same size as the number of fields.")
    
    # Check that the selected layers exist in all fields
    if len(fields) > 1:
        layers_set = set(layers) if isinstance(layers, list) else {layers}
        for i, field in enumerate(fields):
            field_layers = set(field.layers)
            missing_layers = layers_set - field_layers
            if missing_layers:
                raise ValueError(
                    f'Field {i} is missing the following selected layer(s): {missing_layers}. '
                    'Tip: use field.rename_layers() method or select layers that exist in all fields.'
                )
    
    # Process each field: reduce along longitude, then calculate mean over time for each latitude
    combined_data = []
    field_labels_list = field_labels or []
    
    for i, field in enumerate(fields):
        label = field_labels_list[i] if i < len(field_labels_list) else f"Field {i+1}"
        
        # Reduce along longitude to get data organized by (lat, time)
        if not field.grid.is_reduced('lon'):
            field_lon_red = field.red_space('av', axis='lon')
            if field_lon_red is None:
                field_lon_red = field
        else:
            field_lon_red = field
        
        # Process each layer
        for layer in layers:
            if layer not in field_lon_red.layers:
                warnings.warn(f"Layer '{layer}' not found in field {i}, skipping.", UserWarning)
                continue
            
            # Get data for this layer
            data = field_lon_red.data[layer]
            
            # Group by latitude and calculate mean over time
            if isinstance(data.index, pd.MultiIndex):
                # Find latitude level
                if 'lat' in data.index.names:
                    lat_level = 'lat'
                else:
                    # Find the numeric level (should be latitude)
                    for level_name in data.index.names:
                        if level_name != 'time':
                            lat_level = level_name
                            break
                    else:
                        raise ValueError("Could not find latitude level in index")
                
                # Group by latitude and calculate mean
                grouped = data.groupby(level=lat_level).mean()
                
                # Get latitudes and values
                latitudes = grouped.index.values
                values = grouped.values
            else:
                # Single level index
                latitudes = data.index.values
                values = data.values
            
            # Convert to float and filter by latitude range
            latitudes_float = pd.to_numeric(latitudes, errors='coerce')
            mask = (latitudes_float >= lat_range[0]) & (latitudes_float <= lat_range[1])
            latitudes_filtered = latitudes_float[mask]
            values_filtered = values[mask]
            
            # Store mean values for each latitude
            for lat, val in zip(latitudes_filtered, values_filtered):
                if not np.isnan(lat) and not np.isnan(val):
                    combined_data.append({
                        "latitude": float(lat),
                        "value": float(val),
                        "field_label": label,
                        "layer": layer
                    })
    
    if not combined_data:
        raise ValueError("No valid data found for plotting.")
    
    df_long = pd.DataFrame(combined_data)
    
    # Create figure and axis
    fig, ax = setup_figure_and_axes(subfig=subfig, x_fig=x_fig, y_fig=y_fig)
    
    # Determine hue and style based on number of fields and layers
    is_single_field = len(fields) == 1
    is_single_layer = isinstance(layers, str) or (isinstance(layers, list) and len(layers) == 1)
    
    # Determine number of classes for color palette based on what will be used for hue
    if is_single_field and is_single_layer:
        n_classes = 1
    elif is_single_field and not is_single_layer:
        n_classes = len(layers)
    elif not is_single_field and is_single_layer:
        n_classes = len(fields)
    else:
        # Multiple fields and multiple layers: hue='field_label', style='layer'
        n_classes = len(fields)
    
    # Get color palette
    colors, palette_dict = get_color_palette(n_classes, palette=palette, custom_palette=custom_palette)
    
    # Base arguments for seaborn lineplot
    # Use x=latitude, y=value so seaborn groups by latitude and calculates stats for value
    plot_kwargs = {
        "data": df_long,
        "x": "latitude",  # Group by latitude
        "y": "value",     # Calculate statistics for value
        "ax": ax,
    }
    
    # Set hue and style based on conditions
    if is_single_field and is_single_layer:
        plot_kwargs["hue"] = None
        plot_kwargs["style"] = None
        plot_kwargs["legend"] = False  # No legend needed for single field/layer
    elif is_single_field and not is_single_layer:
        plot_kwargs["hue"] = "layer"
        plot_kwargs["style"] = None
        plot_kwargs["legend"] = bool(legend_style)
        plot_kwargs["palette"] = colors
    elif not is_single_field and is_single_layer:
        plot_kwargs["hue"] = "field_label"
        plot_kwargs["style"] = None
        plot_kwargs["legend"] = bool(legend_style)
        plot_kwargs["palette"] = colors
    else:
        plot_kwargs["hue"] = "field_label"
        plot_kwargs["style"] = "layer"
        plot_kwargs["legend"] = bool(legend_style)
        plot_kwargs["palette"] = colors
    
    # Update with user-provided kwargs, but remove subfig if present
    plot_kwargs.update({k: v for k, v in kwargs.items() if k != 'subfig'})
    
    # Plot using seaborn lineplot (this plots with latitude on x, value on y)
    sns.lineplot(**plot_kwargs)
    
    # Swap axes to get desired orientation: value on x, latitude on y
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    ax.set_xlim(ylim)
    ax.set_ylim(xlim)
    
    # Swap line data
    for line in ax.get_lines():
        x_data = line.get_xdata()
        y_data = line.get_ydata()
        line.set_data(y_data, x_data)
    
    # Apply the legend style (only if legend was requested and there are labels)
    if not (is_single_field and is_single_layer):
        _apply_legend_style(ax, legend_style, max_labels_per_col, move_legend)
    
    # Set axis labels
    xlabel = f"{yaxis_label} (in {unit})" if unit and unit != "[no units]" else (yaxis_label or "Value")
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel("Latitude", fontsize=16)
    ax.tick_params(labelsize=14)
    
    if title:
        ax.set_title(title, fontsize=18, pad=20)
    
    # Remove the top and right spines
    sns.despine(ax=ax)
    
    # Apply dark mode if requested
    if dark_mode:
        fig, ax = make_dark_mode(fig, ax)
    
    return handle_figure_output(fig, output_file=output_file, transparent=transparent, subfig=subfig)
