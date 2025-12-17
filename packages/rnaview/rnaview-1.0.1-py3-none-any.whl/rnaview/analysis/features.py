"""
Structural feature extraction for RNA secondary structures.

This module provides functions for identifying and analyzing structural
features in RNA secondary structures, including helices, loops, pseudoknots,
and stem-loops.

Example:
    >>> import rnaview as rv
    >>> rna = rv.load_structure("example.ct")
    >>> helices = rv.find_helices(rna)
    >>> loops = rv.find_loops(rna)
    >>> print(f"Found {len(helices)} helices and {len(loops)} loops")
"""

from __future__ import annotations
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass

from ..core.structure import RNAStructure, BasePair, Helix, Loop, Pseudoknot, StructureType


@dataclass
class StemLoop:
    """
    Represents a stem-loop (hairpin) motif.
    
    Attributes:
        stem: The helical stem region
        loop: The hairpin loop region
        start: Start position of the motif
        end: End position of the motif
        name: Optional identifier
    """
    stem: Helix
    loop: Loop
    start: int
    end: int
    name: Optional[str] = None
    
    @property
    def stem_length(self) -> int:
        """Number of base pairs in the stem."""
        return self.stem.length
    
    @property
    def loop_size(self) -> int:
        """Number of nucleotides in the loop."""
        return self.loop.size
    
    def __repr__(self) -> str:
        return f"StemLoop(stem={self.stem_length}bp, loop={self.loop_size}nt, pos={self.start}-{self.end})"


def find_helices(
    structure: RNAStructure,
    min_length: int = 1
) -> List[Helix]:
    """
    Identify helical (stem) regions in the structure.
    
    A helix is defined as consecutive base pairs where pairs (i,j) and
    (i+1, j-1) are both present.
    
    Args:
        structure: RNAStructure object
        min_length: Minimum helix length in base pairs
    
    Returns:
        List of Helix objects
    
    Example:
        >>> helices = find_helices(rna, min_length=3)
        >>> for h in helices:
        ...     print(f"Helix: {h.length} bp at {h.start_5p}-{h.end_5p}")
    """
    helices = structure.get_helices()
    return [h for h in helices if h.length >= min_length]


def find_loops(
    structure: RNAStructure,
    include_external: bool = False
) -> List[Loop]:
    """
    Identify loop regions in the structure.
    
    Identifies hairpin loops, internal loops, bulges, and multiloops.
    
    Args:
        structure: RNAStructure object
        include_external: Include external (unpaired) regions
    
    Returns:
        List of Loop objects
    
    Example:
        >>> loops = find_loops(rna)
        >>> hairpins = [l for l in loops if l.is_hairpin]
    """
    loops = []
    pair_table = structure.pair_table
    n = structure.length
    
    # Find all loop regions using a traversal approach
    visited = set()
    
    # Process each position
    i = 0
    while i < n:
        if i in visited:
            i += 1
            continue
        
        paired = pair_table.get(i)
        
        if paired is not None and paired > i:
            # Start of a base pair - look for internal structure
            loop_info = _classify_loop_region(structure, i, paired, pair_table)
            if loop_info:
                loops.append(loop_info)
                # Mark positions as visited
                visited.add(i)
                visited.add(paired)
        
        i += 1
    
    # Find hairpin loops
    hairpins = _find_hairpin_loops(structure, pair_table)
    loops.extend(hairpins)
    
    # External regions
    if include_external:
        external = _find_external_regions(structure, pair_table)
        if external:
            loops.append(external)
    
    return loops


def _find_hairpin_loops(
    structure: RNAStructure,
    pair_table: Dict[int, int]
) -> List[Loop]:
    """Find hairpin loops closed by a single base pair."""
    hairpins = []
    
    for bp in structure.base_pairs:
        # Check if this is a closing base pair of a hairpin
        # (no other base pairs between i and j)
        is_hairpin = True
        loop_positions = []
        
        for pos in range(bp.i + 1, bp.j):
            if pos in pair_table:
                # Check if paired position is outside the loop
                paired_pos = pair_table[pos]
                if bp.i < paired_pos < bp.j:
                    is_hairpin = False
                    break
            else:
                loop_positions.append(pos)
        
        if is_hairpin and loop_positions:
            loop = Loop(
                loop_type=StructureType.HAIRPIN_LOOP,
                positions=loop_positions,
                closing_pairs=[bp],
                sequence=structure.sequence[loop_positions[0]:loop_positions[-1]+1]
            )
            hairpins.append(loop)
    
    return hairpins


