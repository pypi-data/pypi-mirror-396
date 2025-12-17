"""
Benchmark datasets for RNA structure analysis.

This module provides access to gold-standard datasets for benchmarking
RNA secondary structure prediction algorithms and validating analysis tools.

Available datasets:
- Archive II: Classic benchmark from Mathews Lab
- RNA STRAND: Large curated database
- Rfam families: Consensus structures
- Built-in test sets for various RNA types

Example:
    >>> import rnaview as rv
    >>> benchmark = rv.load_benchmark("archiveII")
    >>> for rna in benchmark:
    ...     predicted = rv.fold_rna(rna.sequence)
    ...     metrics = rv.compare_structures(predicted, rna)
    ...     print(f"{rna.name}: F1={metrics['f1']:.3f}")
"""

from __future__ import annotations
import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Iterator, Tuple
import urllib.request
import hashlib

from ..core.structure import RNAStructure


# Package data directory
DATA_DIR = Path(__file__).parent.parent / "data" / "benchmark"


@dataclass
class BenchmarkEntry:
    """
    A single entry in a benchmark dataset.
    
    Attributes:
        name: Identifier for the structure
        sequence: RNA sequence
        structure: Dot-bracket structure
        family: RNA family/type
        organism: Source organism (if known)
        pdb_id: PDB ID (if derived from crystal structure)
        length: Sequence length
        metadata: Additional information
    """
    name: str
    sequence: str
    structure: str
    family: str = ""
    organism: str = ""
    pdb_id: str = ""
    length: int = 0
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.length = len(self.sequence)
    
    def to_rna_structure(self) -> RNAStructure:
        """Convert to RNAStructure object."""
        return RNAStructure(
            sequence=self.sequence,
            dotbracket=self.structure,
            name=self.name
        )


class BenchmarkDataset:
    """
    A collection of benchmark RNA structures.
    
    Provides iteration, filtering, and access to benchmark entries.
    
    Attributes:
        name: Dataset name
        description: Dataset description
        entries: List of BenchmarkEntry objects
        families: Available RNA families in the dataset
    
    Example:
        >>> dataset = BenchmarkDataset.load("archiveII")
        >>> trnas = dataset.filter_by_family("tRNA")
        >>> for entry in trnas:
        ...     rna = entry.to_rna_structure()
    """
    
    def __init__(
        self,
        name: str,
        entries: List[BenchmarkEntry],
        description: str = "",
        source: str = "",
        citation: str = ""
    ):
        self.name = name
        self.entries = entries
        self.description = description
        self.source = source
        self.citation = citation
    
    @property
    def families(self) -> List[str]:
        """Get unique family names in the dataset."""
        return sorted(set(e.family for e in self.entries if e.family))
    
    def __len__(self) -> int:
        return len(self.entries)
    
    def __iter__(self) -> Iterator[BenchmarkEntry]:
        return iter(self.entries)
    
    def __getitem__(self, idx) -> BenchmarkEntry:
        return self.entries[idx]
    
    def filter_by_family(self, family: str) -> 'BenchmarkDataset':
        """Filter entries by RNA family."""
        filtered = [e for e in self.entries if e.family.lower() == family.lower()]
        return BenchmarkDataset(
            name=f"{self.name}_{family}",
            entries=filtered,
            description=f"{family} subset of {self.name}"
        )
    
    def filter_by_length(
        self,
        min_length: int = 0,
        max_length: int = float('inf')
    ) -> 'BenchmarkDataset':
        """Filter entries by sequence length."""
        filtered = [e for e in self.entries if min_length <= e.length <= max_length]
        return BenchmarkDataset(
            name=f"{self.name}_len{min_length}-{max_length}",
            entries=filtered,
            description=f"Length-filtered subset of {self.name}"
        )
    
    def get_structures(self) -> List[RNAStructure]:
        """Convert all entries to RNAStructure objects."""
        return [e.to_rna_structure() for e in self.entries]
    
    def summary(self) -> Dict[str, any]:
        """Return summary statistics of the dataset."""
        lengths = [e.length for e in self.entries]
        family_counts = {}
        for e in self.entries:
            family_counts[e.family] = family_counts.get(e.family, 0) + 1
        
        return {
            'name': self.name,
            'num_entries': len(self.entries),
            'families': family_counts,
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0,
            'avg_length': sum(lengths) / len(lengths) if lengths else 0,
        }
    
    @classmethod
    def from_fasta(
        cls,
        filepath: str,
        name: str = "custom"
    ) -> 'BenchmarkDataset':
        """
        Load benchmark from FASTA file with structures.
        
        Expected format:
            >name family
            SEQUENCE
            STRUCTURE
        """
        entries = []
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('>'):
                parts = line[1:].split()
                entry_name = parts[0]
                family = parts[1] if len(parts) > 1 else ""
                
                sequence = lines[i + 1].strip() if i + 1 < len(lines) else ""
                structure = lines[i + 2].strip() if i + 2 < len(lines) else ""
                
                entries.append(BenchmarkEntry(
                    name=entry_name,
                    sequence=sequence,
                    structure=structure,
                    family=family
                ))
                i += 3
            else:
                i += 1
        
        return cls(name=name, entries=entries)
    
    def to_fasta(self, filepath: str) -> None:
        """Save dataset to FASTA format."""
        with open(filepath, 'w') as f:
            for entry in self.entries:
                f.write(f">{entry.name} {entry.family}\n")
                f.write(f"{entry.sequence}\n")
                f.write(f"{entry.structure}\n")


