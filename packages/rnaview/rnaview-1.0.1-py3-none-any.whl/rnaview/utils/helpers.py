"""
Helper utilities for RNA structure analysis.

This module provides validation functions, format converters, and
general-purpose utilities for working with RNA sequences and structures.

Example:
    >>> from rnaview.utils import validate_sequence, dotbracket_to_pairs
    >>> validate_sequence("GCGCUUAAGCGC")
    True
    >>> pairs = dotbracket_to_pairs("((((....))))")
    >>> print(pairs)
    [(0, 11), (1, 10), (2, 9), (3, 8)]
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Set, Dict
import re


# Valid nucleotide characters
VALID_RNA_CHARS = set('ACGUN')
VALID_DNA_CHARS = set('ACGTN')
IUPAC_CHARS = set('ACGUNRYSWKMBDHV')
STRUCTURE_CHARS = set('()[]{}.<>AaBb')


def validate_sequence(
    sequence: str,
    allow_gaps: bool = False,
    allow_lowercase: bool = True,
    allow_iupac: bool = True,
    nucleic_acid_type: str = "RNA"
) -> bool:
    """
    Validate an RNA or DNA sequence.
    
    Args:
        sequence: The sequence string to validate
        allow_gaps: Allow gap characters (-, .)
        allow_lowercase: Allow lowercase letters
        allow_iupac: Allow IUPAC ambiguity codes
        nucleic_acid_type: "RNA" or "DNA"
    
    Returns:
        True if sequence is valid
    
    Raises:
        ValueError: If sequence is invalid (with details)
    
    Example:
        >>> validate_sequence("ACGUACGU")
        True
        >>> validate_sequence("ACGTACGT", nucleic_acid_type="DNA")
        True
    """
    if not sequence:
        raise ValueError("Empty sequence")
    
    # Normalize
    test_seq = sequence.upper() if allow_lowercase else sequence
    
    # Choose valid characters
    if nucleic_acid_type.upper() == "RNA":
        valid = VALID_RNA_CHARS.copy()
    else:
        valid = VALID_DNA_CHARS.copy()
    
    if allow_iupac:
        valid.update(IUPAC_CHARS)
    
    if allow_gaps:
        valid.update({'-', '.'})
    
    # Check each character
    invalid = set(test_seq) - valid
    if invalid:
        raise ValueError(f"Invalid characters in sequence: {invalid}")
    
    return True


def validate_structure(
    structure: str,
    sequence: Optional[str] = None,
    allow_pseudoknots: bool = True
) -> bool:
    """
    Validate a dot-bracket structure string.
    
    Args:
        structure: Dot-bracket notation string
        sequence: Optional sequence to check length match
        allow_pseudoknots: Allow pseudoknot notation ([]{}etc)
    
    Returns:
        True if structure is valid
    
    Raises:
        ValueError: If structure is invalid (with details)
    
    Example:
        >>> validate_structure("((((....))))")
        True
        >>> validate_structure("(((...)))", "GCGCUUAAGCGC")
        ValueError: Length mismatch
    """
    if not structure:
        raise ValueError("Empty structure")
    
    # Check length match with sequence
    if sequence is not None and len(structure) != len(sequence):
        raise ValueError(
            f"Structure length ({len(structure)}) doesn't match "
            f"sequence length ({len(sequence)})"
        )
    
    # Define bracket pairs
    if allow_pseudoknots:
        bracket_pairs = [('(', ')'), ('[', ']'), ('{', '}'), 
                        ('<', '>'), ('A', 'a'), ('B', 'b')]
    else:
        bracket_pairs = [('(', ')')]
    
    # Check valid characters
    valid_chars = {'.', '-', '_', ',', ':'}
    for open_br, close_br in bracket_pairs:
        valid_chars.add(open_br)
        valid_chars.add(close_br)
    
    invalid = set(structure) - valid_chars
    if invalid:
        raise ValueError(f"Invalid characters in structure: {invalid}")
    
    # Check balanced brackets
    for open_br, close_br in bracket_pairs:
        stack = []
        for i, char in enumerate(structure):
            if char == open_br:
                stack.append(i)
            elif char == close_br:
                if not stack:
                    raise ValueError(
                        f"Unmatched closing bracket '{close_br}' at position {i}"
                    )
                stack.pop()
        
        if stack:
            raise ValueError(
                f"Unmatched opening bracket '{open_br}' at positions {stack}"
            )
    
    return True


def parse_dotbracket(structure: str) -> Dict[str, any]:
    """
    Parse dot-bracket structure and extract information.
    
    Args:
        structure: Dot-bracket notation string
    
    Returns:
        Dictionary with structure information:
        - pairs: List of (i, j) base pairs
        - unpaired: List of unpaired positions
        - has_pseudoknot: Whether structure contains pseudoknots
        - bracket_levels: Number of bracket types used
    
    Example:
        >>> info = parse_dotbracket("(((..[[[.))).]]]")
        >>> info['has_pseudoknot']
        True
    """
    validate_structure(structure)
    
    bracket_pairs = [('(', ')'), ('[', ']'), ('{', '}'), 
                    ('<', '>'), ('A', 'a'), ('B', 'b')]
    
    all_pairs = []
    bracket_levels = 0
    
    for level, (open_br, close_br) in enumerate(bracket_pairs):
        pairs = []
        stack = []
        
        for i, char in enumerate(structure):
            if char == open_br:
                stack.append(i)
            elif char == close_br:
                if stack:
                    j = stack.pop()
                    pairs.append((j, i))
        
        if pairs:
            bracket_levels = level + 1
            all_pairs.extend(pairs)
    
    # Sort by 5' position
    all_pairs.sort(key=lambda x: x[0])
    
    # Find unpaired positions
    paired = set()
    for i, j in all_pairs:
        paired.add(i)
        paired.add(j)
    
    unpaired = [i for i in range(len(structure)) if i not in paired]
    
    # Check for pseudoknots (crossing pairs)
    has_pseudoknot = False
    for i, (p1_i, p1_j) in enumerate(all_pairs):
        for p2_i, p2_j in all_pairs[i+1:]:
            if p1_i < p2_i < p1_j < p2_j:
                has_pseudoknot = True
                break
        if has_pseudoknot:
            break
    
    return {
        'pairs': all_pairs,
        'unpaired': unpaired,
        'has_pseudoknot': has_pseudoknot,
        'bracket_levels': bracket_levels,
        'num_pairs': len(all_pairs),
        'length': len(structure),
    }


def dotbracket_to_pairs(
    structure: str,
    zero_indexed: bool = True
) -> List[Tuple[int, int]]:
    """
    Convert dot-bracket notation to list of base pairs.
    
    Args:
        structure: Dot-bracket notation string
        zero_indexed: If True, use 0-indexing; if False, use 1-indexing
    
    Returns:
        List of (i, j) tuples representing base pairs
    
    Example:
        >>> pairs = dotbracket_to_pairs("((((....))))")
        >>> print(pairs)
        [(0, 11), (1, 10), (2, 9), (3, 8)]
    """
    info = parse_dotbracket(structure)
    pairs = info['pairs']
    
    if not zero_indexed:
        pairs = [(i + 1, j + 1) for i, j in pairs]
    
    return pairs


def pairs_to_dotbracket(
    pairs: List[Tuple[int, int]],
    length: int,
    handle_pseudoknots: bool = True
) -> str:
    """
    Convert list of base pairs to dot-bracket notation.
    
    Args:
        pairs: List of (i, j) tuples (0-indexed)
        length: Sequence length
        handle_pseudoknots: Use extended notation for pseudoknots
    
    Returns:
        Dot-bracket notation string
    
    Example:
        >>> db = pairs_to_dotbracket([(0, 11), (1, 10), (2, 9)], 12)
        >>> print(db)
        '(((......))'
    """
    db = ['.'] * length
    bracket_chars = [('(', ')'), ('[', ']'), ('{', '}'), ('<', '>')]
    
    # Sort pairs by 5' position
    sorted_pairs = sorted(pairs, key=lambda x: x[0])
    
    if not handle_pseudoknots:
        # Simple case: just use parentheses
        for i, j in sorted_pairs:
            db[i] = '('
            db[j] = ')'
    else:
        # Assign bracket levels to avoid crossing within same level
        used_brackets = 0
        remaining = list(sorted_pairs)
        
        while remaining and used_brackets < len(bracket_chars):
            open_br, close_br = bracket_chars[used_brackets]
            current_level = []
            still_remaining = []
            
            for pair in remaining:
                i, j = pair
                # Check if this pair crosses any in current level
                can_add = True
                for ci, cj in current_level:
                    if ci < i < cj < j or i < ci < j < cj:
                        can_add = False
                        break
                
                if can_add:
                    current_level.append(pair)
                    db[i] = open_br
                    db[j] = close_br
                else:
                    still_remaining.append(pair)
            
            remaining = still_remaining
            used_brackets += 1
    
    return ''.join(db)


def is_valid_basepair(
    nt1: str,
    nt2: str,
    allow_wobble: bool = True,
    allow_non_canonical: bool = False
) -> bool:
    """
    Check if two nucleotides can form a valid base pair.
    
    Args:
        nt1: First nucleotide
        nt2: Second nucleotide
        allow_wobble: Allow G-U wobble pairs
        allow_non_canonical: Allow any pairing
    
    Returns:
        True if valid base pair
    
    Example:
        >>> is_valid_basepair('G', 'C')
        True
        >>> is_valid_basepair('G', 'U', allow_wobble=True)
        True
    """
    if allow_non_canonical:
        return True
    
    canonical = {('A', 'U'), ('U', 'A'), ('G', 'C'), ('C', 'G')}
    wobble = {('G', 'U'), ('U', 'G')}
    
    pair = (nt1.upper(), nt2.upper())
    
    if pair in canonical:
        return True
    if allow_wobble and pair in wobble:
        return True
    
    return False


def calculate_gc_content(sequence: str) -> float:
    """
    Calculate GC content of a sequence.
    
    Args:
        sequence: RNA or DNA sequence
    
    Returns:
        GC content as fraction (0-1)
    
    Example:
        >>> calculate_gc_content("GCGCAUAU")
        0.5
    """
    sequence = sequence.upper()
    gc = sum(1 for nt in sequence if nt in 'GC')
    total = sum(1 for nt in sequence if nt in 'ACGUT')
    
    if total == 0:
        return 0.0
    
    return gc / total


def reverse_complement(sequence: str, molecule_type: str = "RNA") -> str:
    """
    Get reverse complement of a sequence.
    
    Args:
        sequence: RNA or DNA sequence
        molecule_type: "RNA" or "DNA"
    
    Returns:
        Reverse complement sequence
    
    Example:
        >>> reverse_complement("GCAU")
        'AUGC'
    """
    if molecule_type.upper() == "RNA":
        complement = {'A': 'U', 'U': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
    else:
        complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
    
    seq = sequence.upper()
    comp = ''.join(complement.get(nt, 'N') for nt in seq)
    return comp[::-1]


def find_hairpins(
    structure: str,
    min_stem_length: int = 3,
    max_loop_size: int = 10
) -> List[Dict]:
    """
    Find hairpin loops in a structure.
    
    Args:
        structure: Dot-bracket notation
        min_stem_length: Minimum stem base pairs
        max_loop_size: Maximum loop nucleotides
    
    Returns:
        List of hairpin dictionaries with stem and loop info
    """
    pairs = dotbracket_to_pairs(structure)
    pair_dict = {i: j for i, j in pairs}
    pair_dict.update({j: i for i, j in pairs})
    
    hairpins = []
    used = set()
    
    for i, j in pairs:
        if i in used:
            continue
        
        # Check for hairpin (loop between paired bases)
        loop_start = i + 1
        loop_end = j - 1
        
        if loop_end <= loop_start:
            continue
        
        # Check all positions in between are unpaired
        is_hairpin_loop = all(
            k not in pair_dict for k in range(loop_start, loop_end + 1)
        )
        
        if not is_hairpin_loop:
            continue
        
        loop_size = loop_end - loop_start + 1
        if loop_size > max_loop_size:
            continue
        
        # Find stem length
        stem_length = 1
        while (i - stem_length >= 0 and 
               j + stem_length < len(structure) and
               (i - stem_length, j + stem_length) in [(pi, pj) for pi, pj in pairs]):
            stem_length += 1
        
        if stem_length < min_stem_length:
            continue
        
        hairpin = {
            'stem_start_5p': i - stem_length + 1,
            'stem_end_5p': i,
            'stem_start_3p': j,
            'stem_end_3p': j + stem_length - 1,
            'loop_start': loop_start,
            'loop_end': loop_end,
            'stem_length': stem_length,
            'loop_size': loop_size,
        }
        hairpins.append(hairpin)
        
        # Mark as used
        for k in range(hairpin['stem_start_5p'], hairpin['stem_end_5p'] + 1):
            used.add(k)
    
    return hairpins


def calculate_bp_distance(
    structure1: str,
    structure2: str
) -> int:
    """
    Calculate base pair distance between two structures.
    
    The base pair distance is the number of base pairs in one structure
    but not the other, summed for both structures.
    
    Args:
        structure1: First dot-bracket structure
        structure2: Second dot-bracket structure
    
    Returns:
        Base pair distance (integer)
    
    Example:
        >>> calculate_bp_distance("((..))", "(()..)")
        2
    """
    if len(structure1) != len(structure2):
        raise ValueError("Structures must have same length")
    
    pairs1 = set(dotbracket_to_pairs(structure1))
    pairs2 = set(dotbracket_to_pairs(structure2))
    
    # Symmetric difference
    diff = pairs1.symmetric_difference(pairs2)
    
    return len(diff)


def extract_substructure(
    structure: str,
    start: int,
    end: int
) -> str:
    """
    Extract a substructure from positions start to end.
    
    Handles dangling pairs by converting them to unpaired.
    
    Args:
        structure: Full dot-bracket structure
        start: Start position (0-indexed, inclusive)
        end: End position (exclusive)
    
    Returns:
        Substructure in dot-bracket notation
    """
    sub = list(structure[start:end])
    pairs = dotbracket_to_pairs(structure)
    
    # Check which pairs are within range
    for i, j in pairs:
        # Convert to local indices
        local_i = i - start
        local_j = j - start
        
        # Check if pair is partially outside
        i_in = 0 <= local_i < len(sub)
        j_in = 0 <= local_j < len(sub)
        
        if i_in and not j_in:
            # 5' end is in, 3' end is out
            sub[local_i] = '.'
        elif not i_in and j_in:
            # 3' end is in, 5' end is out
            sub[local_j] = '.'
    
    return ''.join(sub)


def merge_structures(
    structure1: str,
    structure2: str,
    offset: int = 0
) -> str:
    """
    Merge two structures, with structure2 starting at offset.
    
    Useful for combining predicted structures of fragments.
    
    Args:
        structure1: Base structure
        structure2: Structure to merge
        offset: Position where structure2 starts
    
    Returns:
        Merged structure
    """
    if offset < 0:
        raise ValueError("Offset must be non-negative")
    
    # Extend structure1 if needed
    total_length = max(len(structure1), offset + len(structure2))
    result = list(structure1 + '.' * (total_length - len(structure1)))
    
    # Merge structure2
    for i, char in enumerate(structure2):
        pos = offset + i
        if char != '.':
            result[pos] = char
    
    return ''.join(result)
