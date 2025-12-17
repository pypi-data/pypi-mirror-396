# RNAview

<p align="center">
  <strong>A Comprehensive Python Package for RNA Structure Visualization and Analysis</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/rnaview/"><img src="https://img.shields.io/pypi/v/rnaview.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/rnaview/"><img src="https://img.shields.io/pypi/pyversions/rnaview.svg" alt="Python versions"></a>
  <a href="https://github.com/kroy3/rnaview/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
</p>

---

**RNAview** is a powerful, user-friendly Python library designed for researchers to visualize, analyze, and explore RNA secondary and tertiary structures. It provides seamless integration with established RNA structure prediction tools and includes gold-standard benchmark datasets for validation.

## 📸 Gallery

### Multiple Visualization Layouts

<p align="center">
  <img src="docs/images/layouts_comparison.png" alt="Layout Comparison" width="800"/>
</p>

RNAview supports radiate and circular layouts for both simple hairpins and complex structures like tRNA.

### Arc Diagram Representations

<p align="center">
  <img src="docs/images/arc_diagrams.png" alt="Arc Diagrams" width="800"/>
</p>

Visualize RNA structures as arc diagrams - perfect for publications and showing base-pairing patterns clearly. Works seamlessly with hairpins, tRNA, and even complex pseudoknots.

### Customizable Color Schemes

<p align="center">
  <img src="docs/images/color_schemes.png" alt="Color Schemes" width="800"/>
</p>

Choose from multiple color schemes including nucleotide-based, ViennaRNA-style, pastel, colorblind-friendly, monochrome, and publication-ready options.

### Structure Comparison with Metrics

<p align="center">
  <img src="docs/images/comparison.png" alt="Structure Comparison" width="800"/>
</p>

Compare predicted and reference structures with comprehensive accuracy metrics (Sensitivity, PPV, F1 Score, MCC).

### RNA Modification Support

<p align="center">
  <img src="docs/images/modifications.png" alt="RNA Modifications" width="800"/>
</p>

Full support for highlighting RNA modifications including m6A, m5C, pseudouridine, and 70+ other modifications.

### Publication-Quality Figures

<p align="center">
  <img src="docs/images/publication_figure.png" alt="Publication Figure" width="800"/>
</p>

Create multi-panel publication-ready figures combining different visualization styles and RNA structures.

## ✨ Key Features

- 📊 **Multiple Visualization Layouts**: Radiate, circular, NAView, arc diagrams, and 3D views
- 🎨 **Customizable Color Schemes**: Nucleotide-based, colorblind-friendly, publication-ready
- 🧬 **RNA Modifications**: Full support for m6A, m5C, pseudouridine, and 70+ other modifications
- 📈 **Comprehensive Analysis**: Sensitivity, PPV, F1, MCC, and structural distance metrics
- 🔗 **Tool Integration**: ViennaRNA, LinearFold, CONTRAfold, and more
- 📁 **Multiple File Formats**: CT, BPSEQ, dot-bracket, PDB, mmCIF, FASTA, Stockholm
- 📚 **Benchmark Datasets**: Curated tRNA, 5S rRNA, and small RNA datasets

## 🚀 Installation

### From PyPI

```bash
pip install rnaview
```

### With Visualization Support

```bash
pip install rnaview[visualization]
```

### Full Installation

```bash
pip install rnaview[full]
```

### From Source

```bash
git clone https://github.com/kroy3/rnaview.git
cd rnaview
pip install -e .
```

## 📖 Quick Start

### Creating and Visualizing an RNA Structure

```python
import rnaview as rv

# Create from sequence and dot-bracket notation
rna = rv.RNAStructure(
    sequence="GCGCUUAAGCGC",
    dotbracket="((((....))))",
    name="Simple_hairpin"
)

# Visualize in 2D
fig = rv.plot2d(rna, layout="radiate", color_scheme="nucleotide")
fig.savefig("structure.png")

# Print structure summary
print(rna.summary())
```

### Loading from Files