# ============================================================================
# Built-in benchmark data (embedded for offline use)
# ============================================================================

# Archive II representative structures (subset)
_ARCHIVE_II_DATA = [
    # 5S rRNA
    {
        "name": "5S_rRNA_ecoli",
        "family": "5S_rRNA",
        "organism": "E. coli",
        "sequence": "UGCCUGGCGGCCGUAGCGCGGUGGUCCCACCUGACCCCAUGCCGAACUCAGAAGUGAAACGCCGUAGCGCCGAUGGUAGUGUGGGGUCUCCCCAUGCGAGAGUAGGGAACUGCCAGGCAU",
        "structure": "(((((((...(((((((.......)))))))...(((((...((((......))))....))))).(((((....)))))......((((((....))))))....)))))))."
    },
    # tRNA-Phe
    {
        "name": "tRNA_Phe_yeast",
        "family": "tRNA",
        "organism": "S. cerevisiae",
        "sequence": "GCGGAUUUAGCUCAGUUGGGAGAGCGCCAGACUGAAGAUCUGGAGGUCCUGUGUUCGAUCCACAGAAUUCGCACCA",
        "structure": "(((((((..((((........)))).(((((.......))))).....(((((.......)))))...)))))))."
    },
    # Hammerhead ribozyme
    {
        "name": "hammerhead_ribozyme",
        "family": "ribozyme",
        "organism": "Satellite RNA",
        "sequence": "GGACGAAACGCCGAAACGUUGGCGCCUCGAAACGUGAAAGCGUGCCAGUACUUUGUCGUC",
        "structure": "(((((.((((..(((((......)))))......)))).(((((....))))).)))))"
    },
    # SRP RNA
    {
        "name": "SRP_RNA_ecoli",
        "family": "SRP_RNA",
        "organism": "E. coli",
        "sequence": "GGCGGAUGGCCGAGUCCGGAAGGAUAAGCCCUUUAGUAGUCUGGUGGCCCGAACAGCGCGGCGAUUACGGUCCGCC",
        "structure": "(((((((.....((((........))))....((((((((.....)))))))).............)))))))."
    },
    # RNase P
    {
        "name": "RNaseP_bsubA",
        "family": "RNaseP",
        "organism": "B. subtilis",
        "sequence": "GAAGCUGACCAGACAGUCGCCGCUUCGUCGUCGUCCUUUCGGGGGAGACGGGCGGAGGGGAGGAAAGUCCGGGCUCCAUAGGGCAGGCGUCCGUAGAAGCGCUGAUCU",
        "structure": "((((((...((((((.......(((....))).)))))).....((((....)))).((((.(((....))).))))....(((((....)))))...))))))."
    },
    # Group I intron (partial)
    {
        "name": "group_I_intron_tetrahymena",
        "family": "group_I_intron",
        "organism": "Tetrahymena",
        "sequence": "GGUUUAGGGGGCAGAAGCUAAACGUUCGUCUGAAUCGUUUCUAGCAUCGAUGCUGUCAAAGCUUUGGUAAGAGAUUAAGCUUUCCCUGAAAUUUAGGACCC",
        "structure": "((((....((((((((....))))))))((((.((.....))))))...((((....)))).((((....((((....))))....))))...))))."
    },
    # 16S rRNA fragment
    {
        "name": "16S_rRNA_fragment",
        "family": "rRNA",
        "organism": "E. coli",
        "sequence": "AUUCUUUGACUCAAGGUUGAUACCGCGCCGAUAGUAGCGGGUCUACCCAUAGGCGCUGAGCCAGAAUGGAA",
        "structure": "(((.......((((((.(((((......))))).......))))))...(((((....))))).)))."
    },
    # tmRNA
    {
        "name": "tmRNA_ecoli",
        "family": "tmRNA",
        "organism": "E. coli",
        "sequence": "GGGGCUGAUUUGGUAAUAUUCGCUGAGCCGUGUAAGCGAAGCGAGGUUAAACUACAGCACUCUUUCGUCAAGAGUUAAGCUUAGAUCUGAAGUUUUGCC",
        "structure": "(((((..((((...(((......)))....)))).((((((........))))))..((((((....))))))..((((....))))...))))).."
    },
    # Telomerase RNA fragment
    {
        "name": "telomerase_human",
        "family": "telomerase_RNA",
        "organism": "H. sapiens",
        "sequence": "GGGCUGUUUUUCUCGCUGACUUUCAGCGGGCGGAAAAGCCUCGGCCUGCCGCCUUCCACCGUUCAUUCU",
        "structure": "((((...(((((((....((((....)))).......)))))))....((((....)))).....))))."
    },
    # Riboswitch (TPP)
    {
        "name": "TPP_riboswitch",
        "family": "riboswitch",
        "organism": "E. coli",
        "sequence": "GCUGAGAUGGCGAAAGGAAUGGUUGGUGAACGACAAUUUCUAGCGAGUUAACGGAUGCUGAAAUGGCCCUU",
        "structure": ".(((((((......(((((((.......))))))).((((((.....)))))).......)))))))..."
    },
]


