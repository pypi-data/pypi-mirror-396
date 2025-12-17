"""
ViennaRNA Package integration.

This module provides integration with the ViennaRNA Package for
RNA secondary structure prediction and thermodynamic calculations.

ViennaRNA must be installed separately:
    pip install ViennaRNA
    # or
    conda install -c bioconda viennarna

Features:
- MFE structure prediction
- Partition function calculation
- Suboptimal structure enumeration
- Centroid structure calculation
- SHAPE-directed folding

Example:
    >>> import rnaview as rv
    >>> sequence = "GCGCUUAAGCGC"
    >>> structure = rv.fold_rna(sequence)
    >>> print(structure)
    GCGCUUAAGCGC
    ((((....))))
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Union
import subprocess
import tempfile
import os

from ..core.structure import RNAStructure


# Check for ViennaRNA availability
try:
    import RNA
    HAS_VIENNARNA = True
except ImportError:
    HAS_VIENNARNA = False


def _check_viennarna():
    """Check if ViennaRNA is available."""
    if not HAS_VIENNARNA:
        raise ImportError(
            "ViennaRNA is required for this function. "
            "Install with: pip install ViennaRNA or conda install -c bioconda viennarna"
        )


def fold_rna(
    sequence: str,
    constraint: Optional[str] = None,
    temperature: float = 37.0,
    name: Optional[str] = None
) -> RNAStructure:
    """
    Predict RNA secondary structure using MFE folding.
    
    Uses ViennaRNA's RNAfold algorithm to predict the minimum
    free energy (MFE) structure.
    
    Args:
        sequence: RNA sequence (A, C, G, U)
        constraint: Optional structure constraint in dot-bracket
        temperature: Folding temperature in Celsius
        name: Optional name for the returned structure
    
    Returns:
        RNAStructure with predicted structure and energy
    
    Example:
        >>> rna = fold_rna("GCGCUUAAGCGC")
        >>> print(rna.to_dotbracket())
        ((((....))))
    """
    _check_viennarna()
    
    # Set temperature
    RNA.cvar.temperature = temperature
    
    # Create fold compound
    if constraint:
        fc = RNA.fold_compound(sequence)
        fc.constraints_add(constraint, RNA.CONSTRAINT_DB_DEFAULT)
    else:
        fc = RNA.fold_compound(sequence)
    
    # Calculate MFE
    structure, mfe = fc.mfe()
    
    # Create RNAStructure
    rna = RNAStructure(
        sequence=sequence,
        dotbracket=structure,
        name=name or "folded"
    )
    rna.metadata['mfe'] = mfe
    rna.metadata['temperature'] = temperature
    
    return rna


def mfe_structure(
    sequence: str,
    constraint: Optional[str] = None,
    temperature: float = 37.0
) -> Tuple[str, float]:
    """
    Get MFE structure and energy.
    
    Args:
        sequence: RNA sequence
        constraint: Optional structure constraint
        temperature: Temperature in Celsius
    
    Returns:
        Tuple of (dot-bracket structure, MFE in kcal/mol)
    
    Example:
        >>> structure, energy = mfe_structure("GCGCUUAAGCGC")
        >>> print(f"Structure: {structure}, ΔG = {energy:.2f} kcal/mol")
    """
    _check_viennarna()
    
    RNA.cvar.temperature = temperature
    
    if constraint:
        fc = RNA.fold_compound(sequence)
        fc.constraints_add(constraint, RNA.CONSTRAINT_DB_DEFAULT)
        structure, mfe = fc.mfe()
    else:
        structure, mfe = RNA.fold(sequence)
    
    return structure, mfe


def partition_function(
    sequence: str,
    temperature: float = 37.0
) -> Dict[str, any]:
    """
    Calculate partition function and ensemble properties.
    
    Args:
        sequence: RNA sequence
        temperature: Temperature in Celsius
    
    Returns:
        Dictionary with ensemble free energy, base pair probabilities, etc.
    
    Example:
        >>> pf = partition_function("GCGCUUAAGCGC")
        >>> print(f"Ensemble ΔG = {pf['ensemble_energy']:.2f} kcal/mol")
    """
    _check_viennarna()
    
    RNA.cvar.temperature = temperature
    
    fc = RNA.fold_compound(sequence)
    
    # Calculate partition function
    ensemble_struct, ensemble_energy = fc.pf()
    
    # Get base pair probability matrix
    bpp = []
    n = len(sequence)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            prob = fc.pr(i, j)
            if prob > 0.01:  # Only store significant probabilities
                bpp.append((i - 1, j - 1, prob))  # Convert to 0-indexed
    
    # Calculate centroid structure
    centroid, dist = fc.centroid()
    
    return {
        'ensemble_structure': ensemble_struct,
        'ensemble_energy': ensemble_energy,
        'base_pair_probabilities': bpp,
        'centroid_structure': centroid,
        'centroid_distance': dist,
    }


def suboptimal_structures(
    sequence: str,
    delta_energy: float = 5.0,
    max_structures: int = 100,
    temperature: float = 37.0
) -> List[Tuple[str, float]]:
    """
    Enumerate suboptimal structures within energy range.
    
    Uses ViennaRNA's RNAsubopt algorithm.
    
    Args:
        sequence: RNA sequence
        delta_energy: Energy range above MFE in kcal/mol
        max_structures: Maximum number of structures to return
        temperature: Temperature in Celsius
    
    Returns:
        List of (structure, energy) tuples sorted by energy
    
    Example:
        >>> subopt = suboptimal_structures("GCGCUUAAGCGC", delta_energy=3.0)
        >>> for struct, energy in subopt[:5]:
        ...     print(f"{struct}: {energy:.2f} kcal/mol")
    """
    _check_viennarna()
    
    RNA.cvar.temperature = temperature
    
    fc = RNA.fold_compound(sequence)
    fc.pf()
    
    # Get suboptimal structures
    subopt_list = []
    
    # Use Wuchty algorithm
    fc.subopt(int(delta_energy * 100), lambda s, e: subopt_list.append((s, e)))
    
    # Sort by energy and limit
    subopt_list.sort(key=lambda x: x[1])
    return subopt_list[:max_structures]


def shape_directed_fold(
    sequence: str,
    shape_data: List[float],
    temperature: float = 37.0,
    shape_intercept: float = -0.6,
    shape_slope: float = 1.8
) -> RNAStructure:
    """
    SHAPE-directed RNA folding.
    
    Uses SHAPE reactivity data as soft constraints for structure prediction.
    
    Args:
        sequence: RNA sequence
        shape_data: List of SHAPE reactivity values (one per nucleotide)
        temperature: Temperature in Celsius
        shape_intercept: SHAPE constraint intercept parameter
        shape_slope: SHAPE constraint slope parameter
    
    Returns:
        RNAStructure with SHAPE-directed prediction
    
    Example:
        >>> shape = [0.1, 0.2, 0.8, 0.9, ...]  # Reactivity values
        >>> rna = shape_directed_fold(sequence, shape)
    """
    _check_viennarna()
    
    if len(shape_data) != len(sequence):
        raise ValueError("SHAPE data length must match sequence length")
    
    RNA.cvar.temperature = temperature
    
    fc = RNA.fold_compound(sequence)
    
    # Add SHAPE constraints
    fc.sc_add_SHAPE_deigan(shape_data, shape_intercept, shape_slope)
    
    # Fold with constraints
    structure, mfe = fc.mfe()
    
    rna = RNAStructure(
        sequence=sequence,
        dotbracket=structure,
        name="shape_directed"
    )
    rna.metadata['mfe'] = mfe
    rna.metadata['shape_constrained'] = True
    rna.set_reactivity(shape_data)
    
    return rna


def cofold(
    sequence1: str,
    sequence2: str,
    temperature: float = 37.0
) -> Tuple[RNAStructure, float]:
    """
    Predict structure of two interacting RNA sequences.
    
    Uses ViennaRNA's RNAcofold algorithm.
    
    Args:
        sequence1: First RNA sequence
        sequence2: Second RNA sequence
        temperature: Temperature in Celsius
    
    Returns:
        Tuple of (RNAStructure, interaction energy)
    
    Example:
        >>> complex_struct, energy = cofold("GGGGAAAA", "UUUUCCCC")
    """
    _check_viennarna()
    
    RNA.cvar.temperature = temperature
    
    # Combine sequences with separator
    combined = sequence1 + "&" + sequence2
    
    # Fold
    structure, mfe = RNA.cofold(combined)
    
    # Split structure back
    struct1, struct2 = structure.split("&")
    
    rna = RNAStructure(
        sequence=sequence1 + sequence2,
        name="cofold_complex"
    )
    rna.metadata['mfe'] = mfe
    rna.metadata['seq1_length'] = len(sequence1)
    rna.metadata['seq2_length'] = len(sequence2)
    
    return rna, mfe


def ensemble_diversity(
    sequence: str,
    temperature: float = 37.0
) -> float:
    """
    Calculate ensemble diversity (mean base pair distance in ensemble).
    
    Args:
        sequence: RNA sequence
        temperature: Temperature in Celsius
    
    Returns:
        Ensemble diversity value
    """
    _check_viennarna()
    
    RNA.cvar.temperature = temperature
    
    fc = RNA.fold_compound(sequence)
    fc.pf()
    
    return fc.mean_bp_distance()


def evaluate_structure(
    sequence: str,
    structure: str,
    temperature: float = 37.0
) -> float:
    """
    Evaluate the free energy of a given structure.
    
    Args:
        sequence: RNA sequence
        structure: Dot-bracket structure
        temperature: Temperature in Celsius
    
    Returns:
        Free energy in kcal/mol
    
    Example:
        >>> energy = evaluate_structure("GCGCUUAAGCGC", "((((....))))")
        >>> print(f"ΔG = {energy:.2f} kcal/mol")
    """
    _check_viennarna()
    
    RNA.cvar.temperature = temperature
    
    return RNA.eval_structure_simple(sequence, structure)


# Fallback implementation using command-line tools
def _fold_cli(sequence: str, temperature: float = 37.0) -> Tuple[str, float]:
    """Fallback using RNAfold CLI."""
    try:
        result = subprocess.run(
            ['RNAfold', '-T', str(temperature), '--noPS'],
            input=sequence,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"RNAfold failed: {result.stderr}")
        
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            struct_line = lines[1]
            # Parse structure and energy
            parts = struct_line.split()
            structure = parts[0]
            energy = float(parts[-1].strip('()'))
            return structure, energy
        
    except FileNotFoundError:
        raise ImportError("RNAfold not found. Install ViennaRNA package.")
    
    raise RuntimeError("Could not parse RNAfold output")


def get_base_pair_probabilities(
    sequence: str,
    temperature: float = 37.0,
    threshold: float = 0.01
) -> List[Tuple[int, int, float]]:
    """
    Get base pair probabilities from partition function.
    
    Args:
        sequence: RNA sequence
        temperature: Temperature in Celsius
        threshold: Minimum probability to include
    
    Returns:
        List of (i, j, probability) tuples (0-indexed)
    
    Example:
        >>> bpp = get_base_pair_probabilities("GCGCUUAAGCGC")
        >>> for i, j, prob in bpp:
        ...     print(f"({i}, {j}): {prob:.3f}")
    """
    _check_viennarna()
    
    pf_result = partition_function(sequence, temperature)
    return pf_result['base_pair_probabilities']


def available() -> bool:
    """Check if ViennaRNA is available."""
    return HAS_VIENNARNA
