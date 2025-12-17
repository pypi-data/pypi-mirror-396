# RNAview User Manual

**Version 1.0.0**

A Comprehensive Python Package for RNA Structure Visualization and Analysis

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Quick Start Guide](#3-quick-start-guide)
4. [Core Concepts](#4-core-concepts)
5. [Working with RNA Structures](#5-working-with-rna-structures)
6. [File Input/Output](#6-file-inputoutput)
7. [Visualization](#7-visualization)
8. [Structure Analysis](#8-structure-analysis)
9. [RNA Modifications](#9-rna-modifications)
10. [Structure Prediction](#10-structure-prediction)
11. [Benchmark Datasets](#11-benchmark-datasets)
12. [API Reference](#12-api-reference)
13. [Troubleshooting](#13-troubleshooting)
14. [Examples](#14-examples)

---

## 1. Introduction

### 1.1 What is RNAview?

RNAview is a Python library designed for researchers to visualize, analyze, and explore RNA secondary and tertiary structures. It provides:

- **Comprehensive visualization tools** for 2D and 3D RNA structures
- **Support for multiple file formats** used in RNA research
- **Integration with prediction tools** like ViennaRNA and LinearFold
- **RNA modification support** for epitranscriptomics research
- **Benchmark datasets** for method validation
- **Analysis metrics** for structure comparison

### 1.2 Key Features

| Feature | Description |
|---------|-------------|
| 2D Visualization | Radiate, circular, NAView, and arc diagram layouts |
| 3D Visualization | Interactive backbone, ribbon, and surface views |
| File Formats | CT, BPSEQ, dot-bracket, PDB, mmCIF, FASTA, Stockholm |
| Modifications | 70+ RNA modifications with MODOMICS nomenclature |
| Predictions | ViennaRNA, LinearFold, CONTRAfold integration |
| Analysis | Sensitivity, PPV, F1, MCC, structural distance |
| Benchmarks | Curated tRNA, 5S rRNA, and small RNA datasets |

### 1.3 Requirements

- Python 3.8 or higher
- NumPy >= 1.20.0
- Optional: matplotlib, plotly, scipy for visualization

---

## 2. Installation

### 2.1 Basic Installation

```bash
pip install rnaview
```

### 2.2 With Visualization Support

```bash
pip install rnaview[visualization]
```

This includes matplotlib, plotly, and scipy.

### 2.3 Full Installation

```bash
pip install rnaview[full]
```

This includes all optional dependencies including BioPython.

### 2.4 Development Installation

```bash
git clone https://github.com/rnaview/rnaview.git
cd rnaview
pip install -e .[dev]
```

### 2.5 Verifying Installation

```python
import rnaview as rf
print(rf.__version__)  # Should print "1.0.0"
```

---

## 3. Quick Start Guide

### 3.1 Creating Your First RNA Structure

```python
import rnaview as rf

# Create an RNA structure from sequence and dot-bracket notation
rna = rf.RNAStructure(
    sequence="GCGCUUAAGCGC",
    dotbracket="((((....))))",
    name="My_Hairpin"
)

# View basic properties
print(f"Length: {rna.length} nucleotides")
print(f"Base pairs: {rna.num_pairs}")
print(f"Has pseudoknot: {rna.has_pseudoknot}")
```

### 3.2 Loading from a File

```python
# Auto-detect format from extension
rna = rf.load_structure("structure.ct")

# Or specify format explicitly
rna = rf.load_structure("data.txt", format="bpseq")
```

### 3.3 Basic Visualization

```python
# Create a 2D plot
fig = rf.plot2d(rna, layout="radiate")
fig.savefig("structure.png")

# Create an arc diagram
fig = rf.plot_arc(rna)
fig.savefig("arc_diagram.png")
```

### 3.4 Structure Prediction

```python
# Predict structure for a sequence
sequence = "GCGCUUAAGCGC"
predicted = rf.predict_structure(sequence)

print(predicted.to_dotbracket())
```

---

## 4. Core Concepts

### 4.1 The RNAStructure Class

The `RNAStructure` class is the central data structure in RNAview. It represents an RNA molecule with:

- **Sequence**: The nucleotide sequence (A, C, G, U)
- **Base pairs**: Paired positions forming secondary structure
- **Coordinates**: Optional 2D or 3D spatial coordinates
- **Modifications**: RNA chemical modifications
- **Reactivity**: Experimental probing data (e.g., SHAPE)

```python
from rnaview import RNAStructure

rna = RNAStructure(
    sequence="GCGCUUAAGCGC",
    dotbracket="((((....))))",
    name="example"
)
```

### 4.2 Base Pair Notation

RNAview uses **dot-bracket notation** for secondary structure:

| Symbol | Meaning |
|--------|---------|
| `.` | Unpaired nucleotide |
| `(` `)` | Base pair (standard) |
| `[` `]` | Pseudoknot level 1 |
| `{` `}` | Pseudoknot level 2 |
| `<` `>` | Pseudoknot level 3 |

Example with pseudoknot:
```
Sequence:  GGAAGCUGACCAGACAGUCGCC
Structure: ..(((((....[[[..))))).
```

### 4.3 Coordinate Systems

RNAview supports two coordinate systems:

- **2D coordinates**: For secondary structure visualization (Nx2 array)
- **3D coordinates**: For tertiary structure from PDB/mmCIF (Nx3 array)

```python
# Access coordinates
if rna.coordinates_2d is not None:
    print(rna.coordinates_2d.shape)  # (N, 2)

if rna.coordinates_3d is not None:
    print(rna.coordinates_3d.shape)  # (N, 3)
```

---

## 5. Working with RNA Structures

### 5.1 Creating Structures

#### From Sequence and Structure
```python
rna = rf.RNAStructure(
    sequence="GCGCUUAAGCGC",
    dotbracket="((((....))))",
    name="hairpin"
)
```

#### From Base Pair List
```python
rna = rf.RNAStructure(
    sequence="GCGCUUAAGCGC",
    base_pairs=[(0, 11), (1, 10), (2, 9), (3, 8)],
    name="hairpin"
)
```

### 5.2 Accessing Structure Properties

```python
# Basic properties
print(rna.sequence)          # "GCGCUUAAGCGC"
print(rna.length)            # 12
print(rna.num_pairs)         # 4
print(rna.name)              # "hairpin"

# Base pairs
for bp in rna.base_pairs:
    print(f"Pair: {bp.i}-{bp.j}, Type: {bp.pair_type}")

# Check if position is paired
print(rna.is_paired(0))           # True
print(rna.get_paired_position(0)) # 11

# Unpaired positions
print(rna.unpaired_positions)     # [4, 5, 6, 7]
```

### 5.3 Structural Elements

```python
# Find helices (stems)
helices = rna.get_helices()
for h in helices:
    print(f"Helix: {h.length} bp, positions {h.start_5p}-{h.end_5p}")

# Find loops
loops = rna.get_loops()
for loop in loops:
    print(f"Loop type: {loop.loop_type}, size: {loop.size}")

# Check for pseudoknots
if rna.has_pseudoknot:
    pks = rna.get_pseudoknots()
    print(f"Found {len(pks)} pseudoknots")
```

### 5.4 Format Conversion

```python
# Convert to dot-bracket
db = rna.to_dotbracket()
print(db)  # "((((....))))"

# Convert to CT format
ct = rna.to_ct_format()

# Convert to BPSEQ format
bpseq = rna.to_bpseq_format()

# Get structure summary
print(rna.summary())
```

---

## 6. File Input/Output

### 6.1 Supported Formats

| Format | Extension | Read | Write | Description |
|--------|-----------|------|-------|-------------|
| Dot-bracket | .dbn, .db | ✅ | ✅ | Secondary structure notation |
| CT | .ct | ✅ | ✅ | Connectivity table |
| BPSEQ | .bpseq | ✅ | ✅ | Base pair sequence |
| PDB | .pdb | ✅ | ❌ | 3D atomic coordinates |
| mmCIF | .cif | ✅ | ❌ | Macromolecular CIF |
| FASTA | .fasta, .fa | ✅ | ✅ | Sequence format |
| Stockholm | .sto | ✅ | ❌ | Alignment with structure |

### 6.2 Loading Structures

```python
import rnaview as rf

# Auto-detect format
rna = rf.load_structure("structure.ct")

# Explicit format
rna = rf.load_structure("data.txt", format="bpseq")

# Load from PDB with specific chain
rna = rf.load_pdb("structure.pdb", chain_id="A")

# Load multiple sequences from FASTA
structures = rf.load_fasta("sequences.fasta")

# Load alignment from Stockholm
structures = rf.load_stockholm("alignment.sto")
```

### 6.3 Saving Structures

```python
# Save to file (format from extension)
rf.save_structure(rna, "output.ct")
rf.save_structure(rna, "output.dbn")

# Get format strings
ct_string = rf.to_ct(rna)
bpseq_string = rf.to_bpseq(rna)
dbn_string = rf.to_dotbracket(rna)

# Write to file manually
with open("output.ct", "w") as f:
    f.write(rf.to_ct(rna))
```

### 6.4 Working with Compressed Files

```python
# Gzip-compressed files are automatically handled
rna = rf.load_structure("structure.ct.gz")
```

---

## 7. Visualization

### 7.1 2D Visualization Layouts

RNAview provides multiple layout algorithms:

| Layout | Description | Best For |
|--------|-------------|----------|
| `radiate` | Tree-like radial arrangement | General use, stems visible |
| `circular` | Nucleotides on a circle | Compact view |
| `naview` | Optimized angles and spacing | Publication figures |
| `arc` | Linear sequence with arcs | Pseudoknots, long RNAs |

```python
import rnaview as rf

rna = rf.load_structure("trna.ct")

# Different layouts
rf.plot2d(rna, layout="radiate")
rf.plot2d(rna, layout="circular")
rf.plot2d(rna, layout="naview")
rf.plot_arc(rna)
```

### 7.2 Customizing 2D Plots

```python
fig = rf.plot2d(
    rna,
    layout="radiate",
    figsize=(10, 10),              # Figure size in inches
    color_scheme="nucleotide",     # Color scheme
    show_sequence=True,            # Show nucleotide letters
    show_numbering=True,           # Show position numbers
    numbering_interval=10,         # Number every 10th position
    show_modifications=True,       # Highlight modifications
    show_basepairs=True,           # Draw base pair lines
    highlight_positions=[1,2,3],   # Highlight specific positions
    highlight_color="#FFD700",     # Highlight color
    title="My Structure",          # Plot title
    save_path="output.png",        # Save to file
    dpi=300                        # Resolution
)
```

### 7.3 Color Schemes

Available predefined color schemes:

| Scheme | Description |
|--------|-------------|
| `nucleotide` | A=red, C=teal, G=blue, U=green |
| `vibrant` | Bright, high-contrast colors |
| `pastel` | Soft, muted colors |
| `colorblind` | Okabe-Ito colorblind-friendly |
| `grayscale` | Black and white |
| `publication` | Publication-ready scheme |

```python
# Use a color scheme
rf.plot2d(rna, color_scheme="colorblind")

# Get color scheme object for customization
from rnaview.visualization import get_colorscheme

colors = get_colorscheme("nucleotide")
colors.nucleotide_colors['A'] = '#FF0000'  # Custom red for A
rf.plot2d(rna, color_scheme=colors)
```

### 7.4 Arc Diagrams

Arc diagrams are excellent for visualizing pseudoknots:

```python
fig = rf.plot_arc(
    rna,
    figsize=(14, 6),
    show_sequence=True,
    show_numbering=True,
    numbering_interval=20,
    arc_height_scale=0.4      # Scale arc heights
)
```

### 7.5 3D Visualization

For structures with 3D coordinates (from PDB/mmCIF):

```python
# Load 3D structure
rna = rf.load_structure("structure.pdb")

# Create interactive 3D plot (opens in browser)
fig = rf.plot3d(rna, style="backbone")
fig.show()

# Different styles
rf.plot3d(rna, style="backbone")  # Line with spheres
rf.plot3d(rna, style="ribbon")    # Smoothed ribbon
rf.plot3d(rna, style="spheres")   # Large spheres
rf.plot3d(rna, style="surface")   # Molecular surface

# Customize 3D plot
fig = rf.plot3d(
    rna,
    style="ribbon",
    show_basepairs=True,
    show_modifications=True,
    highlight_positions=[10, 20, 30],
    title="3D Structure",
    width=800,
    height=600
)

# Save as HTML
fig.write_html("structure_3d.html")
```

### 7.6 Reactivity Data Overlay

Visualize experimental data (SHAPE, DMS, etc.):

```python
import numpy as np

# Add reactivity data
rna.set_reactivity(np.random.rand(rna.length))

# Plot with overlay
from rnaview.visualization.plot2d import plot_reactivity_overlay

fig = plot_reactivity_overlay(
    rna,
    layout="radiate",
    cmap="RdYlBu_r",    # Red=high, Blue=low
    vmin=0,
    vmax=1
)
```

---

## 8. Structure Analysis

### 8.1 Comparison Metrics

RNAview provides standard metrics for comparing structures:

```python
import rnaview as rf

reference = rf.load_structure("reference.ct")
predicted = rf.load_structure("predicted.ct")

# Calculate metrics
sens = rf.sensitivity(reference, predicted)  # True positives / Reference pairs
ppv = rf.ppv(reference, predicted)           # True positives / Predicted pairs
f1 = rf.f1_score(reference, predicted)       # Harmonic mean of sens and PPV
mcc = rf.mcc(reference, predicted)           # Matthews correlation coefficient

print(f"Sensitivity: {sens:.3f}")
print(f"PPV: {ppv:.3f}")
print(f"F1 Score: {f1:.3f}")
print(f"MCC: {mcc:.3f}")
```

### 8.2 Metric Definitions

| Metric | Formula | Range | Best |
|--------|---------|-------|------|
| Sensitivity | TP / (TP + FN) | 0-1 | 1 |
| PPV | TP / (TP + FP) | 0-1 | 1 |
| F1 Score | 2 × (PPV × Sens) / (PPV + Sens) | 0-1 | 1 |
| MCC | Correlation coefficient | -1 to 1 | 1 |

Where:
- TP = True positives (correctly predicted pairs)
- FP = False positives (predicted but not in reference)
- FN = False negatives (in reference but not predicted)
- TN = True negatives (correctly unpaired)

### 8.3 Structural Distance

```python
# Calculate base pair distance
distance = rf.structural_distance(rna1, rna2)
print(f"BP distance: {distance}")

# Compare structures comprehensively
comparison = rf.compare_structures(reference, predicted)
print(comparison)
```

### 8.4 Feature Analysis

```python
from rnaview.analysis import features

# Find all helices
helices = rf.find_helices(rna)

# Find all loops
loops = rf.find_loops(rna)

# Find pseudoknots
pks = rf.find_pseudoknots(rna)

# Get stem-loop structures
stem_loops = rf.get_stem_loops(rna)

# Calculate free energy (requires ViennaRNA)
energy = rf.calculate_free_energy(rna)
```

---

## 9. RNA Modifications

### 9.1 Supported Modifications

RNAview supports 70+ RNA modifications based on MODOMICS nomenclature:

| Type | Symbol | Full Name |
|------|--------|-----------|
| m6A | m6A | N6-methyladenosine |
| m5C | m5C | 5-methylcytidine |
| m1A | m1A | N1-methyladenosine |
| Ψ | Ψ | Pseudouridine |
| I | I | Inosine |
| Am | Am | 2'-O-methyladenosine |

### 9.2 Creating Modifications

```python
from rnaview import Modification

# Use convenience methods
m6a = Modification.m6A()
psi = Modification.pseudouridine()
m5c = Modification.m5C()
inosine = Modification.inosine()

# Create 2'-O-methylation for any base
am = Modification.two_prime_O_methyl('A')
gm = Modification.two_prime_O_methyl('G')

# Access modification properties
print(m6a.full_name)           # "N6-methyladenosine"
print(m6a.symbol)              # "m6A"
print(m6a.parent_base)         # "A"
print(m6a.mass_shift)          # 14.016
print(m6a.detection_methods)   # ["MeRIP-seq", "m6A-seq", ...]
print(m6a.biological_function) # Description
print(m6a.color)               # Hex color for visualization
```

### 9.3 Adding Modifications to Structures

```python
rna = rf.RNAStructure(
    sequence="GCGCUUAAGCGC",
    dotbracket="((((....))))"
)

# Add modifications at specific positions (0-indexed)
rna.add_modification(4, Modification.m6A())
rna.add_modification(5, Modification.pseudouridine())

# Check modifications
for pos, mod in rna.modifications.items():
    print(f"Position {pos+1}: {mod.full_name}")

# Get modification at position
mod = rna.get_modification(4)
if mod:
    print(f"Found: {mod.symbol}")
```

### 9.4 Modification Tracks

For working with many modifications:

```python
from rnaview.core.modifications import ModificationTrack, ModificationSite

# Create a track
track = ModificationTrack(sequence_length=100, name="m6A_sites")

# Add sites
track.add_site(ModificationSite(
    position=25,
    modification=Modification.m6A(),
    confidence=0.95,
    stoichiometry=0.7
))

# Query sites
sites = track.get_sites_in_range(20, 30)
sites_by_type = track.get_sites_by_type(ModificationType.M6A)
high_conf = track.filter_by_confidence(0.9)

# Get density
density = track.get_modification_density(window_size=50)

# Export to BED format
bed = track.to_bed_format(sequence_name="chr1")
```

### 9.5 Finding Modification Motifs

```python
from rnaview.core.modifications import find_modification_motifs, ModificationType

# Find potential m6A sites (DRACH motif)
positions = find_modification_motifs(rna.sequence, ModificationType.M6A)
print(f"Potential m6A sites: {positions}")
```

---

## 10. Structure Prediction

### 10.1 Available Predictors

| Predictor | Type | Requirements |
|-----------|------|--------------|
| viennarna | Thermodynamic MFE | ViennaRNA Package |
| linearfold | Linear-time | LinearFold binary |
| contrafold | Machine learning | CONTRAfold binary |
| fallback | Basic DP | None (built-in) |

```python
# List available predictors
print(rf.list_predictors())
# ['viennarna', 'linearfold', 'contrafold', 'fallback']

# List only installed predictors
print(rf.list_predictors(available_only=True))
```

### 10.2 Predicting Structures

```python
# Auto-select best available method
rna = rf.predict_structure("GCGCUUAAGCGC")

# Use specific predictor
rna = rf.predict_structure("GCGCUUAAGCGC", method="viennarna")

# With parameters
rna = rf.predict_structure(
    "GCGCUUAAGCGC",
    method="viennarna",
    temperature=37.0,    # Celsius
    dangles=2            # Dangling end treatment
)
```

### 10.3 ViennaRNA Integration

```python
from rnaview.integrations import viennarna

# MFE structure prediction
rna = viennarna.mfe_structure("GCGCUUAAGCGC")

# Partition function
pf_result = viennarna.partition_function("GCGCUUAAGCGC")
print(f"Ensemble free energy: {pf_result['energy']}")

# Suboptimal structures
subopt = viennarna.suboptimal_structures(
    "GCGCUUAAGCGC",
    energy_range=5.0,  # kcal/mol above MFE
    max_structures=10
)
```

### 10.4 Comparing Predictors

```python
from rnaview.integrations.predictors import compare_predictions

# Compare all available predictors
results = compare_predictions("GCGCUUAAGCGC")

for method, structure in results.items():
    print(f"{method}: {structure.to_dotbracket()}")
```

---

## 11. Benchmark Datasets

### 11.1 Available Benchmarks

RNAview includes curated benchmark datasets:

| Dataset | Description | Structures |
|---------|-------------|------------|
| trna | Transfer RNA structures | 5 |
| small_rna | Small regulatory RNAs | 5 |

### 11.2 Loading Benchmarks

```python
# List available benchmarks
print(rf.list_benchmarks())

# Load a benchmark
benchmark = rf.load_benchmark("trna")

print(f"Dataset: {benchmark.name}")
print(f"Structures: {len(benchmark)}")

# Iterate through structures
for rna in benchmark.structures:
    print(f"  {rna.name}: {rna.length} nt, {rna.num_pairs} bp")
```

### 11.3 Benchmark Evaluation

```python
# Evaluate a predictor on benchmark
benchmark = rf.load_benchmark("trna")

results = []
for ref in benchmark.structures:
    pred = rf.predict_structure(ref.sequence, method="fallback")
    
    f1 = rf.f1_score(ref, pred)
    results.append({
        'name': ref.name,
        'f1': f1
    })

# Calculate average performance
avg_f1 = sum(r['f1'] for r in results) / len(results)
print(f"Average F1: {avg_f1:.3f}")
```

### 11.4 Using External Benchmarks

```python
# Load from Archive II format (Mathews lab)
structures = rf.load_structure("archive2_dataset.ct")

# Load from RNA STRAND
structures = rf.load_structure("rnastrand.bpseq")
```

---

## 12. API Reference

### 12.1 Main Functions

```python
import rnaview as rf

# I/O
rf.load_structure(filepath, format=None)
rf.save_structure(structure, filepath, format=None)
rf.to_ct(structure)
rf.to_bpseq(structure)
rf.to_dotbracket(structure)

# Visualization
rf.plot2d(structure, layout="radiate", **kwargs)
rf.plot_arc(structure, **kwargs)
rf.plot_circular(structure, **kwargs)
rf.plot_radiate(structure, **kwargs)
rf.plot3d(structure, style="backbone", **kwargs)

# Analysis
rf.sensitivity(reference, predicted)
rf.ppv(reference, predicted)
rf.f1_score(reference, predicted)
rf.mcc(reference, predicted)
rf.compare_structures(ref, pred)

# Features
rf.find_helices(structure)
rf.find_loops(structure)
rf.find_pseudoknots(structure)

# Prediction
rf.predict_structure(sequence, method="auto")
rf.list_predictors(available_only=False)

# Benchmarks
rf.load_benchmark(name)
rf.list_benchmarks()
```

### 12.2 Classes

```python
from rnaview import (
    RNAStructure,    # Main structure class
    RNASequence,     # Sequence handling
    BasePair,        # Base pair representation
    Helix,           # Helical region
    Loop,            # Loop region
    Pseudoknot,      # Pseudoknot structure
    Modification,    # RNA modification
    ModificationSite,# Modification at position
    ColorScheme,     # Visualization colors
    BenchmarkDataset # Benchmark container
)
```

### 12.3 Utilities

```python
from rnaview.utils import (
    validate_sequence,
    validate_structure,
    dotbracket_to_pairs,
    pairs_to_dotbracket,
    calculate_gc_content,
    reverse_complement
)
```

---

## 13. Troubleshooting

### 13.1 Common Issues

**Import Error: No module named 'rnaview'**
```bash
# Make sure RNAview is installed
pip install rnaview

# Or for development
pip install -e .
```

**Visualization not working**
```bash
# Install visualization dependencies
pip install matplotlib plotly scipy
```

**ViennaRNA not found**
```bash
# Install ViennaRNA Package
conda install -c bioconda viennarna
# Or from source: https://www.tbi.univie.ac.at/RNA/
```

**Structure length mismatch**
```python
# Ensure sequence and structure have same length
assert len(sequence) == len(dotbracket)
```

**Unbalanced brackets**
```python
# Validate structure before creating
from rnaview.utils import validate_structure
validate_structure(dotbracket)  # Raises ValueError if invalid
```

### 13.2 Performance Tips

1. **Large structures**: Use arc diagrams for RNAs > 500 nt
2. **Batch processing**: Use `predict_multiple()` for many sequences
3. **3D visualization**: Use `backend="matplotlib"` for static images
4. **Memory**: Close matplotlib figures with `plt.close()` in loops

---

## 14. Examples

### 14.1 Complete Workflow Example

```python
import rnaview as rf
import matplotlib.pyplot as plt

# 1. Load reference structure
reference = rf.load_structure("trna.ct")
print(f"Loaded: {reference.name}, {reference.length} nt")

# 2. Add known modifications
reference.add_modification(31, rf.Modification.pseudouridine())
reference.add_modification(54, rf.Modification.m5C())

# 3. Predict structure
predicted = rf.predict_structure(reference.sequence)

# 4. Compare structures
sens = rf.sensitivity(reference, predicted)
ppv = rf.ppv(reference, predicted)
f1 = rf.f1_score(reference, predicted)
mcc = rf.mcc(reference, predicted)

print(f"Sensitivity: {sens:.3f}")
print(f"PPV: {ppv:.3f}")
print(f"F1: {f1:.3f}")
print(f"MCC: {mcc:.3f}")

# 5. Visualize comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

rf.plot2d(reference, ax=axes[0], title="Reference")
rf.plot2d(predicted, ax=axes[1], title="Predicted")

fig.suptitle(f"Structure Comparison (F1={f1:.3f})")
plt.savefig("comparison.png", dpi=300)
```

### 14.2 Batch Prediction Example

```python
import rnaview as rf

# Sequences to predict
sequences = [
    "GCGCUUAAGCGC",
    "GGCCAAAGGCC",
    "AUGCUAGCUAGC"
]

# Predict all
for seq in sequences:
    rna = rf.predict_structure(seq)
    print(f"{seq[:10]}... -> {rna.to_dotbracket()}")
```

### 14.3 Modification Analysis Example

```python
import rnaview as rf
from rnaview.core.modifications import find_modification_motifs, ModificationType

# Load sequence
rna = rf.RNAStructure(
    sequence="GGACUAACUGAACUGGACUAACUG",
    dotbracket="........................"
)

# Find potential m6A sites
m6a_sites = find_modification_motifs(rna.sequence, ModificationType.M6A)

# Add modifications
for pos in m6a_sites:
    rna.add_modification(pos, rf.Modification.m6A())

# Visualize
fig = rf.plot_arc(rna, show_modifications=True)
fig.savefig("m6a_sites.png")

print(f"Found {len(m6a_sites)} potential m6A sites")
```

---

## License

RNAview is released under the MIT License.

## Citation

If you use RNAview in your research, please cite:

```bibtex
@software{rnaview2025,
  title = {RNAview: A Python Package for RNA Structure Visualization and Analysis},
  author = {RNAview Development Team},
  year = {2025},
  url = {https://github.com/rnaview/rnaview}
}
```

## Support

- Documentation: https://rnaview.readthedocs.io
- Issues: https://github.com/rnaview/rnaview/issues
- Discussions: https://github.com/rnaview/rnaview/discussions

---

*RNAview User Manual v1.0.0*