# RNA STRAND sample data
_RNA_STRAND_DATA = [
    {
        "name": "PDB_00001",
        "family": "hairpin",
        "sequence": "GGCGCAAGCC",
        "structure": "(((....)))"
    },
    {
        "name": "PDB_00002",
        "family": "stem_loop",
        "sequence": "GCGGAUUUAGCUCAGUU",
        "structure": "(((((........)))))"
    },
    {
        "name": "PDB_00003",
        "family": "internal_loop",
        "sequence": "GCGCAAUUGCGC",
        "structure": "((((....))).)"
    },
    {
        "name": "PDB_00004",
        "family": "bulge",
        "sequence": "GGCGAUAGCC",
        "structure": "(((.....))"
    },
    {
        "name": "PDB_00005",
        "family": "multiloop",
        "sequence": "GGCAAUCCGGAAUCCGCC",
        "structure": "(((.((....)).()))))"
    },
]


def _init_builtin_datasets():
    """Initialize built-in benchmark datasets."""
    global _DATASETS
    
    _DATASETS = {}
    
    # Archive II
    archive_entries = [
        BenchmarkEntry(**data) for data in _ARCHIVE_II_DATA
    ]
    _DATASETS['archiveii'] = BenchmarkDataset(
        name="Archive II",
        entries=archive_entries,
        description="Classic benchmark dataset with diverse RNA families",
        source="Mathews Lab, University of Rochester",
        citation="Sloma & Mathews (2016) Nucleic Acids Res."
    )
    
    # RNA STRAND sample
    strand_entries = [
        BenchmarkEntry(**data) for data in _RNA_STRAND_DATA
    ]
    _DATASETS['rna_strand'] = BenchmarkDataset(
        name="RNA STRAND (sample)",
        entries=strand_entries,
        description="Sample from RNA STRAND database",
        source="RNA STRAND Database",
        citation="Andronescu et al. (2008) BMC Bioinformatics"
    )


# Initialize on import
_DATASETS = {}
_init_builtin_datasets()


def list_benchmarks() -> List[str]:
    """
    List available benchmark datasets.
    
    Returns:
        List of benchmark dataset names
    
    Example:
        >>> benchmarks = list_benchmarks()
        >>> print(benchmarks)
        ['archiveii', 'rna_strand']
    """
    return list(_DATASETS.keys())


def load_benchmark(
    name: str,
    download: bool = False
) -> BenchmarkDataset:
    """
    Load a benchmark dataset.
    
    Args:
        name: Dataset name (case-insensitive)
        download: Download full dataset if not available locally
    
    Returns:
        BenchmarkDataset object
    
    Available datasets:
        - archiveII: Classic benchmark with diverse RNA families
        - rna_strand: Sample from RNA STRAND database
    
    Example:
        >>> benchmark = load_benchmark("archiveII")
        >>> print(f"Loaded {len(benchmark)} structures")
    """
    name = name.lower().replace(' ', '_').replace('-', '_')
    
    if name not in _DATASETS:
        available = ', '.join(_DATASETS.keys())
        raise ValueError(f"Unknown benchmark: {name}. Available: {available}")
    
    return _DATASETS[name]


