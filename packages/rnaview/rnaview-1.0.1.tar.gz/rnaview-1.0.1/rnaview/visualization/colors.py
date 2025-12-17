"""
Color schemes for RNA visualization.

This module provides customizable color schemes for visualizing RNA structures,
including preset schemes and tools for creating custom palettes.

Available color schemes:
- nucleotide: Color by nucleotide type (A, C, G, U)
- structure: Color by structural element (stem, loop, etc.)
- conservation: Gradient for conservation scores
- reactivity: Gradient for SHAPE/DMS reactivity
- modification: Highlight modification sites
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple, Callable
from enum import Enum


class ColorPalette(Enum):
    """Predefined color palettes."""
    DEFAULT = "default"
    VARNA = "varna"
    COLORBREWER = "colorbrewer"
    VIRIDIS = "viridis"
    PUBLICATION = "publication"


@dataclass
class ColorScheme:
    """
    Color scheme for RNA visualization.
    
    Defines colors for nucleotides, structural elements, and annotations.
    
    Attributes:
        name: Scheme identifier
        nucleotide_colors: Dict mapping nucleotides to colors
        structure_colors: Dict mapping structure types to colors
        backbone_color: Color for backbone line
        basepair_color: Color for base pair connections
        pseudoknot_color: Color for pseudoknot base pairs
        modification_colors: Dict mapping modification types to colors
        highlight_color: Color for highlighted positions
        surface_color: Color for 3D surface representation
    
    Example:
        >>> scheme = ColorScheme(name="custom")
        >>> scheme.nucleotide_colors['A'] = "#FF0000"
    """
    name: str = "default"
    nucleotide_colors: Dict[str, str] = field(default_factory=lambda: {
        'A': '#E74C3C',  # Red
        'C': '#3498DB',  # Blue
        'G': '#2ECC71',  # Green
        'U': '#F39C12',  # Orange
        'T': '#F39C12',  # Same as U
        'N': '#95A5A6',  # Gray
        'X': '#95A5A6',  # Gray
    })
    structure_colors: Dict[str, str] = field(default_factory=lambda: {
        'stem': '#2C3E50',
        'hairpin_loop': '#E74C3C',
        'internal_loop': '#3498DB',
        'bulge': '#9B59B6',
        'multiloop': '#1ABC9C',
        'external': '#95A5A6',
        'pseudoknot': '#E91E63',
    })
    backbone_color: str = "#666666"
    basepair_color: str = "#34495E"
    pseudoknot_color: str = "#E91E63"
    highlight_color: str = "#FFD700"
    surface_color: str = "#3498DB"
    modification_colors: Dict[str, str] = field(default_factory=lambda: {
        'm6A': '#FF6B6B',
        'm5C': '#4ECDC4',
        'Ψ': '#45B7D1',
        'm1A': '#96CEB4',
        'I': '#FFEAA7',
        'Am': '#DDA0DD',
        'default': '#FF69B4',
    })
    
    def get_nucleotide_color(self, nt: str, position: int = -1) -> str:
        """Get color for a nucleotide."""
        return self.nucleotide_colors.get(nt.upper(), self.nucleotide_colors.get('N', '#888888'))
    
    def get_structure_color(self, structure_type: str) -> str:
        """Get color for a structural element."""
        return self.structure_colors.get(structure_type, '#888888')
    
    def get_modification_color(self, mod_type: str) -> str:
        """Get color for a modification type."""
        return self.modification_colors.get(mod_type, self.modification_colors.get('default', '#FF69B4'))
    
    def copy(self) -> 'ColorScheme':
        """Create a copy of this color scheme."""
        return ColorScheme(
            name=self.name + "_copy",
            nucleotide_colors=self.nucleotide_colors.copy(),
            structure_colors=self.structure_colors.copy(),
            backbone_color=self.backbone_color,
            basepair_color=self.basepair_color,
            pseudoknot_color=self.pseudoknot_color,
            highlight_color=self.highlight_color,
            surface_color=self.surface_color,
            modification_colors=self.modification_colors.copy(),
        )


# Predefined color schemes
_COLOR_SCHEMES: Dict[str, ColorScheme] = {}


def _init_color_schemes():
    """Initialize predefined color schemes."""
    global _COLOR_SCHEMES
    
    # Default scheme
    _COLOR_SCHEMES['default'] = ColorScheme(name='default')
    _COLOR_SCHEMES['nucleotide'] = ColorScheme(name='nucleotide')
    
    # VARNA-style scheme
    _COLOR_SCHEMES['varna'] = ColorScheme(
        name='varna',
        nucleotide_colors={
            'A': '#A0A0FF',  # Light blue
            'C': '#FFE000',  # Yellow
            'G': '#FF7070',  # Light red
            'U': '#A0FFA0',  # Light green
            'T': '#A0FFA0',
            'N': '#B0B0B0',
            'X': '#B0B0B0',
        },
        backbone_color='#606060',
        basepair_color='#404040',
    )
    
    # Publication-ready (grayscale-friendly)
    _COLOR_SCHEMES['publication'] = ColorScheme(
        name='publication',
        nucleotide_colors={
            'A': '#1f77b4',  # Blue
            'C': '#ff7f0e',  # Orange
            'G': '#2ca02c',  # Green
            'U': '#d62728',  # Red
            'T': '#d62728',
            'N': '#7f7f7f',
            'X': '#7f7f7f',
        },
        backbone_color='#2c2c2c',
        basepair_color='#1c1c1c',
        pseudoknot_color='#9467bd',
    )
    
    # Colorblind-friendly scheme
    _COLOR_SCHEMES['colorblind'] = ColorScheme(
        name='colorblind',
        nucleotide_colors={
            'A': '#0072B2',  # Blue
            'C': '#E69F00',  # Orange
            'G': '#009E73',  # Teal
            'U': '#CC79A7',  # Pink
            'T': '#CC79A7',
            'N': '#999999',
            'X': '#999999',
        },
        backbone_color='#444444',
        basepair_color='#222222',
        pseudoknot_color='#D55E00',
    )
    
    # Monochrome
    _COLOR_SCHEMES['monochrome'] = ColorScheme(
        name='monochrome',
        nucleotide_colors={
            'A': '#333333',
            'C': '#666666',
            'G': '#999999',
            'U': '#CCCCCC',
            'T': '#CCCCCC',
            'N': '#AAAAAA',
            'X': '#AAAAAA',
        },
        backbone_color='#000000',
        basepair_color='#000000',
        pseudoknot_color='#444444',
    )
    
    # Structure-based coloring
    _COLOR_SCHEMES['structure'] = ColorScheme(
        name='structure',
        nucleotide_colors={
            'A': '#808080',
            'C': '#808080',
            'G': '#808080',
            'U': '#808080',
            'T': '#808080',
            'N': '#808080',
            'X': '#808080',
        },
        structure_colors={
            'stem': '#2C3E50',
            'hairpin_loop': '#E74C3C',
            'internal_loop': '#3498DB',
            'bulge': '#9B59B6',
            'multiloop': '#1ABC9C',
            'external': '#BDC3C7',
            'pseudoknot': '#E91E63',
        },
    )
    
    # Pastel scheme
    _COLOR_SCHEMES['pastel'] = ColorScheme(
        name='pastel',
        nucleotide_colors={
            'A': '#FFB3BA',  # Light pink
            'C': '#BAFFC9',  # Light green
            'G': '#BAE1FF',  # Light blue
            'U': '#FFFFBA',  # Light yellow
            'T': '#FFFFBA',
            'N': '#E0E0E0',
            'X': '#E0E0E0',
        },
        backbone_color='#AAAAAA',
        basepair_color='#888888',
    )
    
    # Dark theme
    _COLOR_SCHEMES['dark'] = ColorScheme(
        name='dark',
        nucleotide_colors={
            'A': '#FF6B6B',
            'C': '#4ECDC4',
            'G': '#95E1D3',
            'U': '#F38181',
            'T': '#F38181',
            'N': '#666666',
            'X': '#666666',
        },
        backbone_color='#444444',
        basepair_color='#555555',
        pseudoknot_color='#AA66CC',
        surface_color='#2E4057',
    )


# Initialize schemes on module load
_init_color_schemes()


def get_colorscheme(name: str = "default") -> ColorScheme:
    """
    Get a predefined color scheme by name.
    
    Args:
        name: Color scheme name
    
    Returns:
        ColorScheme object
    
    Available schemes:
        - default / nucleotide: Standard nucleotide coloring
        - varna: VARNA-style colors
        - publication: Publication-ready colors
        - colorblind: Colorblind-friendly palette
        - monochrome: Grayscale
        - structure: Color by structural elements
        - pastel: Soft pastel colors
        - dark: Dark theme colors
    
    Example:
        >>> scheme = get_colorscheme("publication")
    """
    name = name.lower()
    if name not in _COLOR_SCHEMES:
        available = ', '.join(_COLOR_SCHEMES.keys())
        raise ValueError(f"Unknown color scheme: {name}. Available: {available}")
    return _COLOR_SCHEMES[name].copy()


def list_colorschemes() -> List[str]:
    """Return list of available color scheme names."""
    return list(_COLOR_SCHEMES.keys())


def register_colorscheme(scheme: ColorScheme) -> None:
    """
    Register a custom color scheme.
    
    Args:
        scheme: ColorScheme object to register
    
    Example:
        >>> custom = ColorScheme(name="my_scheme")
        >>> custom.nucleotide_colors['A'] = "#FF0000"
        >>> register_colorscheme(custom)
    """
    _COLOR_SCHEMES[scheme.name.lower()] = scheme


def create_gradient_colorscheme(
    low_color: str = "#FFFFFF",
    high_color: str = "#FF0000",
    name: str = "gradient"
) -> ColorScheme:
    """
    Create a color scheme with gradient-based nucleotide coloring.
    
    Useful for coloring by conservation, reactivity, or other continuous values.
    
    Args:
        low_color: Color for low values (hex)
        high_color: Color for high values (hex)
        name: Scheme name
    
    Returns:
        ColorScheme with gradient capability
    """
    scheme = ColorScheme(name=name)
    scheme._low_color = low_color
    scheme._high_color = high_color
    
    def _interpolate_color(value: float) -> str:
        """Interpolate between low and high colors."""
        value = max(0, min(1, value))  # Clamp to [0, 1]
        
        # Parse hex colors
        low_r = int(low_color[1:3], 16)
        low_g = int(low_color[3:5], 16)
        low_b = int(low_color[5:7], 16)
        
        high_r = int(high_color[1:3], 16)
        high_g = int(high_color[3:5], 16)
        high_b = int(high_color[5:7], 16)
        
        # Interpolate
        r = int(low_r + (high_r - low_r) * value)
        g = int(low_g + (high_g - low_g) * value)
        b = int(low_b + (high_b - low_b) * value)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    scheme._interpolate = _interpolate_color
    return scheme


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def lighten_color(hex_color: str, factor: float = 0.3) -> str:
    """Lighten a hex color by a factor."""
    r, g, b = hex_to_rgb(hex_color)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return rgb_to_hex(r, g, b)


def darken_color(hex_color: str, factor: float = 0.3) -> str:
    """Darken a hex color by a factor."""
    r, g, b = hex_to_rgb(hex_color)
    r = int(r * (1 - factor))
    g = int(g * (1 - factor))
    b = int(b * (1 - factor))
    return rgb_to_hex(r, g, b)


# Colormaps for continuous data
COLORMAPS = {
    'reactivity': ['#FFFFFF', '#FFFFCC', '#FFEDA0', '#FED976', '#FEB24C', 
                   '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026'],
    'conservation': ['#F7FBFF', '#DEEBF7', '#C6DBEF', '#9ECAE1', '#6BAED6',
                     '#4292C6', '#2171B5', '#08519C', '#08306B'],
    'divergence': ['#006837', '#1A9850', '#66BD63', '#A6D96A', '#D9EF8B',
                   '#FFFFBF', '#FEE08B', '#FDAE61', '#F46D43', '#D73027', '#A50026'],
}


def get_colormap_colors(name: str) -> List[str]:
    """Get colors for a named colormap."""
    if name not in COLORMAPS:
        raise ValueError(f"Unknown colormap: {name}")
    return COLORMAPS[name].copy()
