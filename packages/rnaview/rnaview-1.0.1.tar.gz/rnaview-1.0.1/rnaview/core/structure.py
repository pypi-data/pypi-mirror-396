"""
Core RNA structure classes.

This module provides the fundamental data structures for representing RNA
secondary and tertiary structures, including base pairs, helices, loops,
and pseudoknots.

Example:
    >>> from rnaview.core import RNAStructure
    >>> rna = RNAStructure(
    ...     sequence="GCGCUUAAGCGC",
    ...     dotbracket="(((....)))"
    ... )
    >>> print(rna.base_pairs)
    [(0, 11), (1, 10), (2, 9)]
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Set, Union, Iterator
from enum import Enum
import numpy as np
from copy import deepcopy


class StructureType(Enum):
    """Enumeration of RNA structural element types."""
    STEM = "stem"
    HAIRPIN_LOOP = "hairpin_loop"
    INTERNAL_LOOP = "internal_loop"
    BULGE = "bulge"
    MULTILOOP = "multiloop"
    EXTERNAL = "external"
    PSEUDOKNOT = "pseudoknot"


class BasePairType(Enum):
    """Types of RNA base pairs."""
    CANONICAL_WC = "watson_crick"  # G-C, A-U
    WOBBLE = "wobble"              # G-U
    NON_CANONICAL = "non_canonical"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BasePair:
    """
    Represents a single base pair in an RNA structure.
    
    Attributes:
        i: 0-indexed position of the 5' nucleotide
        j: 0-indexed position of the 3' nucleotide
        pair_type: Type of base pairing interaction
        confidence: Optional confidence score (0-1) from prediction
        is_pseudoknot: Whether this pair is part of a pseudoknot
        annotation: Optional annotation string
    
    Example:
        >>> bp = BasePair(0, 10, BasePairType.CANONICAL_WC)
        >>> print(bp)
        BasePair(0-10, watson_crick)
    """
    i: int
    j: int
    pair_type: BasePairType = BasePairType.CANONICAL_WC
    confidence: Optional[float] = None
    is_pseudoknot: bool = False
    annotation: Optional[str] = None
    
    def __post_init__(self):
        if self.i >= self.j:
            raise ValueError(f"Invalid base pair: i ({self.i}) must be < j ({self.j})")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
    
    def __repr__(self) -> str:
        return f"BasePair({self.i}-{self.j}, {self.pair_type.value})"
    
    def span(self) -> int:
        """Return the span (j - i) of the base pair."""
        return self.j - self.i
    
    def contains(self, other: 'BasePair') -> bool:
        """Check if this base pair contains another (nested)."""
        return self.i < other.i and other.j < self.j
    
    def crosses(self, other: 'BasePair') -> bool:
        """Check if this base pair crosses another (pseudoknot)."""
        return (self.i < other.i < self.j < other.j or 
                other.i < self.i < other.j < self.j)


@dataclass
class Helix:
    """
    Represents a helical region (stack of consecutive base pairs).
    
    Attributes:
        base_pairs: List of consecutive base pairs forming the helix
        start_5p: 5' start position
        end_5p: 5' end position
        start_3p: 3' start position
        end_3p: 3' end position
        name: Optional identifier for the helix
    
    Example:
        >>> pairs = [BasePair(0, 20), BasePair(1, 19), BasePair(2, 18)]
        >>> helix = Helix(pairs)
        >>> print(helix.length)
        3
    """
    base_pairs: List[BasePair]
    name: Optional[str] = None
    
    def __post_init__(self):
        if not self.base_pairs:
            raise ValueError("Helix must contain at least one base pair")
        # Sort by 5' position
        self.base_pairs = sorted(self.base_pairs, key=lambda bp: bp.i)
    
    @property
    def length(self) -> int:
        """Number of base pairs in the helix."""
        return len(self.base_pairs)
    
    @property
    def start_5p(self) -> int:
        """5' start position."""
        return self.base_pairs[0].i
    
    @property
    def end_5p(self) -> int:
        """5' end position."""
        return self.base_pairs[-1].i
    
    @property
    def start_3p(self) -> int:
        """3' start position (closing pair)."""
        return self.base_pairs[-1].j
    
    @property
    def end_3p(self) -> int:
        """3' end position."""
        return self.base_pairs[0].j
    
    def is_continuous(self) -> bool:
        """Check if base pairs are consecutive."""
        for k in range(len(self.base_pairs) - 1):
            bp1, bp2 = self.base_pairs[k], self.base_pairs[k + 1]
            if bp2.i != bp1.i + 1 or bp2.j != bp1.j - 1:
                return False
        return True