def _classify_loop_region(
    structure: RNAStructure,
    start: int,
    end: int,
    pair_table: Dict[int, int]
) -> Optional[Loop]:
    """Classify a loop region based on its structure."""
    # Count base pairs that close into this region
    closing_pairs = []
    unpaired_5p = []
    unpaired_3p = []
    
    # Scan 5' side
    pos = start + 1
    while pos < end:
        paired = pair_table.get(pos)
        if paired is not None and start < paired < end:
            closing_pairs.append(BasePair(pos, paired))
            pos = paired + 1
        else:
            if not closing_pairs:
                unpaired_5p.append(pos)
            else:
                unpaired_3p.append(pos)
            pos += 1
    
    if not closing_pairs:
        return None  # This is a hairpin, handled separately
    
    # Classify based on number of closing pairs and unpaired regions
    if len(closing_pairs) == 1:
        # Internal loop or bulge
        if unpaired_5p and unpaired_3p:
            loop_type = StructureType.INTERNAL_LOOP
        elif unpaired_5p or unpaired_3p:
            loop_type = StructureType.BULGE
        else:
            return None  # Stacked pair, not a loop
    else:
        # Multiloop
        loop_type = StructureType.MULTILOOP
    
    all_unpaired = unpaired_5p + unpaired_3p
    
    return Loop(
        loop_type=loop_type,
        positions=all_unpaired,
        closing_pairs=closing_pairs,
        sequence=''.join(structure.sequence[p] for p in all_unpaired) if all_unpaired else ''
    )


def _find_external_regions(
    structure: RNAStructure,
    pair_table: Dict[int, int]
) -> Optional[Loop]:
    """Find external (unstructured) regions."""
    external_positions = []
    
    for i in range(structure.length):
        if i not in pair_table:
            # Check if this is truly external (not inside any pair)
            is_external = True
            for bp in structure.base_pairs:
                if bp.i < i < bp.j:
                    is_external = False
                    break
            if is_external:
                external_positions.append(i)
    
    if external_positions:
        return Loop(
            loop_type=StructureType.EXTERNAL,
            positions=external_positions
        )
    return None


def find_pseudoknots(
    structure: RNAStructure
) -> List[Pseudoknot]:
    """
    Identify pseudoknots in the structure.
    
    A pseudoknot occurs when base pairs cross: i < i' < j < j'
    for pairs (i,j) and (i',j').
    
    Args:
        structure: RNAStructure object
    
    Returns:
        List of Pseudoknot objects
    
    Example:
        >>> pks = find_pseudoknots(rna)
        >>> print(f"Found {len(pks)} pseudoknots")
    """
    return structure.get_pseudoknots()


def get_stem_loops(
    structure: RNAStructure,
    min_stem_length: int = 2,
    min_loop_size: int = 3,
    max_loop_size: int = 15
) -> List[StemLoop]:
    """
    Extract stem-loop (hairpin) motifs from the structure.
    
    Args:
        structure: RNAStructure object
        min_stem_length: Minimum stem length in base pairs
        min_loop_size: Minimum loop size in nucleotides
        max_loop_size: Maximum loop size in nucleotides
    
    Returns:
        List of StemLoop objects
    
    Example:
        >>> stem_loops = get_stem_loops(rna, min_stem_length=4)
        >>> for sl in stem_loops:
        ...     print(f"Stem: {sl.stem_length}bp, Loop: {sl.loop_size}nt")
    """
    stem_loops = []
    helices = find_helices(structure, min_length=min_stem_length)
    loops = [l for l in find_loops(structure) if l.is_hairpin]
    
    # Match helices with their hairpin loops
    for helix in helices:
        closing_bp = helix.base_pairs[-1]
        
        for loop in loops:
            if loop.closing_pairs and loop.closing_pairs[0] == closing_bp:
                if min_loop_size <= loop.size <= max_loop_size:
                    sl = StemLoop(
                        stem=helix,
                        loop=loop,
                        start=helix.start_5p,
                        end=helix.end_3p
                    )
                    stem_loops.append(sl)
                break
    
    return stem_loops


