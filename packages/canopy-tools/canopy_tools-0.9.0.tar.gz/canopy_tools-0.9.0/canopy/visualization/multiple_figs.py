import os
import warnings
from typing import Optional, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def setup_figure_and_axes(subfig=None, x_fig=10, y_fig=10, projection=None, constrained_layout=False):
    """
    Set up figure and axes, handling both standalone and subfigure cases.
    """
    if subfig is not None:
        if projection:
            ax = subfig.add_subplot(1, 1, 1, projection=projection())
        else:
            ax = subfig.add_subplot(1, 1, 1)
        fig = subfig.figure
    else:
        if constrained_layout:
            fig = plt.figure(figsize=(x_fig, y_fig), constrained_layout=True)
        else:
            fig, ax = plt.subplots(figsize=(x_fig, y_fig))
            if projection:
                # Remove the default axes and create new one with projection
                fig.delaxes(ax)
                ax = fig.add_subplot(1, 1, 1, projection=projection())
            return fig, ax
        
        if projection:
            ax = fig.add_subplot(1, 1, 1, projection=projection())
        else:
            ax = fig.add_subplot(1, 1, 1)
    
    return fig, ax

def create_plot_wrapper(plot_func, x_fig: Optional[float], y_fig: Optional[float], **plot_kwargs):
    """
    Create a callable wrapper function for use with multiple_figs.
    """
    
    def plot_wrapper(subfig=None):
        kwargs = plot_kwargs.copy()
        if subfig is not None:
            kwargs['subfig'] = subfig
        kwargs['return_fig'] = False  # Prevent infinite recursion
        return plot_func(**kwargs)
    
    # Store x_fig and y_fig as attributes for multiple_figs to access
    plot_wrapper.x_fig = x_fig
    plot_wrapper.y_fig = y_fig
    
    return plot_wrapper

def create_wrapper_from_locals(plot_func, local_vars, x_fig_key='x_fig', y_fig_key='y_fig'):
    """
    Helper function to create a plot wrapper from local variables.
    Automatically extracts all parameters except excluded ones.
    """
    # Exclude these parameters from being passed to create_plot_wrapper
    exclude_keys = {'return_fig', 'x_fig', 'y_fig', 'subfig'}
    
    # Extract x_fig and y_fig
    x_fig = local_vars.get(x_fig_key)
    y_fig = local_vars.get(y_fig_key)
    
    # Get all other parameters (excluding the ones we don't want)
    plot_kwargs = {k: v for k, v in local_vars.items() 
                   if k not in exclude_keys and not k.startswith('_')}
    
    # Handle kwargs if present - unpack it into plot_kwargs
    if 'kwargs' in plot_kwargs and isinstance(plot_kwargs['kwargs'], dict):
        kwargs_dict = plot_kwargs.pop('kwargs')
        plot_kwargs.update(kwargs_dict)
    
    return create_plot_wrapper(plot_func, x_fig, y_fig, **plot_kwargs)


