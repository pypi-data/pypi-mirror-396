"""
File parsers for various RNA structure formats.

This module provides functions to load RNA structures from common file formats
including dot-bracket, CT, BPSEQ, PDB, FASTA, and Stockholm.

Example:
    >>> from rnaview.io import load_structure
    >>> rna = load_structure("example.ct")
    >>> print(rna.summary())
"""

from __future__ import annotations
import os
import re
import gzip
from pathlib import Path
from typing import List, Optional, Union, Dict, Tuple
import numpy as np

from ..core.structure import RNAStructure, BasePair


def load_structure(
    filepath: Union[str, Path],
    format: Optional[str] = None,
    **kwargs
) -> RNAStructure:
    """
    Load an RNA structure from a file.
    
    Automatically detects file format based on extension if not specified.
    
    Args:
        filepath: Path to the structure file
        format: Optional format override ('ct', 'bpseq', 'dbn', 'pdb', 'fasta')
        **kwargs: Additional arguments passed to specific parsers
    
    Returns:
        RNAStructure object
    
    Raises:
        ValueError: If format cannot be determined or file is invalid
        FileNotFoundError: If file does not exist
    
    Example:
        >>> rna = load_structure("structure.ct")
        >>> rna = load_structure("structure.dbn", format="dbn")
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Determine format
    if format is None:
        format = _detect_format(filepath)
    
    format = format.lower()
    
    # Dispatch to appropriate parser
    parsers = {
        'ct': load_ct,
        'bpseq': load_bpseq,
        'dbn': load_dotbracket,
        'db': load_dotbracket,
        'dotbracket': load_dotbracket,
        'fasta': load_fasta,
        'fa': load_fasta,
        'pdb': load_pdb,
        'cif': load_pdb,
        'mmcif': load_pdb,
        'sto': load_stockholm,
        'stockholm': load_stockholm,
    }
    
    if format not in parsers:
        raise ValueError(f"Unsupported format: {format}")
    
    return parsers[format](filepath, **kwargs)


def _detect_format(filepath: Path) -> str:
    """Detect file format from extension."""
    suffix = filepath.suffix.lower()
    
    # Handle compressed files
    if suffix == '.gz':
        suffix = Path(filepath.stem).suffix.lower()
    
    format_map = {
        '.ct': 'ct',
        '.bpseq': 'bpseq',
        '.dbn': 'dbn',
        '.db': 'dbn',
        '.fasta': 'fasta',
        '.fa': 'fasta',
        '.pdb': 'pdb',
        '.cif': 'cif',
        '.sto': 'stockholm',
        '.stk': 'stockholm',
    }
    
    if suffix in format_map:
        return format_map[suffix]
    
    # Try to detect from content
    return _detect_format_from_content(filepath)


def _detect_format_from_content(filepath: Path) -> str:
    """Detect format by examining file content."""
    open_func = gzip.open if str(filepath).endswith('.gz') else open
    
    with open_func(filepath, 'rt') as f:
        first_lines = [f.readline() for _ in range(5)]
    
    content = '\n'.join(first_lines)
    
    # Check for various formats
    if content.startswith('>'):
        return 'fasta'
    if content.startswith('ATOM') or content.startswith('HETATM'):
        return 'pdb'
    if content.startswith('data_') or content.startswith('loop_'):
        return 'cif'
    if content.startswith('# STOCKHOLM'):
        return 'stockholm'
    
    # CT format: first line has sequence length and name
    first_line = first_lines[0].strip()
    parts = first_line.split()
    if len(parts) >= 2 and parts[0].isdigit():
        # Check if second line looks like CT
        if len(first_lines) > 1:
            second = first_lines[1].strip().split()
            if len(second) == 6 and second[0].isdigit():
                return 'ct'
    
    # BPSEQ: three columns
    if all(len(line.split()) == 3 for line in first_lines if line.strip()):
        return 'bpseq'
    
    # Default to dot-bracket if contains structure characters
    if any(c in content for c in '()[]{}'):
        return 'dbn'
    
    raise ValueError(f"Cannot determine format of {filepath}")


def load_dotbracket(
    filepath: Union[str, Path],
    **kwargs
) -> RNAStructure:
    """
    Load RNA structure from dot-bracket notation file.
    
    Expected format:
        >name (optional)
        SEQUENCE
        STRUCTURE
    
    Or simply:
        SEQUENCE
        STRUCTURE
    
    Args:
        filepath: Path to dot-bracket file
    
    Returns:
        RNAStructure object
    """
    filepath = Path(filepath)
    open_func = gzip.open if str(filepath).endswith('.gz') else open
    
    with open_func(filepath, 'rt') as f:
        content = f.read().strip()
    
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    
    name = None
    sequence = None
    structure = None
    
    for line in lines:
        if line.startswith('>'):
            name = line[1:].strip()
        elif set(line).issubset(set('ACGUNacgun-.')):
            sequence = line.upper()
        elif set(line).issubset(set('()[]{}.<>AaBb-')):
            structure = line
    
    if sequence is None:
        raise ValueError("No sequence found in file")
    if structure is None:
        raise ValueError("No structure found in file")
    
    return RNAStructure(
        sequence=sequence,
        dotbracket=structure,
        name=name or filepath.stem
    )


def load_ct(
    filepath: Union[str, Path],
    **kwargs
) -> RNAStructure:
    """
    Load RNA structure from CT (connectivity table) format.
    
    CT format (1-indexed):
        N  NAME
        1  A  0  2  10  1
        2  C  1  3   9  2
        ...
        
    Columns: index, nucleotide, prev, next, paired_to, original_index
    
    Args:
        filepath: Path to CT file
    
    Returns:
        RNAStructure object
    """
    filepath = Path(filepath)
    open_func = gzip.open if str(filepath).endswith('.gz') else open
    
    with open_func(filepath, 'rt') as f:
        lines = f.readlines()
    
    # Parse header
    header = lines[0].strip().split()
    length = int(header[0])
    name = ' '.join(header[1:]) if len(header) > 1 else filepath.stem
    
    sequence = []
    base_pairs = []
    
    for i, line in enumerate(lines[1:length+1]):
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        
        idx = int(parts[0]) - 1  # Convert to 0-indexed
        nt = parts[1].upper()
        paired = int(parts[4]) - 1  # Convert to 0-indexed
        
        sequence.append(nt)
        
        # Only add each pair once (when i < j)
        if paired >= 0 and idx < paired:
            base_pairs.append((idx, paired))
    
    return RNAStructure(
        sequence=''.join(sequence),
        base_pairs=base_pairs,
        name=name
    )


def load_bpseq(
    filepath: Union[str, Path],
    **kwargs
) -> RNAStructure:
    """
    Load RNA structure from BPSEQ format.
    
    BPSEQ format (1-indexed):
        1 A 10
        2 C 9
        3 G 0
        ...
        
    Columns: index, nucleotide, paired_to (0 = unpaired)
    
    Args:
        filepath: Path to BPSEQ file
    
    Returns:
        RNAStructure object
    """
    filepath = Path(filepath)
    open_func = gzip.open if str(filepath).endswith('.gz') else open
    
    with open_func(filepath, 'rt') as f:
        lines = f.readlines()
    
    sequence = []
    base_pairs = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parts = line.split()
        if len(parts) != 3:
            continue
        
        idx = int(parts[0]) - 1  # Convert to 0-indexed
        nt = parts[1].upper()
        paired = int(parts[2]) - 1  # Convert to 0-indexed
        
        sequence.append(nt)
        
        # Only add each pair once (when i < j)
        if paired >= 0 and idx < paired:
            base_pairs.append((idx, paired))
    
    return RNAStructure(
        sequence=''.join(sequence),
        base_pairs=base_pairs,
        name=filepath.stem
    )


def load_pdb(
    filepath: Union[str, Path],
    chain_id: Optional[str] = None,
    model_id: int = 0,
    **kwargs
) -> RNAStructure:
    """
    Load RNA structure from PDB or mmCIF file.
    
    Extracts sequence, base pairs (if annotated), and 3D coordinates.
    
    Args:
        filepath: Path to PDB/mmCIF file
        chain_id: Specific chain to extract (default: first RNA chain)
        model_id: Model number for NMR structures (default: 0)
    
    Returns:
        RNAStructure object with 3D coordinates
    
    Note:
        For full PDB parsing capabilities, consider using BioPython or
        specialized tools like x3dna-dssr for base pair extraction.
    """
    filepath = Path(filepath)
    suffix = filepath.suffix.lower()
    
    if suffix in ('.gz',):
        suffix = Path(filepath.stem).suffix.lower()
        open_func = gzip.open
    else:
        open_func = open
    
    with open_func(filepath, 'rt') as f:
        content = f.read()
    
    if suffix in ('.cif', '.mmcif'):
        return _parse_mmcif(content, chain_id, model_id, filepath.stem)
    else:
        return _parse_pdb(content, chain_id, model_id, filepath.stem)


def _parse_pdb(
    content: str,
    chain_id: Optional[str],
    model_id: int,
    name: str
) -> RNAStructure:
    """Parse PDB format content."""
    lines = content.split('\n')
    
    # RNA residue names
    rna_residues = {'A', 'C', 'G', 'U', 'I',
                    'RA', 'RC', 'RG', 'RU',
                    'DA', 'DC', 'DG', 'DT'}  # Include DNA for flexibility
    
    residue_to_nt = {
        'A': 'A', 'RA': 'A', 'DA': 'A',
        'C': 'C', 'RC': 'C', 'DC': 'C',
        'G': 'G', 'RG': 'G', 'DG': 'G',
        'U': 'U', 'RU': 'U',
        'T': 'U', 'DT': 'U',
        'I': 'I',
    }
    
    # Extract atoms
    current_model = 0
    atoms = []
    
    for line in lines:
        if line.startswith('MODEL'):
            current_model = int(line.split()[1]) - 1
        elif line.startswith('ENDMDL'):
            if current_model >= model_id:
                break
        elif line.startswith(('ATOM', 'HETATM')) and current_model == model_id:
            # Parse atom line
            record = line[:6].strip()
            atom_num = int(line[6:11].strip())
            atom_name = line[12:16].strip()
            res_name = line[17:20].strip()
            chain = line[21].strip()
            res_num = int(line[22:26].strip())
            x = float(line[30:38].strip())
            y = float(line[38:46].strip())
            z = float(line[46:54].strip())
            
            # Filter for RNA
            if res_name.upper() in rna_residues:
                if chain_id is None or chain == chain_id:
                    atoms.append({
                        'atom_name': atom_name,
                        'res_name': res_name,
                        'chain': chain,
                        'res_num': res_num,
                        'coords': (x, y, z)
                    })
    
    if not atoms:
        raise ValueError("No RNA atoms found in PDB file")
    
    # Determine chain if not specified
    if chain_id is None:
        chains = set(a['chain'] for a in atoms)
        chain_id = sorted(chains)[0]
        atoms = [a for a in atoms if a['chain'] == chain_id]
    
    # Extract sequence and coordinates
    residues = {}
    for atom in atoms:
        res_key = (atom['chain'], atom['res_num'])
        if res_key not in residues:
            residues[res_key] = {
                'nt': residue_to_nt.get(atom['res_name'].upper(), 'N'),
                'atoms': {}
            }
        residues[res_key]['atoms'][atom['atom_name']] = atom['coords']
    
    # Sort by residue number
    sorted_residues = sorted(residues.items(), key=lambda x: x[0][1])
    
    sequence = ''.join(r[1]['nt'] for r in sorted_residues)
    
    # Get C3' coordinates for backbone representation
    coordinates = []
    for _, res_data in sorted_residues:
        # Prefer C3', fall back to C4', P, or any atom
        for atom_name in ["C3'", "C4'", "P", "C1'"]:
            if atom_name in res_data['atoms']:
                coordinates.append(res_data['atoms'][atom_name])
                break
        else:
            # Use first available atom
            coords = list(res_data['atoms'].values())[0]
            coordinates.append(coords)
    
    coordinates = np.array(coordinates)
    
    # Note: Base pair extraction from PDB requires specialized tools
    # For now, return structure without predicted pairs
    rna = RNAStructure(
        sequence=sequence,
        name=name,
        coordinates_3d=coordinates
    )
    rna.metadata['chain'] = chain_id
    rna.metadata['source'] = 'pdb'
    
    return rna


def _parse_mmcif(
    content: str,
    chain_id: Optional[str],
    model_id: int,
    name: str
) -> RNAStructure:
    """Parse mmCIF format content."""
    # Simplified mmCIF parser
    # For full support, consider using gemmi or BioPython
    
    lines = content.split('\n')
    
    # Find atom_site loop
    in_atom_site = False
    atom_site_cols = []
    atoms = []
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('_atom_site.'):
            in_atom_site = True
            col_name = line.split('.')[1].split()[0]
            atom_site_cols.append(col_name)
        elif in_atom_site and line.startswith('_'):
            in_atom_site = False
        elif in_atom_site and line and not line.startswith('#'):
            parts = line.split()
            if len(parts) >= len(atom_site_cols):
                atom_data = dict(zip(atom_site_cols, parts))
                atoms.append(atom_data)
    
    if not atoms:
        raise ValueError("No atom data found in mmCIF file")
    
    # Convert to standard format and reuse PDB parsing logic
    # This is a simplified approach
    rna_residues = {'A', 'C', 'G', 'U', 'RA', 'RC', 'RG', 'RU'}
    residue_to_nt = {'A': 'A', 'C': 'C', 'G': 'G', 'U': 'U'}
    
    # Extract unique residues
    residues = {}
    for atom in atoms:
        res_name = atom.get('label_comp_id', atom.get('auth_comp_id', ''))
        if res_name.upper() not in rna_residues:
            continue
        
        chain = atom.get('label_asym_id', atom.get('auth_asym_id', ''))
        if chain_id is not None and chain != chain_id:
            continue
        
        res_num = int(atom.get('label_seq_id', atom.get('auth_seq_id', '0')))
        res_key = (chain, res_num)
        
        if res_key not in residues:
            residues[res_key] = {
                'nt': residue_to_nt.get(res_name.upper(), 'N'),
                'atoms': {}
            }
        
        atom_name = atom.get('label_atom_id', atom.get('auth_atom_id', ''))
        x = float(atom.get('Cartn_x', 0))
        y = float(atom.get('Cartn_y', 0))
        z = float(atom.get('Cartn_z', 0))
        
        residues[res_key]['atoms'][atom_name] = (x, y, z)
    
    if not residues:
        raise ValueError("No RNA residues found in mmCIF file")
    
    # Sort and extract sequence
    sorted_residues = sorted(residues.items(), key=lambda x: x[0][1])
    sequence = ''.join(r[1]['nt'] for r in sorted_residues)
    
    # Get coordinates
    coordinates = []
    for _, res_data in sorted_residues:
        for atom_name in ["C3'", "C4'", "P"]:
            if atom_name in res_data['atoms']:
                coordinates.append(res_data['atoms'][atom_name])
                break
        else:
            coords = list(res_data['atoms'].values())[0]
            coordinates.append(coords)
    
    coordinates = np.array(coordinates)
    
    rna = RNAStructure(
        sequence=sequence,
        name=name,
        coordinates_3d=coordinates
    )
    rna.metadata['source'] = 'mmcif'
    
    return rna


def load_fasta(
    filepath: Union[str, Path],
    include_structure: bool = True,
    **kwargs
) -> Union[RNAStructure, List[RNAStructure]]:
    """
    Load RNA sequence(s) from FASTA format.
    
    If structure annotation is included (e.g., Vienna format output),
    it will be parsed automatically.
    
    Args:
        filepath: Path to FASTA file
        include_structure: Try to parse structure from FASTA (default True)
    
    Returns:
        Single RNAStructure or list of structures if multiple sequences
    """
    filepath = Path(filepath)
    open_func = gzip.open if str(filepath).endswith('.gz') else open
    
    with open_func(filepath, 'rt') as f:
        content = f.read()
    
    # Parse FASTA entries
    entries = []
    current_name = None
    current_lines = []
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('>'):
            if current_name is not None:
                entries.append((current_name, current_lines))
            current_name = line[1:].split()[0]
            current_lines = []
        elif line:
            current_lines.append(line)
    
    if current_name is not None:
        entries.append((current_name, current_lines))
    
    # Create structures
    structures = []
    for name, lines in entries:
        if not lines:
            continue
        
        # Check if structure is included
        sequence = None
        structure = None
        
        for line in lines:
            if set(line).issubset(set('ACGUNacgun-.')):
                sequence = line.upper()
            elif set(line).issubset(set('()[]{}.<>-')):
                structure = line
        
        if sequence is None:
            sequence = ''.join(lines[0].upper().replace('T', 'U'))
        
        rna = RNAStructure(
            sequence=sequence,
            dotbracket=structure,
            name=name
        )
        structures.append(rna)
    
    if len(structures) == 1:
        return structures[0]
    return structures


def load_stockholm(
    filepath: Union[str, Path],
    **kwargs
) -> List[RNAStructure]:
    """
    Load RNA structures from Stockholm alignment format.
    
    Stockholm format is used by Rfam and includes consensus structure
    annotation with #=GC SS_cons lines.
    
    Args:
        filepath: Path to Stockholm file
    
    Returns:
        List of RNAStructure objects (one per sequence in alignment)
    """
    filepath = Path(filepath)
    open_func = gzip.open if str(filepath).endswith('.gz') else open
    
    with open_func(filepath, 'rt') as f:
        content = f.read()
    
    # Parse Stockholm format
    sequences = {}
    consensus_structure = []
    
    for line in content.split('\n'):
        line = line.rstrip()
        
        if line.startswith('#=GC SS_cons'):
            # Consensus secondary structure
            parts = line.split(None, 2)
            if len(parts) > 2:
                consensus_structure.append(parts[2])
        elif line.startswith('#') or line.startswith('//') or not line:
            continue
        else:
            # Sequence line
            parts = line.split(None, 1)
            if len(parts) == 2:
                name, seq = parts
                if name not in sequences:
                    sequences[name] = []
                sequences[name].append(seq)
    
    # Combine multi-line entries
    consensus = ''.join(consensus_structure).replace('_', '.').replace('-', '.')
    
    structures = []
    for name, seq_parts in sequences.items():
        seq = ''.join(seq_parts).upper().replace('T', 'U')
        
        # Remove gaps for ungapped structure
        ungapped_seq = seq.replace('-', '').replace('.', '')
        
        # Map consensus structure to ungapped sequence
        if consensus:
            structure = _map_structure_to_ungapped(seq, consensus)
        else:
            structure = None
        
        rna = RNAStructure(
            sequence=ungapped_seq,
            dotbracket=structure,
            name=name
        )
        structures.append(rna)
    
    return structures


def _map_structure_to_ungapped(
    gapped_seq: str,
    gapped_structure: str
) -> str:
    """Map gapped consensus structure to ungapped sequence."""
    if len(gapped_seq) != len(gapped_structure):
        return None
    
    structure = []
    for i, (nt, ss) in enumerate(zip(gapped_seq, gapped_structure)):
        if nt not in '-.':
            # Keep structure character for non-gap positions
            structure.append(ss if ss not in '-.~_' else '.')
    
    return ''.join(structure)


def parse_dotbracket_string(
    sequence: str,
    structure: str,
    name: Optional[str] = None
) -> RNAStructure:
    """
    Create RNAStructure from sequence and dot-bracket strings.
    
    Convenience function for creating structures from string inputs.
    
    Args:
        sequence: RNA sequence
        structure: Dot-bracket notation
        name: Optional structure name
    
    Returns:
        RNAStructure object
    
    Example:
        >>> rna = parse_dotbracket_string(
        ...     "GCGCUUAAGCGC",
        ...     "((((....))))"
        ... )
    """
    return RNAStructure(
        sequence=sequence,
        dotbracket=structure,
        name=name
    )
