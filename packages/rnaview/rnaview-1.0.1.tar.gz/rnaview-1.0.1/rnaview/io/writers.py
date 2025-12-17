"""
File writers for various RNA structure formats.

This module provides functions to save RNA structures to common file formats
including dot-bracket, CT, BPSEQ, and FASTA.

Example:
    >>> from rnaview.io import save_structure
    >>> save_structure(rna, "output.ct", format="ct")
"""

from __future__ import annotations
from pathlib import Path
from typing import Union, Optional, List

from ..core.structure import RNAStructure


def save_structure(
    structure: RNAStructure,
    filepath: Union[str, Path],
    format: Optional[str] = None,
    **kwargs
) -> None:
    """
    Save an RNA structure to a file.
    
    Automatically selects format based on file extension if not specified.
    
    Args:
        structure: RNAStructure object to save
        filepath: Output file path
        format: Optional format override ('ct', 'bpseq', 'dbn', 'fasta')
        **kwargs: Additional arguments passed to specific writers
    
    Example:
        >>> save_structure(rna, "output.ct")
        >>> save_structure(rna, "output.dbn", format="dbn")
    """
    filepath = Path(filepath)
    
    # Determine format from extension if not specified
    if format is None:
        format = _format_from_extension(filepath)
    
    format = format.lower()
    
    # Generate content
    writers = {
        'ct': to_ct,
        'bpseq': to_bpseq,
        'dbn': to_dotbracket,
        'db': to_dotbracket,
        'dotbracket': to_dotbracket,
        'fasta': to_fasta,
        'fa': to_fasta,
    }
    
    if format not in writers:
        raise ValueError(f"Unsupported format: {format}")
    
    content = writers[format](structure, **kwargs)
    
    # Write to file
    with open(filepath, 'w') as f:
        f.write(content)


def _format_from_extension(filepath: Path) -> str:
    """Determine format from file extension."""
    suffix = filepath.suffix.lower()
    
    format_map = {
        '.ct': 'ct',
        '.bpseq': 'bpseq',
        '.dbn': 'dbn',
        '.db': 'dbn',
        '.fasta': 'fasta',
        '.fa': 'fasta',
    }
    
    if suffix in format_map:
        return format_map[suffix]
    
    # Default to dot-bracket
    return 'dbn'


def to_dotbracket(
    structure: RNAStructure,
    include_sequence: bool = True,
    include_name: bool = True,
    include_pseudoknots: bool = True,
    **kwargs
) -> str:
    """
    Convert RNA structure to dot-bracket notation string.
    
    Args:
        structure: RNAStructure object
        include_sequence: Include sequence in output (default True)
        include_name: Include name header (default True)
        include_pseudoknots: Use extended notation for pseudoknots
    
    Returns:
        Dot-bracket formatted string
    
    Example:
        >>> content = to_dotbracket(rna)
        >>> print(content)
        >example
        GCGCUUAAGCGC
        ((((....))))
    """
    lines = []
    
    if include_name and structure.name:
        lines.append(f">{structure.name}")
    
    if include_sequence:
        lines.append(structure.sequence)
    
    lines.append(structure.to_dotbracket(include_pseudoknots=include_pseudoknots))
    
    return '\n'.join(lines)


def to_ct(
    structure: RNAStructure,
    **kwargs
) -> str:
    """
    Convert RNA structure to CT (connectivity table) format.
    
    CT format (1-indexed):
        N  NAME
        1  A  0  2  10  1
        2  C  1  3   9  2
        ...
        
    Args:
        structure: RNAStructure object
    
    Returns:
        CT formatted string
    
    Example:
        >>> content = to_ct(rna)
    """
    lines = []
    
    # Header: length and name
    name = structure.name or "RNA"
    lines.append(f"{structure.length}\t{name}")
    
    # Build pair table (1-indexed)
    pair_table = {0: 0}  # Initialize with dummy
    for bp in structure.base_pairs:
        pair_table[bp.i + 1] = bp.j + 1  # Convert to 1-indexed
        pair_table[bp.j + 1] = bp.i + 1
    
    # Generate lines
    for i in range(structure.length):
        idx = i + 1  # 1-indexed
        nt = structure.sequence[i]
        prev_idx = i if i == 0 else idx - 1
        next_idx = idx + 1 if i < structure.length - 1 else 0
        paired = pair_table.get(idx, 0)  # 0 if unpaired
        
        lines.append(f"{idx}\t{nt}\t{prev_idx}\t{next_idx}\t{paired}\t{idx}")
    
    return '\n'.join(lines)


