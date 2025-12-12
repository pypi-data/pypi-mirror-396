import warnings
from typing import Optional, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import canopy as cp
from canopy.visualization.multiple_figs import setup_figure_and_axes, create_wrapper_from_locals
from canopy.visualization.plot_functions import get_color_palette, make_dark_mode, handle_figure_output, select_sites

def make_distribution_plot(fields: cp.Field | List[cp.Field], output_file: Optional[str] = None,
                           plot_type: Optional[str] = "box", layers: Optional[List[str] | str] = None,
                           gridop: Optional[str] = None, sites: Optional[bool | List[tuple]] = False,
                           yaxis_label: Optional[str] = None, field_labels: Optional[List[str]] = None,
                           unit: Optional[List[str]] = None, title: Optional[str] = None, 
                           palette: Optional[str] = None, custom_palette: Optional[List[str]] = None, 
                           horizontal: Optional[bool] = False, vertical_xlabels: Optional[bool] = False, 
                           dark_mode: bool = False, transparent: bool = False, 
                           x_fig: float = 10, y_fig: float = 10, subfig=None, 
                           return_fig: Optional[bool] = False, **kwargs) -> Optional[plt.Figure]:
    """
    Create a comparative plot from a list of input data Fields from, for example, different runs. 
    The functions can generate boxplot, strip or swarm plot, violin plot, boxen plot, point plot, 
    bar plot or count plot based on the `plot_type` parameter.

    Parameters
    ----------
    fields : cp.Field or List[cp.Field]
        Input data Field to display.
    output_file : str, optional
        File path for saving the plot.
    plot_type: str, optional
        Type of plot. Either "strip", "swarm", "box", "violin", "boxen", "point", or "bar"
    layers : List[str] or str, optional
        List of layer names to display.
    gridop : str, optional
        If provided, the grid reduction operation. Either None, 'sum' or 'av'. Default is None.
    sites : bool or List[Tuple], optional
        Control site-level plotting instead of spatial reduction. Default is False. True = all sites,
        if provided with a list, only select the sites in the list.
    yaxis_label : str, optional
        Y-axis label, if not provided canopy will try to retrieve the name of the variable in the metadata.
    field_labels : List[str], optional
        Names of each series to display in the legend.
    unit : List[str], optional
        Unit of the y-axis variable, if not provided canopy will try to retrieve the unit of the variable in the metadata.
    title : str, optional
        Title of the plot.
    palette : str, optional
        Seaborn color palette to use for the line colors (https://seaborn.pydata.org/tutorial/color_palettes.html, 
        recommended palette are in https://colorbrewer2.org).
    custom_palette : List[str], optional
        Path of custom color palette .txt file to use. Names should match label names.
    horizontal : bool, optional
        If True, renders the plot with horizontal orientation (flips the axes).
    vertical_xlabels : bool, optional
        If True, rotates the x-axis tick labels vertically (i.e., 90 degrees).
    dark_mode : bool, optional
        If True, applies dark mode styling to the figure. Default is False.
    transparent : bool, optional
        If True, sets the figure background to be transparent when saved. Default is False.
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
        Additional keyword arguments are passed directly to `seaborn.catplot`. 
        This allows customization of plot features such as `aspect`, `errorbar`, height`, etc.
    """
    # If return_fig is True, create a wrapper function and return it
    if return_fig:
        return create_wrapper_from_locals(make_distribution_plot, locals())
    
    # Check for some initial conditions
    if layers and sites:
        raise ValueError("layers and sites argument cannot be used simultanuously. Only one layer for multiple sites.")
    if plot_type == "count":
        raise ValueError("count plot is not supported for distribution plot.")
    if gridop is not None and sites is not False:
        warnings.warn("If gridop is selected, sites won't have an effect because the space is going to be reduced anyway.", UserWarning)
        sites = False

    # Force variables to be a list
    if not isinstance(fields, list):
        fields = [fields]
    if isinstance(layers, str):
        layers = [layers]
    if sites is not None and sites is not False and not isinstance(sites, bool) and not isinstance(sites, list):
        sites = [sites]

    # Retrieve metadata
    yaxis_label = yaxis_label or str(fields[0].metadata.get('name', ''))
    # Normalize unit to string (function signature allows List[str] but we use it as string)
    if unit is None:
        unit_str = str(fields[0].metadata.get('units', ''))
    elif isinstance(unit, list):
        unit_str = unit[0] if unit else ""
    else:
        unit_str = unit
    layers = layers or fields[0].layers

    # Check valid labels
    if len(fields) > 1 and field_labels is None:
            raise ValueError("field_labels must be defined when there are more than one field.")
    
    # If only one field and no field_labels provided, don't use label
    if len(fields) == 1 and field_labels is None:
        field_labels = [" "]

    # Convert all series to DataFrames with flattened structure
    combined_data = []
    gridop_str = gridop or 'av'  # Ensure gridop is not None
    field_labels_list = field_labels or []  # Ensure field_labels is not None
    for i, field in enumerate(fields):
        label = field_labels_list[i] if i < len(field_labels_list) else f"Field {i+1}"
        if gridop: # Reduce grid if gridop is provided
            field_red = field.red_space(gridop_str)
            field_to_use = field_red if field_red is not None else field
        else:
            field_to_use = field
        df = cp.make_lines(field_to_use)

        if sites: # If sites, flatten data
            df = select_sites(df, sites=sites)
            layers = list(df.columns) # Update layers

        for layer in layers:
            values = df[layer].values
            # Handle both ExtensionArray and ndarray
            if hasattr(values, 'flatten'):
                data = values.flatten()
            else:
                data = np.asarray(values).flatten()
            combined_data.append(pd.DataFrame({
                "value": data,
                "series": label,
                "layer": layer
            }))

    df_long = pd.concat(combined_data, ignore_index=True)

    # Get color palette - one color per field/series (not per layer)
    n_classes = len(field_labels_list)
    colors, color_dict = get_color_palette(n_classes=n_classes, palette=palette, custom_palette=custom_palette)
    palette_dict = {label: color for label, color in zip(field_labels_list, colors)}

    # Set axes depending on orientation
    x, y = ("value", "layer") if horizontal else ("layer", "value")

    # Create figure and axis
    fig, ax = setup_figure_and_axes(subfig=subfig, x_fig=x_fig, y_fig=y_fig)

    # Base arguments for seaborn plotting functions
    plot_kwargs = {
        "data": df_long,
        "x": x,
        "y": y,
        "hue": "series",
        "palette": palette_dict if palette_dict else palette,
        "ax": ax
    }

    # Update with user-provided kwargs, but remove subfig if present
    plot_kwargs.update({k: v for k, v in kwargs.items() if k != 'subfig'})

    # Recommended arguments
    if plot_type == "box" or plot_type == "boxen":
        plot_kwargs["fill"] = False
        plot_kwargs["showfliers"] = False
        plot_kwargs["gap"] = 0.1
    if plot_type == "violin":
        plot_kwargs["inner"] = None
        plot_kwargs["bw_method"] = 1
        if len(fields) == 2:
            plot_kwargs["split"] = True

    # Use the underlying plotting function based on plot_type
    with warnings.catch_warnings():
        # Suppress deprecation warning about 'vert'
        warnings.filterwarnings("ignore", category=PendingDeprecationWarning, message=".*vert.*")
        if plot_type == "box":
            ax = sns.boxplot(**plot_kwargs)
        elif plot_type == "violin":
            ax = sns.violinplot(**plot_kwargs)
        elif plot_type == "boxen":
            ax = sns.boxenplot(**plot_kwargs)
        elif plot_type == "strip":
            ax = sns.stripplot(**plot_kwargs)
        elif plot_type == "swarm":
            ax = sns.swarmplot(**plot_kwargs)
        elif plot_type == "point":
            ax = sns.pointplot(**plot_kwargs)
        elif plot_type == "bar":
            ax = sns.barplot(**plot_kwargs)
        else:
            raise ValueError(f"Unsupported plot_type: {plot_type}")

    # Set labels and title
    axis_label = f"{yaxis_label} (in {unit_str})" if unit_str and unit_str != "[no units]" else (yaxis_label or "")
    if horizontal:
        ax.set_xlabel(axis_label, fontsize=16)
        ax.set_ylabel("")
    else:
        ax.set_ylabel(axis_label, fontsize=16)
        ax.set_xlabel("")

    ax.tick_params(labelsize=14)
    if title:
        ax.set_title(title, fontsize=16)
    
    # Remove the top and right spines
    sns.despine(ax=ax)

    # Rotate labels if requested to prevent overlap
    if vertical_xlabels:
        if horizontal:
            # When horizontal, rotate y-axis labels (which show the layer names)
            plt.setp(ax.get_yticklabels(), rotation=90, ha='center')
        else:
            # When vertical, rotate x-axis labels (which show the layer names)
            plt.setp(ax.get_xticklabels(), rotation=90, ha='right')

    # Custom legend (colored labels, no box)
    handles, labels = ax.get_legend_handles_labels()
    if labels and palette_dict:
        ax.legend(handles=[plt.Line2D([], [], color=palette_dict.get(label, 'black'), marker='', linestyle='') for label in labels],
                  labels=labels, handlelength=0, handletextpad=0, labelcolor=[palette_dict.get(label, 'black') for label in labels],
                  loc='best', frameon=False, fontsize=14)

    # Apply dark mode
    if dark_mode:
        fig, ax = make_dark_mode(fig, ax)

    return handle_figure_output(fig, output_file=output_file, transparent=transparent, subfig=subfig)
