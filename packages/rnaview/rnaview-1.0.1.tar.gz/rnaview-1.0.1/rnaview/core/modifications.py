"""
RNA modification handling and annotation.

This module provides classes and utilities for working with RNA modifications,
including common modifications like m6A, m5C, pseudouridine, and 2'-O-methylation.

Supported modification types are based on MODOMICS database nomenclature.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum


class ModificationType(Enum):
    """
    Common RNA modification types.
    
    Based on MODOMICS database nomenclature and common abbreviations.
    """
    # Methylations
    M6A = "m6A"           # N6-methyladenosine
    M1A = "m1A"           # N1-methyladenosine
    M5C = "m5C"           # 5-methylcytidine
    M7G = "m7G"           # 7-methylguanosine
    M1G = "m1G"           # 1-methylguanosine
    M2G = "m2G"           # N2-methylguanosine
    M22G = "m2,2G"        # N2,N2-dimethylguanosine
    AM = "Am"             # 2'-O-methyladenosine
    CM = "Cm"             # 2'-O-methylcytidine
    GM = "Gm"             # 2'-O-methylguanosine
    UM = "Um"             # 2'-O-methyluridine
    
    # Pseudouridine
    PSI = "Ψ"             # Pseudouridine
    
    # Other common modifications
    I = "I"               # Inosine
    D = "D"               # Dihydrouridine
    T = "T"               # Ribothymidine (5-methyluridine)
    Q = "Q"               # Queuosine
    WYOSINE = "yW"        # Wyosine
    
    # Base modifications
    S2U = "s2U"           # 2-thiouridine
    S4U = "s4U"           # 4-thiouridine
    AC4C = "ac4C"         # N4-acetylcytidine
    
    # Unknown/Other
    UNKNOWN = "unknown"
    OTHER = "other"


# Modification properties database
MODIFICATION_PROPERTIES = {
    ModificationType.M6A: {
        "full_name": "N6-methyladenosine",
        "parent_base": "A",
        "mass_shift": 14.016,
        "detection_methods": ["MeRIP-seq", "m6A-seq", "DART-seq", "m6A-CLIP"],
        "biological_function": "mRNA stability, translation, splicing regulation",
        "abundance": "Most abundant internal mRNA modification",
        "color": "#FF6B6B",  # Red-ish
    },
    ModificationType.M5C: {
        "full_name": "5-methylcytidine",
        "parent_base": "C",
        "mass_shift": 14.016,
        "detection_methods": ["Bisulfite-seq", "m5C-RIP", "Aza-IP"],
        "biological_function": "RNA stability, translation regulation",
        "abundance": "Found in tRNA, rRNA, mRNA",
        "color": "#4ECDC4",  # Teal
    },
    ModificationType.PSI: {
        "full_name": "Pseudouridine",
        "parent_base": "U",
        "mass_shift": 0,  # Isomer
        "detection_methods": ["Pseudo-seq", "CMC treatment", "Ψ-seq"],
        "biological_function": "RNA structure stabilization",
        "abundance": "Most abundant RNA modification overall",
        "color": "#45B7D1",  # Blue
    },
    ModificationType.M1A: {
        "full_name": "N1-methyladenosine",
        "parent_base": "A",
        "mass_shift": 14.016,
        "detection_methods": ["m1A-seq", "m1A-ID-seq"],
        "biological_function": "Translation regulation, stress response",
        "abundance": "Found in tRNA, rRNA, mRNA",
        "color": "#96CEB4",  # Green
    },
    ModificationType.I: {
        "full_name": "Inosine",
        "parent_base": "A",
        "mass_shift": 0.984,
        "detection_methods": ["ICE-seq", "RNA editing detection"],
        "biological_function": "A-to-I editing, codon recoding",
        "abundance": "Common in double-stranded RNA regions",
        "color": "#FFEAA7",  # Yellow
    },
    ModificationType.AM: {
        "full_name": "2'-O-methyladenosine",
        "parent_base": "A",
        "mass_shift": 14.016,
        "detection_methods": ["2'-O-Me-seq", "RiboMethSeq"],
        "biological_function": "Self/non-self discrimination, stability",
        "abundance": "Common in rRNA, snRNA",
        "color": "#DDA0DD",  # Plum
    },
}


@dataclass
class Modification:
    """
    Represents an RNA modification type with its properties.
    
    Attributes:
        mod_type: The type of modification
        symbol: Short symbol for display
        full_name: Full chemical name
        parent_base: The unmodified base
        mass_shift: Mass difference from parent (Da)
        detection_methods: Experimental methods for detection
        biological_function: Known biological roles
        color: Display color (hex)
    
    Example:
        >>> mod = Modification.m6A()
        >>> print(mod.full_name)
        'N6-methyladenosine'
    """
    mod_type: ModificationType
    symbol: str = ""
    full_name: str = ""
    parent_base: str = ""
    mass_shift: float = 0.0
    detection_methods: List[str] = field(default_factory=list)
    biological_function: str = ""
    color: str = "#888888"
    custom_properties: Dict[str, any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Load properties from database if available."""
        if self.mod_type in MODIFICATION_PROPERTIES and not self.symbol:
            props = MODIFICATION_PROPERTIES[self.mod_type]
            self.symbol = self.mod_type.value
            self.full_name = props.get("full_name", "")
            self.parent_base = props.get("parent_base", "")
            self.mass_shift = props.get("mass_shift", 0.0)
            self.detection_methods = props.get("detection_methods", [])
            self.biological_function = props.get("biological_function", "")
            self.color = props.get("color", "#888888")
    
    @classmethod
    def m6A(cls) -> 'Modification':
        """Create an m6A modification."""
        return cls(ModificationType.M6A)
    
    @classmethod
    def m5C(cls) -> 'Modification':
        """Create an m5C modification."""
        return cls(ModificationType.M5C)
    
    @classmethod
    def pseudouridine(cls) -> 'Modification':
        """Create a pseudouridine modification."""
        return cls(ModificationType.PSI)
    
    @classmethod
    def m1A(cls) -> 'Modification':
        """Create an m1A modification."""
        return cls(ModificationType.M1A)
    
    @classmethod
    def inosine(cls) -> 'Modification':
        """Create an inosine modification."""
        return cls(ModificationType.I)
    
    @classmethod
    def two_prime_O_methyl(cls, base: str) -> 'Modification':
        """Create a 2'-O-methylation modification for a given base."""
        base_to_type = {
            'A': ModificationType.AM,
            'C': ModificationType.CM,
            'G': ModificationType.GM,
            'U': ModificationType.UM,
        }
        return cls(base_to_type.get(base.upper(), ModificationType.OTHER))
    
    @classmethod
    def from_symbol(cls, symbol: str) -> 'Modification':
        """Create a modification from its symbol."""
        symbol_to_type = {mt.value: mt for mt in ModificationType}
        if symbol in symbol_to_type:
            return cls(symbol_to_type[symbol])
        return cls(ModificationType.UNKNOWN, symbol=symbol)
    
    def __repr__(self) -> str:
        return f"Modification({self.symbol})"
    
    def __str__(self) -> str:
        return self.symbol


