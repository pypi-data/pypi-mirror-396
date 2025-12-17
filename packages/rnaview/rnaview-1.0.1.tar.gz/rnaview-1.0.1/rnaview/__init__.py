"""
RNAview: A Comprehensive Python Package for RNA Structure Visualization and Analysis
====================================================================================

RNAview provides tools for:
- Visualizing RNA secondary and tertiary structures (2D and 3D)
- Loading and saving multiple file formats (CT, BPSEQ, dot-bracket, PDB, etc.)
- Analyzing structural features (helices, loops, pseudoknots)
- Comparing structures with standard metrics (sensitivity, PPV, F1, MCC)
- Working with RNA modifications (m6A, m5C, pseudouridine, etc.)
- Integrating with prediction tools (ViennaRNA, LinearFold, etc.)

Quick Start
-----------
>>> import rnaview as rv
>>> 
>>> # Create an RNA structure
>>> rna = rv.RNAStructure(
...     sequence="GCGCUUAAGCGC",
...     dotbracket="((((....))))",
...     name="hairpin"
... )
>>> 
>>> # Visualize
>>> rv.plot2d(rna, layout="radiate")
>>> 
>>> # Predict structure
>>> predicted = rv.predict_structure("GCGCUUAAGCGC")
>>> 
>>> # Compare structures
>>> f1 = rv.f1_score(rna, predicted)

For more information, see the documentation at https://rnaview.readthedocs.io
"""

__version__ = "1.0.0"
__author__ = "RNAview Development Team"
__license__ = "MIT"

# Core classes
from rnaview.core.structure import (
    RNAStructure,
    BasePair,
    Helix,
    Loop,
    Pseudoknot,
)
from rnaview.core.sequence import RNASequence
from rnaview.core.modifications import (
    Modification,
    ModificationType,
    ModificationSite,
    ModificationTrack,
)

# I/O functions
from rnaview.io.parsers import (
    load_structure,
    load_dotbracket,
    load_ct,
    load_bpseq,
    load_pdb,
    load_fasta,
    load_stockholm,
)
from rnaview.io.writers import (
    save_structure,
    to_dotbracket,
    to_ct,
    to_bpseq,
    to_fasta,
    to_vienna,
)

# Visualization
from rnaview.visualization.plot2d import (
    plot2d,
    plot_arc,
    plot_circular,
    plot_radiate,
)
from rnaview.visualization.plot3d import (
    plot3d,
    plot_ribbon,
    plot_surface,
)
from rnaview.visualization.colors import (
    ColorScheme,
    get_colorscheme,
    list_colorschemes,
)

# Analysis
from rnaview.analysis.metrics import (
    sensitivity,
    ppv,
    f1_score,
    mcc,
    compare_structures,
    structural_distance,
)
from rnaview.analysis.features import (
    find_helices,
    find_loops,
    find_pseudoknots,
    get_stem_loops,
    calculate_free_energy,
)

# Datasets
from rnaview.datasets.benchmark import (
    load_benchmark,
    list_benchmarks,
    BenchmarkDataset,
)

# Integrations
from rnaview.integrations.predictors import (
    predict_structure,
    list_predictors,
)

__all__ = [
    # Version
    "__version__",
    # Core classes
    "RNAStructure",
    "RNASequence",
    "BasePair",
    "Helix",
    "Loop",
    "Pseudoknot",
    "Modification",
    "ModificationType",
    "ModificationSite",
    "ModificationTrack",
    # I/O
    "load_structure",
    "load_dotbracket",
    "load_ct",
    "load_bpseq",
    "load_pdb",
    "load_fasta",
    "load_stockholm",
    "save_structure",
    "to_dotbracket",
    "to_ct",
    "to_bpseq",
    "to_fasta",
    "to_vienna",
    # Visualization
    "plot2d",
    "plot_arc",
    "plot_circular",
    "plot_radiate",
    "plot3d",
    "plot_ribbon",
    "plot_surface",
    "ColorScheme",
    "get_colorscheme",
    "list_colorschemes",
    # Analysis
    "sensitivity",
    "ppv",
    "f1_score",
    "mcc",
    "compare_structures",
    "structural_distance",
    "find_helices",
    "find_loops",
    "find_pseudoknots",
    "get_stem_loops",
    "calculate_free_energy",
    # Datasets
    "load_benchmark",
    "list_benchmarks",
    "BenchmarkDataset",
    # Integrations
    "predict_structure",
    "list_predictors",
]