def multiple_figs(fig_list: List[Figure], output_file: Optional[str] = None, 
                  ncols: Optional[int] = 2, dpi: Optional[int] = 150, 
                  dark_mode: Optional[bool] = False, add_letters: Optional[bool] = False,
                  title: Optional[str] = None, title_font_size: Optional[int] = 24):
    """
    Arrange multiple figures into a single figure using matplotlib subfigures.

    Parameters
    ----------
    fig_list : list of callables
        List of plotting functions created with return_fig=True
        (e.g., make_static_plot(..., return_fig=True)).
    output_file : str, optional
        Path to save the combined figure
    ncols : int, optional
        Number of columns in the grid. Default is 2.
    dpi : int, optional
        Resolution for the output. Default is 150.
    dark_mode : bool, optional
        If True, use dark gray background instead of white. Default is False.
    add_letters : bool, optional
        If True, adds letter labels (a, b, c...) to the bottom left corner of each subfigure.
        Default is False.
    title : str, optional
        A common title for all figures.
    title_font_size : int, optional
        Font size for the title in points (pt). Default is 24.
    
    Returns
    -------
    matplotlib.Figure
        The combined figure object.
    
    Example
    -------
    plot1 = cv.make_static_plot(field_a=agpp1, field_b=agpp3, kind='scatter', return_fig=True)
    plot2 = cv.make_time_series(fields=[agpp, agpp_nolc], return_fig=True)
    cv.multiple_figs([plot1, plot2], ncols=2, output_file="combined.png")
    """
    if not fig_list:
        raise ValueError("fig_list cannot be empty")
    
    # Calculate grid dimensions
    nplots = len(fig_list)
    if ncols is None:
        ncols = 2
    nrows = _calculate_grid_dimensions(nplots, ncols)
    
    # Extract x_fig and y_fig from plot functions if available
    x_figs, y_figs = _extract_fig_sizes(fig_list)
    
    # Calculate figure size based on actual x_fig/y_fig values
    fig_width, fig_height = _calculate_figure_size(x_figs, y_figs, ncols, nrows, title)
    
    combined_fig = plt.figure(figsize=(fig_width, fig_height), constrained_layout=True)
    
    # Adjust constrained layout to reserve space for title at the top
    if title:
        layout_engine = combined_fig.get_layout_engine()
        if layout_engine:
            layout_engine.set(w_pad=0.02, h_pad=0.02, hspace=0.05, wspace=0.05)
    
    # Create subfigures with width and height ratios based on x_fig/y_fig
    width_ratios, height_ratios = _calculate_size_ratios(x_figs, y_figs, ncols, nrows, nplots)
    if width_ratios and height_ratios:
        subfigs = combined_fig.subfigures(nrows, ncols, wspace=0.05, hspace=0.05,
                                          width_ratios=width_ratios, height_ratios=height_ratios)
    else:
        subfigs = combined_fig.subfigures(nrows, ncols, wspace=0.05, hspace=0.05)
    
    # Flatten subfigs if needed (subfigs can be 1D or 2D array)
    subfigs = _flatten_subfigs(subfigs, nrows, ncols)
    
    # Apply dark mode to figure if requested
    if dark_mode:
        combined_fig.patch.set_facecolor('#1F1F1F')
    
    # Process each figure
    for i, fig_item in enumerate(fig_list):
        if i >= len(subfigs):
            break
            
        subfig = subfigs[i]
        
        # Apply dark mode to subfigure if requested
        if dark_mode:
            subfig.patch.set_facecolor('#1F1F1F')
        
        _process_figure_item(fig_item, subfig, i)
        
        # Add letter label if requested
        if add_letters:
            _add_letter_label(subfig, i, dark_mode)
    
    # Add title if provided
    if title:
        title_color = 'white' if dark_mode else 'black'
        combined_fig.suptitle(title, fontsize=title_font_size, y=1.05, color=title_color)
    
    # Save or show the result
    _save_or_show_figure(combined_fig, output_file, dpi)
    
    return combined_fig

def _calculate_grid_dimensions(nplots: int, ncols: int) -> int:
    """
    Calculate the number of rows needed for the grid layout.
    """
    nrows = (nplots + ncols - 1) // ncols
    return nrows

def _extract_fig_sizes(fig_list: List[Figure]) -> Tuple[List[float], List[float]]:
    """
    Extract x_fig and y_fig from plot functions if available.
    """
    x_figs = []
    y_figs = []
    for fig_item in fig_list:
        if callable(fig_item) and hasattr(fig_item, 'x_fig') and hasattr(fig_item, 'y_fig'):
            x_figs.append(fig_item.x_fig if fig_item.x_fig is not None else 10)
            y_figs.append(fig_item.y_fig if fig_item.y_fig is not None else 10)
        else:
            # Default values if not available
            x_figs.append(10)
            y_figs.append(10)
    return x_figs, y_figs