@dataclass
class ModificationSite:
    """
    Represents a specific modification at a position in an RNA.
    
    Attributes:
        position: 0-indexed position in the sequence
        modification: The Modification object
        confidence: Confidence score (0-1) from detection
        stoichiometry: Fraction of molecules modified (0-1)
        evidence: Experimental evidence/method
        source: Data source (database, experiment, prediction)
        annotation: Additional notes
    
    Example:
        >>> site = ModificationSite(
        ...     position=100,
        ...     modification=Modification.m6A(),
        ...     confidence=0.95
        ... )
    """
    position: int
    modification: Modification
    confidence: Optional[float] = None
    stoichiometry: Optional[float] = None
    evidence: Optional[str] = None
    source: Optional[str] = None
    annotation: Optional[str] = None
    
    def __post_init__(self):
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be 0-1, got {self.confidence}")
        if self.stoichiometry is not None and not 0 <= self.stoichiometry <= 1:
            raise ValueError(f"Stoichiometry must be 0-1, got {self.stoichiometry}")
    
    def __repr__(self) -> str:
        return f"ModificationSite(pos={self.position}, mod={self.modification.symbol})"


class ModificationTrack:
    """
    A collection of modification sites for an RNA molecule.
    
    Provides methods for adding, querying, and analyzing modifications
    across an RNA sequence.
    
    Attributes:
        sites: List of ModificationSite objects
        sequence_length: Length of the associated sequence
        name: Optional track name
    
    Example:
        >>> track = ModificationTrack(sequence_length=1000, name="m6A sites")
        >>> track.add_site(ModificationSite(100, Modification.m6A(), 0.9))
        >>> track.get_sites_in_range(50, 150)
        [ModificationSite(pos=100, mod=m6A)]
    """
    
    def __init__(
        self,
        sequence_length: int,
        name: Optional[str] = None,
        sites: Optional[List[ModificationSite]] = None
    ):
        self.sequence_length = sequence_length
        self.name = name
        self.sites: List[ModificationSite] = sites or []
        self._position_index: Dict[int, List[ModificationSite]] = {}
        
        # Build index
        for site in self.sites:
            self._add_to_index(site)
    
    def _add_to_index(self, site: ModificationSite) -> None:
        """Add site to position index."""
        if site.position not in self._position_index:
            self._position_index[site.position] = []
        self._position_index[site.position].append(site)
    
    def add_site(self, site: ModificationSite) -> None:
        """Add a modification site."""
        if site.position < 0 or site.position >= self.sequence_length:
            raise ValueError(f"Position {site.position} out of range")
        self.sites.append(site)
        self._add_to_index(site)
    
    def add_sites(self, sites: List[ModificationSite]) -> None:
        """Add multiple modification sites."""
        for site in sites:
            self.add_site(site)
    
    def get_sites_at(self, position: int) -> List[ModificationSite]:
        """Get all modification sites at a position."""
        return self._position_index.get(position, [])
    
    def get_sites_in_range(
        self, 
        start: int, 
        end: int
    ) -> List[ModificationSite]:
        """Get all sites within a position range (inclusive)."""
        return [s for s in self.sites if start <= s.position <= end]
    
    def get_sites_by_type(
        self, 
        mod_type: ModificationType
    ) -> List[ModificationSite]:
        """Get all sites of a specific modification type."""
        return [s for s in self.sites if s.modification.mod_type == mod_type]
    
    def filter_by_confidence(
        self, 
        min_confidence: float
    ) -> List[ModificationSite]:
        """Get sites above a confidence threshold."""
        return [s for s in self.sites 
                if s.confidence is not None and s.confidence >= min_confidence]
    
    def get_modification_density(
        self, 
        window_size: int = 100
    ) -> List[Tuple[int, float]]:
        """
        Calculate modification density across the sequence.
        
        Args:
            window_size: Sliding window size
        
        Returns:
            List of (position, density) tuples
        """
        densities = []
        for i in range(0, self.sequence_length - window_size + 1):
            count = len(self.get_sites_in_range(i, i + window_size - 1))
            density = count / window_size
            densities.append((i + window_size // 2, density))
        return densities
    
    def to_bed_format(self, sequence_name: str = "RNA") -> str:
        """Export sites to BED format."""
        lines = []
        for site in self.sites:
            score = int(site.confidence * 1000) if site.confidence else 0
            lines.append(
                f"{sequence_name}\t{site.position}\t{site.position + 1}\t"
                f"{site.modification.symbol}\t{score}\t+"
            )
        return '\n'.join(lines)
    
    @classmethod
    def from_bed(
        cls, 
        bed_string: str, 
        sequence_length: int
    ) -> 'ModificationTrack':
        """Parse modification sites from BED format."""
        track = cls(sequence_length)
        
        for line in bed_string.strip().split('\n'):
            if not line or line.startswith('#'):
                continue
            
            fields = line.split('\t')
            if len(fields) >= 4:
                position = int(fields[1])
                symbol = fields[3]
                confidence = float(fields[4]) / 1000 if len(fields) > 4 else None
                
                site = ModificationSite(
                    position=position,
                    modification=Modification.from_symbol(symbol),
                    confidence=confidence
                )
                track.add_site(site)
        
        return track
    
    def summary(self) -> Dict[str, any]:
        """Return summary statistics."""
        type_counts = {}
        for site in self.sites:
            t = site.modification.symbol
            type_counts[t] = type_counts.get(t, 0) + 1
        
        return {
            "total_sites": len(self.sites),
            "unique_positions": len(self._position_index),
            "modification_types": type_counts,
            "density": len(self.sites) / self.sequence_length if self.sequence_length > 0 else 0,
        }
    
    def __len__(self) -> int:
        return len(self.sites)
    
    def __iter__(self):
        return iter(self.sites)
    
    def __repr__(self) -> str:
        return f"ModificationTrack({len(self.sites)} sites, name='{self.name}')"


# Predefined modification consensus motifs
MODIFICATION_MOTIFS = {
    ModificationType.M6A: {
        "motif": "DRACH",  # D=A/G/U, R=A/G, A=A, C=C, H=A/C/U
        "expanded": "[AGU][AG]AC[ACU]",
        "description": "m6A consensus motif",
    },
    ModificationType.M5C: {
        "motif": "NSUN2",  # Various depending on enzyme
        "expanded": "[ACGU]C[ACGU]",
        "description": "m5C loose consensus",
    },
    ModificationType.PSI: {
        "motif": "U",  # Context-dependent
        "expanded": "U",
        "description": "Pseudouridylation site",
    },
}


def find_modification_motifs(
    sequence: str,
    mod_type: ModificationType
) -> List[int]:
    """
    Find potential modification sites based on consensus motifs.
    
    Args:
        sequence: RNA sequence
        mod_type: Type of modification to search for
    
    Returns:
        List of potential modification positions
    """
    import re
    
    if mod_type not in MODIFICATION_MOTIFS:
        return []
    
    motif_info = MODIFICATION_MOTIFS[mod_type]
    pattern = motif_info["expanded"]
    
    positions = []
    for match in re.finditer(pattern, sequence, re.IGNORECASE):
        # Position of the modified base varies by modification type
        if mod_type == ModificationType.M6A:
            positions.append(match.start() + 2)  # The A in DRACH
        else:
            positions.append(match.start())
    
    return positions
