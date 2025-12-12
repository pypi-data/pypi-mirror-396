# -----------------------------------------------
# | Tests for latitudinal plotting using canopy |
# -----------------------------------------------

import pytest
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Set non-GUI backend before pyplot import
from canopy import Field
import canopy.visualization as cv

DATA_DIR = Path("tests/test_data")

@pytest.mark.filterwarnings("ignore:FigureCanvasAgg is non-interactive, and thus cannot be shown:UserWarning")
def test_make_latitudinal_plot():
    """Test that make_latitudinal_plot works on a test field."""

    field = Field.from_file(DATA_DIR / "anpp_spain_1990_2010.out.gz")

    cv.make_latitudinal_plot(
        fields=field,
        layers=["Abi_alb","Bet_pen","Bet_pub","Que_rob","C3_gr"],
        yaxis_label="Carbon Pool (kgC m-2)",
        title="Carbon Pool in Spain from 1990 to 2010",
        unit="kgC m⁻² yr⁻¹",
        palette="Greens",
        move_legend=True,
        legend_style="default",
        max_labels_per_col=3,
        dark_mode=True,
        x_fig=10,
        y_fig=5,
        linewidth=2.5,
        alpha=0.7,
        linestyle='--'
        )

@pytest.mark.filterwarnings("ignore:FigureCanvasAgg is non-interactive, and thus cannot be shown:UserWarning")
def test_make_latitudinal_plot_single_layer():
    """Test that make_latitudinal_plot works with a single layer."""

    field = Field.from_file(DATA_DIR / "anpp_spain_1990_2010.out.gz")

    cv.make_latitudinal_plot(
        fields=field,
        layers="Total",
        yaxis_label="Carbon Pool (kgC m-2)",
        title="Single layer latitudinal plot",
        unit="kgC m⁻² yr⁻¹",
        dark_mode=False,
        x_fig=8,
        y_fig=10
        )

@pytest.mark.filterwarnings("ignore:FigureCanvasAgg is non-interactive, and thus cannot be shown:UserWarning")
def test_make_latitudinal_plot_multiple_fields():
    """Test that make_latitudinal_plot works with multiple fields."""

    field1 = Field.from_file(DATA_DIR / "anpp_spain_1990_2010.out.gz")
    field2 = Field.from_file(DATA_DIR / "anpp_spain_1990_2010.out.gz")

    cv.make_latitudinal_plot(
        fields=[field1, field2],
        layers="Total",
        field_labels=["Field 1", "Field 2"],
        yaxis_label="Carbon Pool (kgC m-2)",
        title="Multiple fields latitudinal plot",
        unit="kgC m⁻² yr⁻¹",
        palette="Set2",
        legend_style="default",
        dark_mode=False,
        x_fig=10,
        y_fig=8
        )

@pytest.mark.filterwarnings("ignore:FigureCanvasAgg is non-interactive, and thus cannot be shown:UserWarning")
def test_make_latitudinal_plot_multiple_fields_layers():
    """Test that make_latitudinal_plot works with multiple fields and layers."""

    field1 = Field.from_file(DATA_DIR / "anpp_spain_1990_2010.out.gz")
    field2 = Field.from_file(DATA_DIR / "anpp_spain_1990_2010.out.gz")

    cv.make_latitudinal_plot(
        fields=[field1, field2],
        layers=["Abi_alb", "Bet_pen"],
        field_labels=["Field 1", "Field 2"],
        yaxis_label="Carbon Pool (kgC m-2)",
        title="Multiple fields and layers latitudinal plot",
        unit="kgC m⁻² yr⁻¹",
        palette="Set2",
        legend_style="default",
        dark_mode=True,
        x_fig=10,
        y_fig=10
        )

