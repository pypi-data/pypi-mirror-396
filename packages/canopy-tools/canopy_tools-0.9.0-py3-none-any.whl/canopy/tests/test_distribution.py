# ------------------------------------------
# | Tests for distribution plotting using canopy |
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
def test_make_distribution_plot_all_types():
    """Test that make_distribution_plot works with all plot types."""
    
    field_a = Field.from_file(DATA_DIR / "anpp_spain_1990_2010.out.gz")
    field_b = Field.from_file(DATA_DIR / "anpp_spain_1990_2010_mod.out.gz")
    
    # Test all plot types (excluding 'swarm' as it's very slow with large datasets)
    plot_types = ["box", "violin", "boxen", "strip", "point", "bar"]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for plot_type in plot_types:
            output_file = Path(tmpdir) / f"test_distribution_{plot_type}.png"
            cv.make_distribution_plot(
                fields=[field_a, field_b],
                plot_type=plot_type,
                layers=["Abi_alb", "Bet_pen", "Bet_pub", "Que_rob", "C3_gr"],
                field_labels=["no mod", "mod"],
                yaxis_label="Actual NPP",
                unit="kgC m-2",
                title=f"Distribution plot ({plot_type})",
                palette="tab10",
                dark_mode=True,
                transparent=False,
                x_fig=10,
                y_fig=10,
                output_file=str(output_file)
            )

@pytest.mark.filterwarnings("ignore:FigureCanvasAgg is non-interactive, and thus cannot be shown:UserWarning")
def test_make_distribution_plot_single_field():
    """Test that make_distribution_plot works with a single field."""
    
    field_a = Field.from_file(DATA_DIR / "anpp_spain_1990_2010.out.gz")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_distribution_single.png"
        cv.make_distribution_plot(
            fields=field_a,
            plot_type="box",
            layers=["Abi_alb", "Bet_pen", "Bet_pub"],
            yaxis_label="Actual NPP",
            unit="kgC m-2",
            title="Single field distribution plot",
            palette="tab10",
            dark_mode=False,
            transparent=False,
            x_fig=10,
            y_fig=10,
            output_file=str(output_file)
        )
