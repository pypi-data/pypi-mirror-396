import os
import warnings
from typing import Union, Optional, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

def select_sites(data: Union[pd.DataFrame, List[Tuple[float, float]]], 
                 sites: Union[bool, List[Tuple[float, float]]] = True) -> pd.DataFrame:
    """
    Select and reorder columns of a DataFrame according to requested sites.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    
    if sites is True:
        # Keep all columns
        df = data.copy()
        df.columns = [f"{c[1]}, {c[2]}" for c in df.columns]
        return df
    
    elif isinstance(sites, list):
        ordered_cols = []
        for lon, lat in sites:
            cols = [c for c in data.columns if np.isclose(c[1], float(lon)) and np.isclose(c[2], float(lat))]
            if not cols:
                raise ValueError(f"Requested site ({lon}, {lat}) not found in data.")
            ordered_cols.extend(cols)
        
        df = data[ordered_cols].copy()
        df.columns = [f"{c[1]}, {c[2]}" for c in ordered_cols]
        return df
    
    raise ValueError("sites must be True or a list of (lon, lat) tuples")

def handle_figure_output(fig, output_file=None, transparent=False, subfig=None):
    """
    Figure handler: save or show.
    """
    # If subfig was provided, the plot is already in the parent figure, so return None
    if subfig is not None:
        return None
    
    if output_file:
        # Only use bbox_inches='tight' if nothing is out of bounds
        if _has_out_of_bounds_artists(fig):
            save_figure_png(output_file, bbox_inches=None, transparent=transparent)
        else:
            save_figure_png(output_file, bbox_inches='tight', transparent=transparent)
        plt.close()
    else:
        plt.show()
    
    return fig if output_file is None else None

def _has_out_of_bounds_artists(fig):
    # Handle Seaborn FacetGrid/PairGrid
    if hasattr(fig, "axes"):
        axes = fig.axes
        # FacetGrid.axes is a numpy array, flatten it
        if hasattr(axes, "flat"):
            axes = axes.flat
    # Handle matplotlib Figure
    elif hasattr(fig, "get_axes"):
        axes = fig.get_axes()
    else:
        return False

    for ax in axes:
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        for line in ax.get_lines():
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            if ((xdata < xlim[0]).any() or (xdata > xlim[1]).any() or
                (ydata < ylim[0]).any() or (ydata > ylim[1]).any()):
                return True
    return False

def save_figure_png(output_file, bbox_inches=None, transparent=False):
    """
    Save the current matplotlib figure as a PNG file.
    """
    # Ensure the extension is .png
    base, _ = os.path.splitext(output_file)
    output_file = f"{base}.png"
    
    # Create directory if it doesn't exist
    directory = os.path.dirname(output_file)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    # Save the figure
    plt.savefig(output_file, format="png", dpi=300, bbox_inches=bbox_inches, transparent=transparent)

def get_color_palette(n_classes, palette=None, custom_palette=None):
    """
    Generate a color palette for plotting based on either a ColorBrewer palette or a custom palette file.
    """
    if custom_palette:
        palette_dict = {}
        with open(custom_palette, 'r') as file:
            lines = file.readlines()
            if len(lines) != n_classes:
                raise ValueError(f"Custom palette file has {len(lines)} lines, but {n_classes} classes are required.")
            for line in lines:
                parts = line.strip().split()
                if len(parts) == 2:
                    label, color = parts
                    palette_dict[label] = color
                else:
                    raise ValueError("Custom palette provided should have two elements maximum per line.")
        
        # Extract colors from the dictionary
        palette = [palette_dict[label] for label in palette_dict]

    else:
        if palette:
            palette = sns.color_palette(palette, n_colors=n_classes)
        else:
            # Get the base tab20 palette (20 colors)
            base_palette = sns.color_palette("tab20", n_colors=20)
            # Loop through the palette if more than 20 classes are needed
            if n_classes > 20:
                warnings.warn(f"Requested {n_classes} classes, but tab20 palette only has 20 colors. Colors will be repeated cyclically. Consider using a custom palette with custom_palette for better distinction.", UserWarning)
            palette = [base_palette[i % 20] for i in range(n_classes)]
        palette_dict = None
    
    return palette, palette_dict

def make_dark_mode(fig, ax, legend_style=None, cbar=None, gridlines=None):
    """
    Apply dark mode styling to the given figure and axis.
    """
    dark_gray = '#1F1F1F'
    fig.patch.set_facecolor(dark_gray)
    ax.set_facecolor(dark_gray)
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    if gridlines:
        gridlines.xlabel_style = {'color': 'white'}
        gridlines.ylabel_style = {'color': 'white'}
    
    if cbar:
        cbar.ax.xaxis.label.set_color('white')
        cbar.ax.tick_params(axis='x', colors='white')
        cbar.outline.set_edgecolor('white')
    
    legend = ax.get_legend()
    if legend:
        if legend_style is None or legend_style == 'default':
            for text in legend.get_texts():
                text.set_color('white')
    
    return fig, ax