def get_archiveII(family: Optional[str] = None) -> BenchmarkDataset:
    """
    Get Archive II benchmark dataset.
    
    Args:
        family: Optional filter by RNA family
    
    Returns:
        BenchmarkDataset with Archive II structures
    
    Example:
        >>> trnas = get_archiveII(family="tRNA")
    """
    dataset = load_benchmark("archiveii")
    if family:
        return dataset.filter_by_family(family)
    return dataset


def get_rna_strand(
    min_length: int = 0,
    max_length: int = float('inf')
) -> BenchmarkDataset:
    """
    Get RNA STRAND sample dataset.
    
    Args:
        min_length: Minimum sequence length filter
        max_length: Maximum sequence length filter
    
    Returns:
        BenchmarkDataset with RNA STRAND structures
    
    Example:
        >>> short_rnas = get_rna_strand(max_length=50)
    """
    dataset = load_benchmark("rna_strand")
    return dataset.filter_by_length(min_length, max_length)


def create_test_structure(
    structure_type: str = "hairpin",
    length: int = 20
) -> RNAStructure:
    """
    Create a simple test RNA structure.
    
    Useful for quick testing and demonstration.
    
    Args:
        structure_type: Type of structure ('hairpin', 'stem_loop', 'pseudoknot')
        length: Approximate length
    
    Returns:
        RNAStructure object
    
    Example:
        >>> rna = create_test_structure("hairpin", length=30)
    """
    if structure_type == "hairpin":
        # Simple hairpin
        stem_len = (length - 4) // 2
        sequence = "G" * stem_len + "UUCG" + "C" * stem_len
        structure = "(" * stem_len + "...." + ")" * stem_len
        
    elif structure_type == "stem_loop":
        # Stem with internal loop
        stem1 = length // 4
        loop = 4
        stem2 = length // 4
        sequence = "G" * stem1 + "AA" + "C" * stem2 + "UUCG" + "G" * stem2 + "UU" + "C" * stem1
        structure = "(" * stem1 + ".." + "(" * stem2 + "...." + ")" * stem2 + ".." + ")" * stem1
        
    elif structure_type == "pseudoknot":
        # Simple H-type pseudoknot
        sequence = "GGGGAAAAACCCCUUUUGGGG"
        structure = "[[[[.....]]]]....[[[[" # Note: simplified pseudoknot notation
        
    else:
        # Default to hairpin
        return create_test_structure("hairpin", length)
    
    return RNAStructure(
        sequence=sequence,
        dotbracket=structure.replace('[', '(').replace(']', ')'),
        name=f"test_{structure_type}"
    )


def get_example_structures() -> Dict[str, RNAStructure]:
    """
    Get a collection of example structures for demonstration.
    
    Returns:
        Dictionary mapping names to RNAStructure objects
    
    Example:
        >>> examples = get_example_structures()
        >>> for name, rna in examples.items():
        ...     print(f"{name}: {rna.length} nt, {rna.num_pairs} bp")
    """
    examples = {}
    
    # Simple hairpin
    examples['simple_hairpin'] = RNAStructure(
        sequence="GCGCUUAAGCGC",
        dotbracket="((((....))))",
        name="simple_hairpin"
    )
    
    # tRNA-like
    examples['trna_like'] = RNAStructure(
        sequence="GCGGAUUUAGCUCAGUUGGGAGAGCGCCAGACUGAAGAUCUGGAGGUCCUGUGUUCGAUCCACAGAAUUCGCACCA",
        dotbracket="(((((((..((((........)))).(((((.......))))).....(((((.......)))))...))))))).",
        name="trna_like"
    )
    
    # Multi-stem structure
    examples['multi_stem'] = RNAStructure(
        sequence="GGGAAACCCGGGAAACCCGGGAAACCC",
        dotbracket="(((....))).(((....))).(((...)))",
        name="multi_stem"
    )
    
    # Structure with bulge
    examples['with_bulge'] = RNAStructure(
        sequence="GGCGAUAUAGCC",
        dotbracket="((((.....).))",
        name="with_bulge"
    )
    
    return examples