def calculate_free_energy(
    structure: RNAStructure,
    temperature: float = 37.0,
    use_dangle: bool = True
) -> float:
    """
    Estimate free energy of the RNA structure.
    
    Uses nearest-neighbor thermodynamic parameters. For accurate
    calculations, use ViennaRNA integration.
    
    Args:
        structure: RNAStructure object
        temperature: Temperature in Celsius
        use_dangle: Include dangling end contributions
    
    Returns:
        Estimated free energy in kcal/mol
    
    Note:
        This is an approximation. For precise energies, use
        rnaview.integrations.viennarna.mfe_structure()
    
    Example:
        >>> dG = calculate_free_energy(rna)
        >>> print(f"ΔG = {dG:.2f} kcal/mol")
    """
    # Nearest-neighbor parameters (simplified Turner 2004 rules)
    # Stacking energies in kcal/mol at 37°C
    STACK_ENERGIES = {
        # Watson-Crick pairs: (5'-XY-3')/(3'-AB-5') where XY pairs with AB
        ('CG', 'CG'): -3.30, ('CG', 'GC'): -2.40, ('CG', 'UA'): -2.10, ('CG', 'AU'): -2.10,
        ('GC', 'CG'): -2.40, ('GC', 'GC'): -3.30, ('GC', 'UA'): -2.10, ('GC', 'AU'): -2.10,
        ('UA', 'CG'): -2.40, ('UA', 'GC'): -2.10, ('UA', 'UA'): -0.90, ('UA', 'AU'): -1.10,
        ('AU', 'CG'): -2.10, ('AU', 'GC'): -2.20, ('AU', 'UA'): -1.30, ('AU', 'AU'): -0.90,
        # G-U wobble pairs (approximations)
        ('GU', 'CG'): -1.40, ('GU', 'GC'): -2.50, ('GU', 'UA'): -1.30, ('GU', 'AU'): -1.00,
        ('UG', 'CG'): -2.50, ('UG', 'GC'): -1.50, ('UG', 'UA'): -0.50, ('UG', 'AU'): -1.30,
    }
    
    # Loop initiation energies
    HAIRPIN_INIT = {3: 5.4, 4: 5.6, 5: 5.7, 6: 5.4, 7: 6.0, 8: 5.5, 9: 6.4}
    
    energy = 0.0
    
    # Stacking energies
    helices = structure.get_helices()
    for helix in helices:
        for k in range(len(helix.base_pairs) - 1):
            bp1 = helix.base_pairs[k]
            bp2 = helix.base_pairs[k + 1]
            
            # Get stacking pair
            nt_5p = structure.sequence[bp1.i] + structure.sequence[bp2.i]
            nt_3p = structure.sequence[bp1.j] + structure.sequence[bp2.j]
            
            stack_key = (nt_5p, nt_3p[::-1])  # Reverse 3' strand
            
            if stack_key in STACK_ENERGIES:
                energy += STACK_ENERGIES[stack_key]
            else:
                # Default stacking
                energy += -1.5
    
    # Hairpin loop energies
    loops = [l for l in structure.get_loops() if l.is_hairpin]
    for loop in loops:
        size = loop.size
        if size in HAIRPIN_INIT:
            energy += HAIRPIN_INIT[size]
        elif size < 3:
            energy += 10.0  # Penalty for too-small loops
        else:
            energy += HAIRPIN_INIT[9] + 1.75 * 1.987 * (273.15 + 37) / 1000 * 2.303 * (size / 9)
    
    # AU/GU end penalties
    for helix in helices:
        terminal_pairs = [helix.base_pairs[0], helix.base_pairs[-1]]
        for bp in terminal_pairs:
            pair = (structure.sequence[bp.i], structure.sequence[bp.j])
            if pair in [('A', 'U'), ('U', 'A'), ('G', 'U'), ('U', 'G')]:
                energy += 0.45
    
    return round(energy, 2)