def _calculate_figure_size(x_figs: List[float], y_figs: List[float], ncols: int, nrows: int, 
                           title: Optional[str]) -> Tuple[float, float]:
    """
    Calculate figure size based on actual x_fig/y_fig values.
    Use max values per row/column to ensure all subfigures fit.
    """
    nplots = len(x_figs)
    
    if x_figs and y_figs:
        # Calculate max width per column and max height per row
        max_width_per_col = []
        max_height_per_row = []
        
        for col in range(ncols):
            col_indices = [i for i in range(nplots) if i % ncols == col]
            if col_indices:
                max_width_per_col.append(max(x_figs[i] for i in col_indices))
            else:
                max_width_per_col.append(10)
        
        for row in range(nrows):
            row_indices = [i for i in range(nplots) if i // ncols == row]
            if row_indices:
                max_height_per_row.append(max(y_figs[i] for i in row_indices))
            else:
                max_height_per_row.append(10)
        
        fig_width = sum(max_width_per_col)
        fig_height = sum(max_height_per_row)
    else:
        # Fallback to default sizing
        fig_width = ncols * 6
        fig_height = nrows * 5
    
    # Add extra space for title if provided
    if title:
        fig_height += 0.8
    
    return fig_width, fig_height

def _calculate_size_ratios(x_figs: List[float], y_figs: List[float], ncols: int, nrows: int, 
                           nplots: int) -> Tuple[Optional[List[float]], Optional[List[float]]]:
    """
    Calculate width and height ratios based on x_fig/y_fig values.
    """
    if not x_figs or not y_figs:
        return None, None
    
    # Calculate width ratios (proportional to x_fig values per column)
    width_ratios = []
    for col in range(ncols):
        col_indices = [i for i in range(nplots) if i % ncols == col]
        if col_indices:
            # Use average x_fig for this column
            width_ratios.append(sum(x_figs[i] for i in col_indices) / len(col_indices))
        else:
            width_ratios.append(1)
    
    # Calculate height ratios (proportional to y_fig values per row)
    height_ratios = []
    for row in range(nrows):
        row_indices = [i for i in range(nplots) if i // ncols == row]
        if row_indices:
            # Use average y_fig for this row
            height_ratios.append(sum(y_figs[i] for i in row_indices) / len(row_indices))
        else:
            height_ratios.append(1)
    
    return width_ratios, height_ratios


def _flatten_subfigs(subfigs, nrows: int, ncols: int) -> List[Figure]:
    """
    Flatten subfigs if needed (subfigs can be 1D or 2D array).
    Convert numpy array to list of Figure objects.
    """
    if nrows == 1 or ncols == 1:
        # For 1D case, subfigures returns a 1D array
        if hasattr(subfigs, 'flatten'):
            subfigs_flat = subfigs.flatten()
            subfigs_list: List[Figure] = [subfigs_flat[i] for i in range(len(subfigs_flat))]
        else:
            subfigs_list = [subfigs]
    else:
        # For 2D case, flatten the array
        subfigs_flat = subfigs.flatten()
        subfigs_list = [subfigs_flat[i] for i in range(len(subfigs_flat))]
    return subfigs_list

def _process_figure_item(fig_item, subfig, i: int):
    """
    Process a single figure item - either call it as a function or handle as a figure object.
    """
    # Check if fig_item is a callable (function) or a figure object
    if callable(fig_item):
        # It's a function - call it with subfig parameter
        try:
            result = fig_item(subfig=subfig)
            # If function returns a figure, close it (plot should be in subfig now)
            if result is not None and hasattr(result, 'savefig'):
                plt.close(result)
        except TypeError as e:
            # Function doesn't accept subfig parameter - try calling without it
            # This handles legacy functions that don't support subfig yet
            try:
                result = fig_item()
                warnings.warn(f"Function at index {i} doesn't support subfig parameter. "
                              f"Creating plot separately (may cause layout issues).")
                if result is not None:
                    plt.close(result)
            except Exception as e2:
                raise ValueError(f"Plotting function at index {i} failed: {e2}") from e2
    else:
        # It's a figure object (legacy support) - just close it
        warnings.warn(f"Figure object at index {i} provided. For best results with subfigures, "
                      f"use return_fig=True when calling plotting functions.")
        if hasattr(fig_item, 'fig'):
            plt.close(fig_item.fig)
        else:
            plt.close(fig_item)

def _add_letter_label(subfig, i: int, dark_mode: bool):
    """
    Add letter label to the bottom left corner of a subfigure.
    """
    letter = chr(97 + i)  # Convert number to letter (97 is ASCII for 'a')
    # Get the first axis in the subfigure
    axes = subfig.get_axes()
    if axes:
        main_ax = axes[0]
        main_ax.text(0.02, 0.98, f"({letter})", 
                   fontsize=12, fontweight='bold',
                   color='white' if dark_mode else 'black',
                   transform=main_ax.transAxes,
                   verticalalignment='top',
                   horizontalalignment='left',
                   bbox=dict(boxstyle='round,pad=0.3', 
                            facecolor='white' if not dark_mode else '#1F1F1F',
                            edgecolor='black' if not dark_mode else 'white', 
                            alpha=0.8))

def _save_or_show_figure(combined_fig, output_file: Optional[str], dpi: int):
    """
    Save or show the combined figure.
    """
    if output_file:
        # Ensure the extension is .png
        base, _ = os.path.splitext(output_file)
        output_file = f"{base}.png"
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(output_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        combined_fig.savefig(output_file, dpi=dpi, bbox_inches='tight', 
                            facecolor=combined_fig.get_facecolor(), 
                            edgecolor='none', pad_inches=0.1)
        plt.close(combined_fig)
    else:
        plt.show()
