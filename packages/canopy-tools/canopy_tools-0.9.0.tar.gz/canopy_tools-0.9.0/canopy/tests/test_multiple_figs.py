# ------------------------------------------
# | Tests for multiple_figs using canopy |
# ------------------------------------------

import pytest
from pathlib import Path
import tempfile
import matplotlib
matplotlib.use('Agg')  # Set non-GUI backend before pyplot import
from canopy import Field
import canopy.visualization as cv

DATA_DIR = Path("tests/test_data")

@pytest.mark.filterwarnings("ignore:FigureCanvasAgg is non-interactive, and thus cannot be shown:UserWarning")
def test_multiple_figs_basic():
    """Test that multiple_figs works with basic plot combinations."""
    
    field_a = Field.from_file(DATA_DIR / "anpp_spain_1990_2010.out.gz")
    field_b = Field.from_file(DATA_DIR / "anpp_spain_1990_2010_mod.out.gz")
    
    # Create plot functions
    fig1 = cv.make_static_plot(
        field_a=field_a,
        field_b=field_b,
        layers=["Abi_alb", "Bet_pen"],
        field_a_label="no mod",
        field_b_label="mod",
        unit_a="kgC m-2",
        unit_b="kgC m-2",
        title="Scatter plot",
        palette="tab10",
        x_fig=8,
        y_fig=8,
        return_fig=True
    )
    
    fig2 = cv.make_time_series(
        fields=[field_a, field_b],
        layers="Abi_alb",
        field_labels=["no mod", "mod"],
        yaxis_label="Actual NPP",
        unit="kgC m-2",
        title="Time series",
        x_fig=8,
        y_fig=8,
        return_fig=True
    )
    
    fig3 = cv.make_distribution_plot(
        fields=[field_a, field_b],
        layers="Abi_alb",
        field_labels=["no mod", "mod"],
        yaxis_label="Actual NPP",
        unit="kgC m-2",
        title="Distribution plot",
        plot_type="box",
        x_fig=8,
        y_fig=8,
        return_fig=True
    )
    
    # Test multiple_figs with 2 columns
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_multiple_basic.png"
        cv.multiple_figs(
            [fig1, fig2, fig3],
            ncols=2,
            dark_mode=False,
            add_letters=True,
            title="Combined plots test",
            output_file=str(output_file)
        )

@pytest.mark.filterwarnings("ignore:FigureCanvasAgg is non-interactive, and thus cannot be shown:UserWarning")
def test_multiple_figs_with_maps():
    """Test that multiple_figs works with map plots."""
    
    field_a = Field.from_file(DATA_DIR / "anpp_spain_1990_2010.out.gz")
    field_b = Field.from_file(DATA_DIR / "anpp_spain_1990_2010_mod.out.gz")
    
    # Create plot functions including maps
    fig1 = cv.make_simple_map(
        field=field_a,
        layer="Abi_alb",
        cb_label="Actual NPP",
        title="Map 1",
        unit="kgC m-2",
        n_classes=4,
        x_fig=8,
        y_fig=8,
        return_fig=True
    )
    
    fig2 = cv.make_diff_map(
        field_a=field_a,
        field_b=field_b,
        layer="Abi_alb",
        cb_label="Actual NPP",
        title="Difference map",
        unit="kgC m-2",
        n_classes=4,
        x_fig=8,
        y_fig=8,
        return_fig=True
    )
    
    # Test multiple_figs with maps
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_multiple_maps.png"
        cv.multiple_figs(
            [fig1, fig2],
            ncols=2,
            dark_mode=False,
            add_letters=True,
            output_file=str(output_file)
        )

@pytest.mark.filterwarnings("ignore:FigureCanvasAgg is non-interactive, and thus cannot be shown:UserWarning")
def test_multiple_figs_single_column():
    """Test that multiple_figs works with single column layout."""
    
    field_a = Field.from_file(DATA_DIR / "anpp_spain_1990_2010.out.gz")
    field_b = Field.from_file(DATA_DIR / "anpp_spain_1990_2010_mod.out.gz")
    
    fig1 = cv.make_static_plot(
        field_a=field_a,
        field_b=field_b,
        layers="Abi_alb",
        field_a_label="no mod",
        field_b_label="mod",
        unit_a="kgC m-2",
        unit_b="kgC m-2",
        title="Plot 1",
        x_fig=10,
        y_fig=6,
        return_fig=True
    )
    
    fig2 = cv.make_time_series(
        fields=[field_a, field_b],
        layers="Abi_alb",
        field_labels=["no mod", "mod"],
        yaxis_label="Actual NPP",
        unit="kgC m-2",
        title="Plot 2",
        x_fig=10,
        y_fig=6,
        return_fig=True
    )
    
    # Test multiple_figs with single column
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_multiple_single_col.png"
        cv.multiple_figs(
            [fig1, fig2],
            ncols=1,
            dark_mode=False,
            add_letters=False,
            output_file=str(output_file)
        )