@dataclass
class Loop:
    """
    Represents a loop region in RNA secondary structure.
    
    Attributes:
        loop_type: Type of loop (hairpin, internal, bulge, multiloop)
        positions: List of unpaired nucleotide positions
        closing_pairs: Base pairs that close the loop
        sequence: Optional sequence of loop nucleotides
    
    Example:
        >>> loop = Loop(StructureType.HAIRPIN_LOOP, [3, 4, 5, 6])
        >>> print(loop.size)
        4
    """
    loop_type: StructureType
    positions: List[int]
    closing_pairs: List[BasePair] = field(default_factory=list)
    sequence: Optional[str] = None
    name: Optional[str] = None
    
    @property
    def size(self) -> int:
        """Number of unpaired nucleotides in the loop."""
        return len(self.positions)
    
    @property
    def is_hairpin(self) -> bool:
        """Check if this is a hairpin loop."""
        return self.loop_type == StructureType.HAIRPIN_LOOP
    
    @property
    def is_internal(self) -> bool:
        """Check if this is an internal loop."""
        return self.loop_type == StructureType.INTERNAL_LOOP
    
    @property
    def is_bulge(self) -> bool:
        """Check if this is a bulge."""
        return self.loop_type == StructureType.BULGE
    
    @property
    def is_multiloop(self) -> bool:
        """Check if this is a multiloop."""
        return self.loop_type == StructureType.MULTILOOP


@dataclass
class Pseudoknot:
    """
    Represents a pseudoknot in RNA structure.
    
    A pseudoknot occurs when nucleotides in a loop pair with nucleotides
    outside the loop, creating crossing base pairs.
    
    Attributes:
        stem1: First stem of the pseudoknot
        stem2: Second stem of the pseudoknot
        loop1: First loop region
        loop2: Second loop region
        knot_type: Classification of pseudoknot type (H-type, K-type, etc.)
        name: Optional identifier
    
    Example:
        >>> pk = Pseudoknot(stem1=helix1, stem2=helix2, knot_type="H-type")
    """
    stem1: Helix
    stem2: Helix
    loop1: Optional[Loop] = None
    loop2: Optional[Loop] = None
    knot_type: str = "H-type"
    name: Optional[str] = None
    
    def all_base_pairs(self) -> List[BasePair]:
        """Return all base pairs in the pseudoknot."""
        return self.stem1.base_pairs + self.stem2.base_pairs
    
    def get_crossing_pairs(self) -> List[Tuple[BasePair, BasePair]]:
        """Return pairs of base pairs that cross each other."""
        crossing = []
        for bp1 in self.stem1.base_pairs:
            for bp2 in self.stem2.base_pairs:
                if bp1.crosses(bp2):
                    crossing.append((bp1, bp2))
        return crossing