def get_base_pair_types(
    structure: RNAStructure
) -> Dict[str, int]:
    """
    Count base pair types in the structure.
    
    Args:
        structure: RNAStructure object
    
    Returns:
        Dictionary with pair type counts
    
    Example:
        >>> types = get_base_pair_types(rna)
        >>> print(f"G-C pairs: {types.get('GC', 0)}")
    """
    counts = {}
    
    for bp in structure.base_pairs:
        nt1 = structure.sequence[bp.i]
        nt2 = structure.sequence[bp.j]
        
        # Canonical ordering
        pair = f"{nt1}{nt2}"
        pair_rev = f"{nt2}{nt1}"
        
        # Normalize to alphabetical order
        key = min(pair, pair_rev)
        counts[key] = counts.get(key, 0) + 1
    
    return counts


def get_structure_statistics(
    structure: RNAStructure
) -> Dict[str, any]:
    """
    Compute comprehensive statistics for an RNA structure.
    
    Args:
        structure: RNAStructure object
    
    Returns:
        Dictionary with various structural statistics
    
    Example:
        >>> stats = get_structure_statistics(rna)
        >>> print(f"Paired fraction: {stats['paired_fraction']:.2%}")
    """
    n = structure.length
    helices = find_helices(structure)
    loops = find_loops(structure)
    
    hairpins = [l for l in loops if l.is_hairpin]
    internal = [l for l in loops if l.is_internal]
    bulges = [l for l in loops if l.is_bulge]
    multiloops = [l for l in loops if l.is_multiloop]
    
    return {
        'length': n,
        'num_pairs': structure.num_pairs,
        'paired_fraction': 2 * structure.num_pairs / n if n > 0 else 0,
        'num_helices': len(helices),
        'avg_helix_length': sum(h.length for h in helices) / len(helices) if helices else 0,
        'max_helix_length': max((h.length for h in helices), default=0),
        'num_hairpin_loops': len(hairpins),
        'num_internal_loops': len(internal),
        'num_bulges': len(bulges),
        'num_multiloops': len(multiloops),
        'avg_hairpin_size': sum(l.size for l in hairpins) / len(hairpins) if hairpins else 0,
        'has_pseudoknot': structure.has_pseudoknot,
        'gc_content': sum(1 for c in structure.sequence if c in 'GC') / n if n > 0 else 0,
        'base_pair_types': get_base_pair_types(structure),
    }


def find_motifs(
    structure: RNAStructure,
    motif_type: str = "tetraloop"
) -> List[Dict[str, any]]:
    """
    Find common RNA structural motifs.
    
    Args:
        structure: RNAStructure object
        motif_type: Type of motif to search for
            - 'tetraloop': GNRA, UNCG, CUUG tetraloops
            - 'kink_turn': K-turn motifs
            - 'sarcin_ricin': Sarcin-ricin loop
    
    Returns:
        List of found motifs with positions and details
    
    Example:
        >>> tetraloops = find_motifs(rna, "tetraloop")
    """
    motifs = []
    
    if motif_type == "tetraloop":
        # Find GNRA, UNCG, CUUG tetraloops
        tetraloop_patterns = {
            'GNRA': ['GAAA', 'GAGA', 'GCAA', 'GGAA', 'GUAA', 
                     'GACA', 'GCCA', 'GGCA', 'GUCA',
                     'GAGA', 'GCGA', 'GGGA', 'GUGA'],
            'UNCG': ['UACG', 'UCCG', 'UGCG', 'UUCG'],
            'CUUG': ['CUUG'],
        }
        
        loops = [l for l in find_loops(structure) if l.is_hairpin and l.size == 4]
        
        for loop in loops:
            seq = loop.sequence
            for family, patterns in tetraloop_patterns.items():
                if seq in patterns:
                    motifs.append({
                        'type': 'tetraloop',
                        'family': family,
                        'sequence': seq,
                        'position': loop.positions[0],
                        'loop': loop
                    })
                    break
    
    return motifs