def to_bpseq(
    structure: RNAStructure,
    **kwargs
) -> str:
    """
    Convert RNA structure to BPSEQ format.
    
    BPSEQ format (1-indexed):
        1 A 10
        2 C 9
        3 G 0
        ...
        
    Args:
        structure: RNAStructure object
    
    Returns:
        BPSEQ formatted string
    
    Example:
        >>> content = to_bpseq(rna)
    """
    lines = []
    
    # Build pair table (1-indexed)
    pair_table = {}
    for bp in structure.base_pairs:
        pair_table[bp.i + 1] = bp.j + 1
        pair_table[bp.j + 1] = bp.i + 1
    
    # Generate lines
    for i in range(structure.length):
        idx = i + 1  # 1-indexed
        nt = structure.sequence[i]
        paired = pair_table.get(idx, 0)  # 0 if unpaired
        
        lines.append(f"{idx} {nt} {paired}")
    
    return '\n'.join(lines)


def to_fasta(
    structure: RNAStructure,
    line_width: int = 60,
    include_structure: bool = False,
    **kwargs
) -> str:
    """
    Convert RNA structure to FASTA format.
    
    Args:
        structure: RNAStructure object
        line_width: Characters per line (default 60)
        include_structure: Include dot-bracket as second entry
    
    Returns:
        FASTA formatted string
    
    Example:
        >>> content = to_fasta(rna, include_structure=True)
    """
    lines = []
    
    # Header
    name = structure.name or "sequence"
    lines.append(f">{name}")
    
    # Sequence (wrapped)
    seq = structure.sequence
    for i in range(0, len(seq), line_width):
        lines.append(seq[i:i+line_width])
    
    # Optionally add structure
    if include_structure:
        lines.append(f">{name}_structure")
        db = structure.to_dotbracket()
        for i in range(0, len(db), line_width):
            lines.append(db[i:i+line_width])
    
    return '\n'.join(lines)


def to_vienna(
    structure: RNAStructure,
    include_energy: bool = False,
    energy: Optional[float] = None,
    **kwargs
) -> str:
    """
    Convert to Vienna format (RNAfold output format).
    
    Vienna format:
        >name
        SEQUENCE
        STRUCTURE (ENERGY)
    
    Args:
        structure: RNAStructure object
        include_energy: Include energy in output
        energy: Free energy value (if known)
    
    Returns:
        Vienna formatted string
    """
    lines = []
    
    if structure.name:
        lines.append(f">{structure.name}")
    
    lines.append(structure.sequence)
    
    db = structure.to_dotbracket()
    if include_energy and energy is not None:
        lines.append(f"{db} ({energy:.2f})")
    else:
        lines.append(db)
    
    return '\n'.join(lines)


def to_rnaml(
    structure: RNAStructure,
    **kwargs
) -> str:
    """
    Convert to RNAML (RNA Markup Language) XML format.
    
    Args:
        structure: RNAStructure object
    
    Returns:
        RNAML XML string
    """
    from xml.etree.ElementTree import Element, SubElement, tostring
    from xml.dom import minidom
    
    # Root element
    root = Element('rnaml')
    root.set('version', '1.0')
    
    # Molecule
    molecule = SubElement(root, 'molecule')
    molecule.set('id', structure.name or 'rna_1')
    
    # Sequence
    seq_elem = SubElement(molecule, 'sequence')
    seq_elem.set('length', str(structure.length))
    seq_data = SubElement(seq_elem, 'seq-data')
    seq_data.text = structure.sequence
    
    # Structure
    struct_elem = SubElement(molecule, 'structure')
    
    # Base pairs
    bp_list = SubElement(struct_elem, 'base-pair-list')
    for i, bp in enumerate(structure.base_pairs):
        bp_elem = SubElement(bp_list, 'base-pair')
        bp_elem.set('id', str(i + 1))
        
        base5 = SubElement(bp_elem, 'base-id-5p')
        base5.set('position', str(bp.i + 1))
        
        base3 = SubElement(bp_elem, 'base-id-3p')
        base3.set('position', str(bp.j + 1))
        
        edge5 = SubElement(bp_elem, 'edge-5p')
        edge5.text = 'W'  # Watson-Crick edge
        
        edge3 = SubElement(bp_elem, 'edge-3p')
        edge3.text = 'W'
        
        orient = SubElement(bp_elem, 'bond-orientation')
        orient.text = 'cis'
    
    # Convert to string with pretty printing
    rough_string = tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def write_multiple(
    structures: List[RNAStructure],
    filepath: Union[str, Path],
    format: str = "fasta",
    **kwargs
) -> None:
    """
    Write multiple structures to a single file.
    
    Args:
        structures: List of RNAStructure objects
        filepath: Output file path
        format: Output format ('fasta', 'ct', etc.)
    
    Example:
        >>> write_multiple([rna1, rna2, rna3], "structures.fasta")
    """
    filepath = Path(filepath)
    
    contents = []
    for struct in structures:
        if format in ('ct', 'bpseq'):
            # These formats don't naturally support multiple structures
            # Use separate sections
            if format == 'ct':
                contents.append(to_ct(struct, **kwargs))
            else:
                contents.append(to_bpseq(struct, **kwargs))
            contents.append('')  # Empty line separator
        else:
            contents.append(to_fasta(struct, **kwargs))
    
    with open(filepath, 'w') as f:
        f.write('\n'.join(contents))