```python
import rnaview as rv

# Auto-detect format from extension
rna = rv.load_structure("structure.ct")
rna = rv.load_structure("structure.dbn")
rna = rv.load_structure("structure.pdb")
```

### Structure Prediction

```python
import rnaview as rv

# Predict structure (uses best available method)
sequence = "GCGCUUAAGCGC"
rna = rv.predict_structure(sequence)

# Use specific predictor
rna = rv.predict_structure(sequence, method="viennarna", temperature=37)
```

### Creating Arc Diagrams

```python
import rnaview as rv

rna = rv.load_structure("trna.ct")

# Create arc diagram
fig = rv.plot_arc(rna, show_sequence=True, color_scheme="nucleotide")
fig.savefig("trna_arc.png")
```

### Adding RNA Modifications

```python
import rnaview as rv

rna = rv.RNAStructure(
    sequence="GCGCUUAAGCGC",
    dotbracket="((((....))))"
)

# Add modifications
rna.add_modification(4, rv.Modification.m6A())
rna.add_modification(5, rv.Modification.pseudouridine())

# Visualize with modifications highlighted
fig = rv.plot2d(rna, show_modifications=True)
```

### Comparing Structures

```python
import rnaview as rv

reference = rv.load_structure("reference.ct")
predicted = rv.load_structure("predicted.ct")

# Calculate accuracy metrics
sensitivity = rv.sensitivity(reference, predicted)
ppv = rv.ppv(reference, predicted)
f1 = rv.f1_score(reference, predicted)
mcc = rv.mcc(reference, predicted)

print(f"Sensitivity: {sensitivity:.3f}")
print(f"PPV: {ppv:.3f}")
print(f"F1 Score: {f1:.3f}")
print(f"MCC: {mcc:.3f}")

# Visualize comparison
fig = rv.plot_comparison(reference, predicted)
fig.savefig("comparison.png")
```

## 📁 Supported File Formats

| Format | Extension | Read | Write | Description |
|--------|-----------|------|-------|-------------|
| Dot-bracket | .dbn, .db | ✅ | ✅ | Standard secondary structure notation |
| CT | .ct | ✅ | ✅ | Connectivity table format |
| BPSEQ | .bpseq | ✅ | ✅ | Base pair sequence format |
| PDB | .pdb | ✅ | ❌ | 3D structure format |
| mmCIF | .cif | ✅ | ❌ | Macromolecular CIF |
| FASTA | .fasta, .fa | ✅ | ✅ | Sequence format |
| Stockholm | .sto | ✅ | ❌ | Alignment format with structure |

## 🔌 Integration with Prediction Tools

| Tool | Type | Status |
|------|------|--------|
| ViennaRNA (RNAfold) | Thermodynamic | ✅ Supported |
| LinearFold | Linear-time | ✅ Supported |
| CONTRAfold | Machine Learning | ✅ Supported |
| Fallback (built-in) | Basic DP | ✅ Always available |

## 🎨 Available Color Schemes

- **nucleotide**: Standard nucleotide colors (A=red, U=orange, G=green, C=blue)
- **varna**: ViennaRNA-style coloring
- **pastel**: Soft pastel colors for presentations
- **colorblind**: Colorblind-friendly palette
- **monochrome**: Grayscale for publications
- **publication**: High-contrast publication-ready colors

## 📚 Documentation

Full documentation is available at [https://rnaview.readthedocs.io](https://rnaview.readthedocs.io)

See also the [User Manual](docs/USER_MANUAL.md) for comprehensive guides.

## 🤝 Contributing

Contributions are welcome! Please see our contributing guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📖 Citation

If you use RNAview in your research, please cite:

```bibtex
@software{rnaview2025,
  title = {RNAview: A Python Package for RNA Structure Visualization and Analysis},
  author = {RNAview Development Team},
  year = {2025},
  url = {https://github.com/kroy3/rnaview}
}
```

## 🙏 Acknowledgments

- ViennaRNA package for thermodynamic calculations
- The RNA research community for valuable feedback
- Contributors and users who help improve RNAview

---

<p align="center">
  Made with ❤️ for the RNA research community
</p>