class RNAStructure:
    """
    Main class representing an RNA structure with sequence and base pairs.
    
    This class provides a comprehensive representation of RNA secondary
    structure, including support for pseudoknots, modifications, and
    3D coordinates.
    
    Attributes:
        sequence: RNA nucleotide sequence
        name: Optional structure name/identifier
        base_pairs: List of BasePair objects
        modifications: Dictionary of position -> Modification
        coordinates_2d: 2D coordinates for visualization (Nx2 array)
        coordinates_3d: 3D coordinates if available (Nx3 array)
        reactivity: Per-nucleotide reactivity data (e.g., SHAPE)
        confidence_scores: Per-nucleotide confidence from prediction
        metadata: Additional metadata dictionary
    
    Example:
        >>> rna = RNAStructure(
        ...     sequence="GCGCUUAAGCGC",
        ...     dotbracket="((((....))))"
        ... )
        >>> rna.num_pairs
        4
        >>> rna.has_pseudoknot
        False
    """
    
    def __init__(
        self,
        sequence: str,
        dotbracket: Optional[str] = None,
        base_pairs: Optional[List[Union[BasePair, Tuple[int, int]]]] = None,
        name: Optional[str] = None,
        coordinates_3d: Optional[np.ndarray] = None,
    ):
        """
        Initialize an RNA structure.
        
        Args:
            sequence: RNA sequence (A, C, G, U characters)
            dotbracket: Optional dot-bracket notation string
            base_pairs: Optional list of base pairs or (i, j) tuples
            name: Optional structure identifier
            coordinates_3d: Optional 3D coordinates (Nx3 numpy array)
        
        Raises:
            ValueError: If sequence is invalid or structure is inconsistent
        """
        # Validate and store sequence
        self.sequence = self._validate_sequence(sequence)
        self.name = name
        self.length = len(self.sequence)
        
        # Initialize base pairs
        self._base_pairs: List[BasePair] = []
        self._pair_table: Dict[int, int] = {}  # Maps position to paired position
        
        # Parse structure
        if dotbracket is not None:
            self._parse_dotbracket(dotbracket)
        elif base_pairs is not None:
            self._set_base_pairs(base_pairs)
        
        # Initialize optional data
        self.coordinates_2d: Optional[np.ndarray] = None
        self.coordinates_3d = coordinates_3d
        self.reactivity: Optional[np.ndarray] = None
        self.confidence_scores: Optional[np.ndarray] = None
        self.modifications: Dict[int, 'Modification'] = {}
        self.metadata: Dict[str, any] = {}
        
        # Cached structural features
        self._helices: Optional[List[Helix]] = None
        self._loops: Optional[List[Loop]] = None
        self._pseudoknots: Optional[List[Pseudoknot]] = None
    
    def _validate_sequence(self, sequence: str) -> str:
        """Validate and normalize RNA sequence."""
        sequence = sequence.upper().replace('T', 'U')
        valid_chars = set('ACGUNXRY-.')  # Include ambiguity codes
        invalid = set(sequence) - valid_chars
        if invalid:
            raise ValueError(f"Invalid characters in sequence: {invalid}")
        return sequence
    
    def _parse_dotbracket(self, dotbracket: str) -> None:
        """Parse dot-bracket notation to extract base pairs."""
        if len(dotbracket) != self.length:
            raise ValueError(
                f"Dot-bracket length ({len(dotbracket)}) doesn't match "
                f"sequence length ({self.length})"
            )
        
        # Support for multiple bracket types (pseudoknots)
        bracket_pairs = [
            ('(', ')'),
            ('[', ']'),
            ('{', '}'),
            ('<', '>'),
            ('A', 'a'),
            ('B', 'b'),
        ]
        
        for open_br, close_br in bracket_pairs:
            stack = []
            is_pk = open_br not in '('  # Non-standard brackets are pseudoknots
            
            for i, char in enumerate(dotbracket):
                if char == open_br:
                    stack.append(i)
                elif char == close_br:
                    if not stack:
                        raise ValueError(
                            f"Unmatched closing bracket '{close_br}' at position {i}"
                        )
                    j = stack.pop()
                    bp = BasePair(
                        i=j, j=i,
                        pair_type=self._infer_pair_type(j, i),
                        is_pseudoknot=is_pk
                    )
                    self._base_pairs.append(bp)
                    self._pair_table[j] = i
                    self._pair_table[i] = j
            
            if stack:
                raise ValueError(
                    f"Unmatched opening bracket '{open_br}' at positions {stack}"
                )
        
        # Sort by 5' position
        self._base_pairs.sort(key=lambda bp: bp.i)
    
    def _infer_pair_type(self, i: int, j: int) -> BasePairType:
        """Infer base pair type from sequence."""
        nt1, nt2 = self.sequence[i], self.sequence[j]
        canonical_wc = {('A', 'U'), ('U', 'A'), ('G', 'C'), ('C', 'G')}
        wobble = {('G', 'U'), ('U', 'G')}
        
        pair = (nt1, nt2)
        if pair in canonical_wc:
            return BasePairType.CANONICAL_WC
        elif pair in wobble:
            return BasePairType.WOBBLE
        else:
            return BasePairType.NON_CANONICAL
    
    def _set_base_pairs(
        self, 
        pairs: List[Union[BasePair, Tuple[int, int]]]
    ) -> None:
        """Set base pairs from list."""
        for pair in pairs:
            if isinstance(pair, tuple):
                i, j = pair
                if i > j:
                    i, j = j, i
                bp = BasePair(i=i, j=j, pair_type=self._infer_pair_type(i, j))
            else:
                bp = pair
            self._base_pairs.append(bp)
            self._pair_table[bp.i] = bp.j
            self._pair_table[bp.j] = bp.i
        
        self._base_pairs.sort(key=lambda bp: bp.i)
    
    @property
    def base_pairs(self) -> List[BasePair]:
        """Return list of base pairs."""
        return self._base_pairs.copy()
    
    @property
    def num_pairs(self) -> int:
        """Number of base pairs."""
        return len(self._base_pairs)
    
    @property
    def pair_table(self) -> Dict[int, int]:
        """Dictionary mapping each paired position to its partner."""
        return self._pair_table.copy()
    
    def get_paired_position(self, i: int) -> Optional[int]:
        """Get the position paired to position i, or None if unpaired."""
        return self._pair_table.get(i)
    
    def is_paired(self, i: int) -> bool:
        """Check if position i is paired."""
        return i in self._pair_table
    
    @property
    def unpaired_positions(self) -> List[int]:
        """Return list of unpaired positions."""
        return [i for i in range(self.length) if i not in self._pair_table]
    
    @property
    def has_pseudoknot(self) -> bool:
        """Check if structure contains pseudoknots."""
        for i, bp1 in enumerate(self._base_pairs):
            for bp2 in self._base_pairs[i+1:]:
                if bp1.crosses(bp2):
                    return True
        return False
    
    def to_dotbracket(self, include_pseudoknots: bool = True) -> str:
        """
        Convert structure to dot-bracket notation.
        
        Args:
            include_pseudoknots: Use extended notation for pseudoknots
        
        Returns:
            Dot-bracket string
        """
        db = ['.'] * self.length
        bracket_chars = [('(', ')'), ('[', ']'), ('{', '}'), ('<', '>')]
        
        if not include_pseudoknots:
            # Simple case: only use parentheses
            for bp in self._base_pairs:
                if not bp.is_pseudoknot:
                    db[bp.i] = '('
                    db[bp.j] = ')'
        else:
            # Group base pairs by nesting level for pseudoknot handling
            used_brackets = 0
            remaining = list(self._base_pairs)
            
            while remaining and used_brackets < len(bracket_chars):
                open_br, close_br = bracket_chars[used_brackets]
                current_level = []
                still_remaining = []
                
                for bp in remaining:
                    # Check if this bp can be added without crossing
                    can_add = True
                    for added_bp in current_level:
                        if bp.crosses(added_bp):
                            can_add = False
                            break
                    
                    if can_add:
                        current_level.append(bp)
                        db[bp.i] = open_br
                        db[bp.j] = close_br
                    else:
                        still_remaining.append(bp)
                
                remaining = still_remaining
                used_brackets += 1
        
        return ''.join(db)
    
    def to_ct_format(self) -> str:
        """Convert to CT (connectivity table) format string."""
        lines = [f"{self.length}\t{self.name or 'RNA'}"]
        
        for i in range(self.length):
            nt = self.sequence[i]
            prev_idx = i if i == 0 else i
            next_idx = i + 2 if i < self.length - 1 else 0
            paired = self._pair_table.get(i, -1) + 1  # CT is 1-indexed, 0 = unpaired
            
            lines.append(f"{i+1}\t{nt}\t{prev_idx}\t{next_idx}\t{paired}\t{i+1}")
        
        return '\n'.join(lines)
    
    def to_bpseq_format(self) -> str:
        """Convert to BPSEQ format string."""
        lines = []
        for i in range(self.length):
            nt = self.sequence[i]
            paired = self._pair_table.get(i, -1) + 1  # 1-indexed, 0 = unpaired
            lines.append(f"{i+1} {nt} {paired}")
        return '\n'.join(lines)
    
    def get_helices(self) -> List[Helix]:
        """
        Extract helical regions from the structure.
        
        Returns:
            List of Helix objects representing continuous stems.
        """
        if self._helices is not None:
            return self._helices
        
        helices = []
        used = set()
        
        for bp in self._base_pairs:
            if bp.i in used:
                continue
            
            # Start a new helix
            helix_pairs = [bp]
            used.add(bp.i)
            used.add(bp.j)
            
            # Extend helix
            current = bp
            while True:
                next_i, next_j = current.i + 1, current.j - 1
                if next_i >= next_j:
                    break
                
                # Find the next base pair
                found = False
                for next_bp in self._base_pairs:
                    if next_bp.i == next_i and next_bp.j == next_j:
                        helix_pairs.append(next_bp)
                        used.add(next_bp.i)
                        used.add(next_bp.j)
                        current = next_bp
                        found = True
                        break
                
                if not found:
                    break
            
            if helix_pairs:
                helices.append(Helix(helix_pairs))
        
        self._helices = helices
        return helices
    
    def get_loops(self) -> List[Loop]:
        """
        Extract loop regions from the structure.
        
        Returns:
            List of Loop objects.
        """
        if self._loops is not None:
            return self._loops
        
        loops = []
        helices = self.get_helices()
        
        for helix in helices:
            # Check for hairpin loop
            closing_bp = helix.base_pairs[-1]
            loop_start = closing_bp.i + 1
            loop_end = closing_bp.j - 1
            
            if loop_end > loop_start:
                # Check if all positions in between are unpaired
                loop_positions = list(range(loop_start, loop_end + 1))
                if all(pos not in self._pair_table for pos in loop_positions):
                    loop = Loop(
                        loop_type=StructureType.HAIRPIN_LOOP,
                        positions=loop_positions,
                        closing_pairs=[closing_bp],
                        sequence=self.sequence[loop_start:loop_end+1]
                    )
                    loops.append(loop)
        
        self._loops = loops
        return loops
    
    def get_pseudoknots(self) -> List[Pseudoknot]:
        """
        Identify and extract pseudoknots from the structure.
        
        Returns:
            List of Pseudoknot objects.
        """
        if self._pseudoknots is not None:
            return self._pseudoknots
        
        pseudoknots = []
        pk_pairs = [bp for bp in self._base_pairs if bp.is_pseudoknot]
        
        # Group crossing pairs into pseudoknots
        # This is a simplified implementation
        if pk_pairs:
            # Find stems involved in pseudoknots
            regular_pairs = [bp for bp in self._base_pairs if not bp.is_pseudoknot]
            
            # Basic H-type pseudoknot detection
            for pk_bp in pk_pairs:
                for reg_bp in regular_pairs:
                    if pk_bp.crosses(reg_bp):
                        stem1 = Helix([reg_bp])
                        stem2 = Helix([pk_bp])
                        pk = Pseudoknot(stem1=stem1, stem2=stem2)
                        pseudoknots.append(pk)
                        break
        
        self._pseudoknots = pseudoknots
        return pseudoknots
    
    def add_modification(
        self,
        position: int,
        modification: 'Modification'
    ) -> None:
        """Add a modification at a specific position."""
        if position < 0 or position >= self.length:
            raise ValueError(f"Position {position} out of range [0, {self.length})")
        self.modifications[position] = modification
    
    def get_modification(self, position: int) -> Optional['Modification']:
        """Get modification at a position, if any."""
        return self.modifications.get(position)
    
    def set_reactivity(self, reactivity: np.ndarray) -> None:
        """Set per-nucleotide reactivity data (e.g., SHAPE)."""
        if len(reactivity) != self.length:
            raise ValueError(
                f"Reactivity length ({len(reactivity)}) doesn't match "
                f"sequence length ({self.length})"
            )
        self.reactivity = np.array(reactivity)
    
    def copy(self) -> 'RNAStructure':
        """Create a deep copy of the structure."""
        return deepcopy(self)
    
    def __len__(self) -> int:
        return self.length
    
    def __repr__(self) -> str:
        return (
            f"RNAStructure(name='{self.name}', length={self.length}, "
            f"pairs={self.num_pairs}, has_pk={self.has_pseudoknot})"
        )
    
    def __str__(self) -> str:
        return f"{self.sequence}\n{self.to_dotbracket()}"
    
    def __iter__(self) -> Iterator[Tuple[str, Optional[int]]]:
        """Iterate over (nucleotide, paired_position) tuples."""
        for i in range(self.length):
            yield self.sequence[i], self._pair_table.get(i)
    
    def __getitem__(self, idx: int) -> Tuple[str, Optional[int]]:
        """Get (nucleotide, paired_position) at index."""
        if idx < 0 or idx >= self.length:
            raise IndexError(f"Index {idx} out of range [0, {self.length})")
        return self.sequence[idx], self._pair_table.get(idx)
    
    def summary(self) -> str:
        """Return a summary string of the structure."""
        helices = self.get_helices()
        loops = self.get_loops()
        
        lines = [
            f"RNA Structure: {self.name or 'Unnamed'}",
            f"  Length: {self.length} nt",
            f"  Base pairs: {self.num_pairs}",
            f"  Helices: {len(helices)}",
            f"  Loops: {len(loops)}",
            f"  Has pseudoknot: {self.has_pseudoknot}",
            f"  Modifications: {len(self.modifications)}",
        ]
        
        if self.coordinates_3d is not None:
            lines.append(f"  3D coordinates: Available")
        if self.reactivity is not None:
            lines.append(f"  Reactivity data: Available")
        
        return '\n'.join(lines)
