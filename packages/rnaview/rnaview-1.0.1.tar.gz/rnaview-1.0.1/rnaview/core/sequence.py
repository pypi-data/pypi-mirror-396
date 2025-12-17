"""
RNA sequence handling and manipulation.

This module provides the RNASequence class for working with RNA sequences,
including validation, manipulation, and biological feature extraction.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Iterator, Set
from collections import Counter
import re


# Standard genetic code for translation (if needed)
CODON_TABLE = {
    'UUU': 'F', 'UUC': 'F', 'UUA': 'L', 'UUG': 'L',
    'UCU': 'S', 'UCC': 'S', 'UCA': 'S', 'UCG': 'S',
    'UAU': 'Y', 'UAC': 'Y', 'UAA': '*', 'UAG': '*',
    'UGU': 'C', 'UGC': 'C', 'UGA': '*', 'UGG': 'W',
    'CUU': 'L', 'CUC': 'L', 'CUA': 'L', 'CUG': 'L',
    'CCU': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'CAU': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'CGU': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'AUU': 'I', 'AUC': 'I', 'AUA': 'I', 'AUG': 'M',
    'ACU': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'AAU': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'AGU': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GUU': 'V', 'GUC': 'V', 'GUA': 'V', 'GUG': 'V',
    'GCU': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'GAU': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'GGU': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}

# IUPAC ambiguity codes
IUPAC_CODES = {
    'A': {'A'},
    'C': {'C'},
    'G': {'G'},
    'U': {'U'},
    'R': {'A', 'G'},      # Purine
    'Y': {'C', 'U'},      # Pyrimidine
    'S': {'G', 'C'},      # Strong
    'W': {'A', 'U'},      # Weak
    'K': {'G', 'U'},      # Keto
    'M': {'A', 'C'},      # Amino
    'B': {'C', 'G', 'U'}, # Not A
    'D': {'A', 'G', 'U'}, # Not C
    'H': {'A', 'C', 'U'}, # Not G
    'V': {'A', 'C', 'G'}, # Not U
    'N': {'A', 'C', 'G', 'U'},  # Any
}


@dataclass
class RNASequence:
    """
    Represents an RNA sequence with associated metadata and operations.
    
    This class provides functionality for RNA sequence manipulation,
    validation, and biological feature extraction.
    
    Attributes:
        sequence: The RNA sequence string
        name: Optional sequence identifier
        description: Optional description
        organism: Optional source organism
        accession: Optional database accession
        annotations: Dictionary of position-based annotations
    
    Example:
        >>> seq = RNASequence("AUGCUAGCUAG", name="example")
        >>> seq.gc_content
        0.4545...
        >>> seq.complement()
        'UACGAUCGAUC'
    """
    sequence: str
    name: Optional[str] = None
    description: Optional[str] = None
    organism: Optional[str] = None
    accession: Optional[str] = None
    annotations: Dict[int, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize the sequence."""
        self.sequence = self._normalize(self.sequence)
        if not self._is_valid():
            raise ValueError(f"Invalid RNA sequence: contains invalid characters")
    
    def _normalize(self, seq: str) -> str:
        """Normalize sequence to uppercase RNA."""
        return seq.upper().replace('T', 'U').replace(' ', '').replace('\n', '')
    
    def _is_valid(self) -> bool:
        """Check if sequence contains only valid characters."""
        valid_chars = set('ACGUNXRY-.' + ''.join(IUPAC_CODES.keys()))
        return all(c in valid_chars for c in self.sequence)
    
    @property
    def length(self) -> int:
        """Return sequence length."""
        return len(self.sequence)
    
    def __len__(self) -> int:
        return self.length
    
    def __str__(self) -> str:
        return self.sequence
    
    def __repr__(self) -> str:
        return f"RNASequence('{self.sequence[:20]}...', name='{self.name}', length={self.length})"
    
    def __getitem__(self, idx) -> str:
        """Get nucleotide(s) at index or slice."""
        return self.sequence[idx]
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over nucleotides."""
        return iter(self.sequence)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, RNASequence):
            return self.sequence == other.sequence
        elif isinstance(other, str):
            return self.sequence == self._normalize(other)
        return False
    
    def __hash__(self) -> int:
        return hash(self.sequence)
    
    def __add__(self, other: 'RNASequence') -> 'RNASequence':
        """Concatenate two sequences."""
        if isinstance(other, RNASequence):
            return RNASequence(self.sequence + other.sequence)
        elif isinstance(other, str):
            return RNASequence(self.sequence + other)
        raise TypeError(f"Cannot concatenate RNASequence with {type(other)}")
    
    @property
    def gc_content(self) -> float:
        """Calculate GC content as a fraction."""
        if self.length == 0:
            return 0.0
        gc = sum(1 for nt in self.sequence if nt in 'GC')
        return gc / self.length
    
    @property
    def composition(self) -> Dict[str, int]:
        """Return nucleotide composition counts."""
        return dict(Counter(self.sequence))
    
    @property
    def composition_fraction(self) -> Dict[str, float]:
        """Return nucleotide composition as fractions."""
        counts = self.composition
        total = sum(counts.values())
        return {nt: count/total for nt, count in counts.items()}
    
    def complement(self) -> str:
        """Return the complementary sequence (5' to 3')."""
        complement_map = {'A': 'U', 'U': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
        return ''.join(complement_map.get(nt, 'N') for nt in self.sequence)
    
    def reverse_complement(self) -> str:
        """Return the reverse complement sequence."""
        return self.complement()[::-1]
    
    def to_dna(self) -> str:
        """Convert to DNA sequence (U -> T)."""
        return self.sequence.replace('U', 'T')
    
    @classmethod
    def from_dna(cls, dna_seq: str, **kwargs) -> 'RNASequence':
        """Create RNASequence from DNA sequence."""
        rna_seq = dna_seq.upper().replace('T', 'U')
        return cls(rna_seq, **kwargs)
    
    def find_motif(self, motif: str) -> List[int]:
        """
        Find all occurrences of a motif in the sequence.
        
        Args:
            motif: The motif to search for (supports IUPAC codes)
        
        Returns:
            List of start positions (0-indexed)
        """
        motif = self._normalize(motif)
        positions = []
        
        # Convert motif to regex pattern for IUPAC codes
        pattern = ''
        for char in motif:
            if char in IUPAC_CODES:
                bases = IUPAC_CODES[char]
                pattern += f'[{"".join(bases)}]'
            else:
                pattern += char
        
        for match in re.finditer(pattern, self.sequence):
            positions.append(match.start())
        
        return positions
    
    def find_orfs(self, min_length: int = 30) -> List[Tuple[int, int, str]]:
        """
        Find open reading frames in the sequence.
        
        Args:
            min_length: Minimum ORF length in nucleotides
        
        Returns:
            List of (start, end, protein_sequence) tuples
        """
        orfs = []
        start_codon = 'AUG'
        stop_codons = {'UAA', 'UAG', 'UGA'}
        
        # Search in all three reading frames
        for frame in range(3):
            i = frame
            while i < self.length - 2:
                codon = self.sequence[i:i+3]
                if codon == start_codon:
                    # Found start codon, look for stop
                    protein = ''
                    j = i
                    while j < self.length - 2:
                        codon = self.sequence[j:j+3]
                        if codon in stop_codons:
                            if j - i >= min_length:
                                orfs.append((i, j+3, protein))
                            break
                        protein += CODON_TABLE.get(codon, 'X')
                        j += 3
                i += 3
        
        return orfs
    
    def kmer_frequencies(self, k: int = 3) -> Dict[str, int]:
        """
        Calculate k-mer frequencies.
        
        Args:
            k: k-mer length
        
        Returns:
            Dictionary of k-mer to count
        """
        kmers = Counter()
        for i in range(self.length - k + 1):
            kmer = self.sequence[i:i+k]
            kmers[kmer] += 1
        return dict(kmers)
    
    def dinucleotide_frequencies(self) -> Dict[str, float]:
        """Calculate dinucleotide frequencies."""
        freq = self.kmer_frequencies(k=2)
        total = sum(freq.values())
        return {k: v/total for k, v in freq.items()}
    
    def slice(self, start: int, end: int) -> 'RNASequence':
        """
        Extract a subsequence.
        
        Args:
            start: Start position (0-indexed, inclusive)
            end: End position (exclusive)
        
        Returns:
            New RNASequence object
        """
        return RNASequence(
            self.sequence[start:end],
            name=f"{self.name}_{start}-{end}" if self.name else None
        )
    
    def mutate(self, position: int, new_nucleotide: str) -> 'RNASequence':
        """
        Create a new sequence with a point mutation.
        
        Args:
            position: Position to mutate (0-indexed)
            new_nucleotide: New nucleotide
        
        Returns:
            New RNASequence with the mutation
        """
        if position < 0 or position >= self.length:
            raise ValueError(f"Position {position} out of range")
        
        new_seq = self.sequence[:position] + new_nucleotide.upper() + self.sequence[position+1:]
        return RNASequence(new_seq, name=f"{self.name}_mut{position}" if self.name else None)
    
    def insert(self, position: int, insertion: str) -> 'RNASequence':
        """
        Create a new sequence with an insertion.
        
        Args:
            position: Position to insert at
            insertion: Sequence to insert
        
        Returns:
            New RNASequence with insertion
        """
        new_seq = self.sequence[:position] + insertion.upper() + self.sequence[position:]
        return RNASequence(new_seq, name=f"{self.name}_ins{position}" if self.name else None)
    
    def delete(self, start: int, length: int) -> 'RNASequence':
        """
        Create a new sequence with a deletion.
        
        Args:
            start: Start position of deletion
            length: Number of nucleotides to delete
        
        Returns:
            New RNASequence with deletion
        """
        new_seq = self.sequence[:start] + self.sequence[start+length:]
        return RNASequence(new_seq, name=f"{self.name}_del{start}" if self.name else None)
    
    def to_fasta(self, line_width: int = 60) -> str:
        """
        Format as FASTA string.
        
        Args:
            line_width: Characters per line (default 60)
        
        Returns:
            FASTA-formatted string
        """
        header = f">{self.name or 'sequence'}"
        if self.description:
            header += f" {self.description}"
        
        # Wrap sequence
        lines = [header]
        for i in range(0, self.length, line_width):
            lines.append(self.sequence[i:i+line_width])
        
        return '\n'.join(lines)
    
    @classmethod
    def from_fasta(cls, fasta_string: str) -> List['RNASequence']:
        """
        Parse sequences from FASTA format.
        
        Args:
            fasta_string: FASTA-formatted string
        
        Returns:
            List of RNASequence objects
        """
        sequences = []
        current_name = None
        current_desc = None
        current_seq = []
        
        for line in fasta_string.strip().split('\n'):
            line = line.strip()
            if line.startswith('>'):
                # Save previous sequence if exists
                if current_seq:
                    sequences.append(cls(
                        ''.join(current_seq),
                        name=current_name,
                        description=current_desc
                    ))
                
                # Parse header
                header = line[1:].split(None, 1)
                current_name = header[0] if header else None
                current_desc = header[1] if len(header) > 1 else None
                current_seq = []
            else:
                current_seq.append(line)
        
        # Don't forget last sequence
        if current_seq:
            sequences.append(cls(
                ''.join(current_seq),
                name=current_name,
                description=current_desc
            ))
        
        return sequences
    
    def has_ambiguity(self) -> bool:
        """Check if sequence contains ambiguity codes."""
        standard = set('ACGU')
        return any(nt not in standard for nt in self.sequence)
    
    def resolve_ambiguity(self) -> List['RNASequence']:
        """
        Generate all possible sequences from ambiguity codes.
        
        Warning: This can generate a very large number of sequences!
        
        Returns:
            List of all possible unambiguous sequences
        """
        if not self.has_ambiguity():
            return [self]
        
        # Recursive resolution
        def resolve(seq: str) -> List[str]:
            for i, char in enumerate(seq):
                if char in IUPAC_CODES and char not in 'ACGU':
                    possibilities = []
                    for base in IUPAC_CODES[char]:
                        new_seq = seq[:i] + base + seq[i+1:]
                        possibilities.extend(resolve(new_seq))
                    return possibilities
            return [seq]
        
        resolved = resolve(self.sequence)
        return [RNASequence(s, name=f"{self.name}_variant" if self.name else None) 
                for s in resolved]
