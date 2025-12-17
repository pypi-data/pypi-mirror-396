"""
2D RNA structure visualization.

This module provides functions for visualizing RNA secondary structures
in various 2D layouts including radiate (tree), circular, NAView, and arc diagrams.

Features:
- Multiple layout algorithms
- Customizable color schemes
- Modification highlighting
- Reactivity data overlays
- Base numbering
- Publication-quality output

Example:
    >>> import rnaview as rv
    >>> rna = rv.load_structure("example.ct")
    >>> rv.plot2d(rna, layout="radiate", color_by="type")
"""

from __future__ import annotations
import math
from typing import Optional, Dict, List, Tuple, Union, Literal
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.colors import Normalize, LinearSegmentedColormap
    import matplotlib.cm as cm
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from ..core.structure import RNAStructure, BasePair, StructureType
from .colors import ColorScheme, get_colorscheme


LayoutType = Literal["radiate", "circular", "naview", "arc", "turtle"]


def _check_matplotlib():
    """Check if matplotlib is available."""
    if not HAS_MATPLOTLIB:
        raise ImportError(
            "matplotlib is required for visualization. "
            "Install it with: pip install matplotlib"
        )


def plot2d(
    structure: RNAStructure,
    layout: LayoutType = "radiate",
    ax: Optional['plt.Axes'] = None,
    figsize: Tuple[float, float] = (10, 10),
    color_scheme: Union[str, ColorScheme] = "nucleotide",
    show_sequence: bool = True,
    show_numbering: bool = True,
    numbering_interval: int = 10,
    show_modifications: bool = True,
    show_basepairs: bool = True,
    highlight_positions: Optional[List[int]] = None,
    highlight_color: str = "#FFD700",
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    dpi: int = 150,
    **kwargs
) -> 'plt.Figure':
    """
    Plot RNA secondary structure in 2D.
    
    Args:
        structure: RNAStructure object to visualize
        layout: Layout algorithm ('radiate', 'circular', 'naview', 'arc')
        ax: Optional matplotlib axes to plot on
        figsize: Figure size in inches
        color_scheme: Color scheme name or ColorScheme object
        show_sequence: Display nucleotide letters
        show_numbering: Show position numbers
        numbering_interval: Interval for position labels
        show_modifications: Highlight modification sites
        show_basepairs: Draw base pair connections
        highlight_positions: List of positions to highlight
        highlight_color: Color for highlighted positions
        title: Optional plot title
        save_path: Path to save figure (optional)
        dpi: Resolution for saved figure
        **kwargs: Additional layout-specific arguments
    
    Returns:
        matplotlib Figure object
    
    Example:
        >>> fig = plot2d(rna, layout="radiate", color_scheme="nucleotide")
        >>> plt.show()
    """
    _check_matplotlib()
    
    # Get color scheme
    if isinstance(color_scheme, str):
        colors = get_colorscheme(color_scheme)
    else:
        colors = color_scheme
    
    # Calculate layout coordinates
    if layout == "radiate":
        coords = _radiate_layout(structure, **kwargs)
    elif layout == "circular":
        coords = _circular_layout(structure, **kwargs)
    elif layout == "naview":
        coords = _naview_layout(structure, **kwargs)
    elif layout == "arc":
        return plot_arc(structure, ax=ax, figsize=figsize, 
                       color_scheme=colors, **kwargs)
    elif layout == "turtle":
        coords = _turtle_layout(structure, **kwargs)
    else:
        raise ValueError(f"Unknown layout: {layout}")
    
    # Store coordinates in structure
    structure.coordinates_2d = coords
    
    # Create figure
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()
    
    # Draw base pairs
    if show_basepairs:
        _draw_basepairs(ax, structure, coords, colors)
    
    # Draw backbone
    _draw_backbone(ax, coords, color=colors.backbone_color)
    
    # Draw nucleotides
    _draw_nucleotides(
        ax, structure, coords, colors,
        show_sequence=show_sequence,
        show_modifications=show_modifications
    )
    
    # Highlight positions
    if highlight_positions:
        _highlight_positions(ax, coords, highlight_positions, highlight_color)
    
    # Add numbering
    if show_numbering:
        _add_numbering(ax, structure, coords, numbering_interval)
    
    # Style
    ax.set_aspect('equal')
    ax.axis('off')
    
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    elif structure.name:
        ax.set_title(structure.name, fontsize=12)
    
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
    
    return fig


def plot_arc(
    structure: RNAStructure,
    ax: Optional['plt.Axes'] = None,
    figsize: Tuple[float, float] = (14, 6),
    color_scheme: Union[str, ColorScheme] = "nucleotide",
    show_sequence: bool = True,
    show_numbering: bool = True,
    numbering_interval: int = 20,
    arc_height_scale: float = 0.4,
    **kwargs
) -> 'plt.Figure':
    """
    Plot RNA structure as an arc diagram.
    
    Arc diagrams display the sequence linearly with arcs connecting
    base-paired positions. Excellent for visualizing pseudoknots.
    
    Args:
        structure: RNAStructure object
        ax: Optional matplotlib axes
        figsize: Figure size
        color_scheme: Color scheme
        show_sequence: Display nucleotide letters
        show_numbering: Show position numbers
        numbering_interval: Interval for numbering
        arc_height_scale: Scale factor for arc heights
    
    Returns:
        matplotlib Figure object
    
    Example:
        >>> fig = plot_arc(rna)
        >>> plt.show()
    """
    _check_matplotlib()
    
    if isinstance(color_scheme, str):
        colors = get_colorscheme(color_scheme)
    else:
        colors = color_scheme
    
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()
    
    n = structure.length
    
    # Draw sequence backbone (horizontal line)
    x_coords = np.arange(n)
    ax.plot(x_coords, np.zeros(n), color=colors.backbone_color, 
            linewidth=1.5, zorder=1)
    
    # Draw arcs for base pairs
    for bp in structure.base_pairs:
        span = bp.j - bp.i
        height = span * arc_height_scale
        
        # Create arc
        center = (bp.i + bp.j) / 2
        width = span
        
        # Choose color based on pair type or pseudoknot status
        if bp.is_pseudoknot:
            arc_color = colors.pseudoknot_color
            linestyle = '--'
        else:
            arc_color = colors.basepair_color
            linestyle = '-'
        
        arc = mpatches.Arc(
            (center, 0), width, height * 2,
            angle=0, theta1=0, theta2=180,
            color=arc_color, linewidth=1.5,
            linestyle=linestyle, zorder=2
        )
        ax.add_patch(arc)
    
    # Draw nucleotides
    for i, nt in enumerate(structure.sequence):
        color = colors.get_nucleotide_color(nt)
        circle = plt.Circle(
            (i, 0), 0.35,
            facecolor=color,
            edgecolor='black',
            linewidth=0.5,
            zorder=3
        )
        ax.add_patch(circle)
        
        # Add letter
        if show_sequence:
            ax.text(i, 0, nt, ha='center', va='center',
                   fontsize=8, fontweight='bold', zorder=4)
    
    # Add modifications
    for pos, mod in structure.modifications.items():
        ax.plot(pos, 0.6, marker='v', color=mod.color,
               markersize=8, zorder=5)
        ax.text(pos, 0.9, mod.symbol, ha='center', va='bottom',
               fontsize=6, color=mod.color)
    
    # Add numbering
    if show_numbering:
        for i in range(0, n, numbering_interval):
            ax.text(i, -0.7, str(i + 1), ha='center', va='top',
                   fontsize=8, color='gray')
    
    # Style
    max_span = max((bp.j - bp.i for bp in structure.base_pairs), default=n)
    max_height = max_span * arc_height_scale
    
    ax.set_xlim(-1, n)
    ax.set_ylim(-1.5, max_height + 1.5)
    ax.set_aspect('auto')
    ax.axis('off')
    
    if structure.name:
        ax.set_title(structure.name, fontsize=12)
    
    plt.tight_layout()
    return fig


def plot_circular(
    structure: RNAStructure,
    ax: Optional['plt.Axes'] = None,
    figsize: Tuple[float, float] = (10, 10),
    color_scheme: Union[str, ColorScheme] = "nucleotide",
    **kwargs
) -> 'plt.Figure':
    """
    Plot RNA structure in circular layout.
    
    Nucleotides are arranged in a circle with base pairs shown as chords.
    
    Args:
        structure: RNAStructure object
        ax: Optional matplotlib axes
        figsize: Figure size
        color_scheme: Color scheme
    
    Returns:
        matplotlib Figure object
    """
    return plot2d(structure, layout="circular", ax=ax, figsize=figsize,
                 color_scheme=color_scheme, **kwargs)


def plot_radiate(
    structure: RNAStructure,
    ax: Optional['plt.Axes'] = None,
    figsize: Tuple[float, float] = (10, 10),
    color_scheme: Union[str, ColorScheme] = "nucleotide",
    **kwargs
) -> 'plt.Figure':
    """
    Plot RNA structure in radiate (tree-like) layout.
    
    This is the standard secondary structure representation with
    stems and loops arranged radially.
    
    Args:
        structure: RNAStructure object
        ax: Optional matplotlib axes
        figsize: Figure size
        color_scheme: Color scheme
    
    Returns:
        matplotlib Figure object
    """
    return plot2d(structure, layout="radiate", ax=ax, figsize=figsize,
                 color_scheme=color_scheme, **kwargs)


def plot_naview(
    structure: RNAStructure,
    ax: Optional['plt.Axes'] = None,
    figsize: Tuple[float, float] = (10, 10),
    color_scheme: Union[str, ColorScheme] = "nucleotide",
    **kwargs
) -> 'plt.Figure':
    """
    Plot RNA structure using NAView algorithm.
    
    NAView produces aesthetically pleasing layouts by optimizing
    stem angles and loop sizes.
    
    Args:
        structure: RNAStructure object
        ax: Optional matplotlib axes
        figsize: Figure size
        color_scheme: Color scheme
    
    Returns:
        matplotlib Figure object
    """
    return plot2d(structure, layout="naview", ax=ax, figsize=figsize,
                 color_scheme=color_scheme, **kwargs)


# ============================================================================
# Layout algorithms
# ============================================================================

def _radiate_layout(
    structure: RNAStructure,
    bond_length: float = 1.0,
    loop_radius: float = 1.5,
    **kwargs
) -> np.ndarray:
    """
    Calculate radiate (tree-like) layout coordinates.
    
    Uses a recursive algorithm to position stems radially
    with loops as circular arrangements.
    """
    n = structure.length
    coords = np.zeros((n, 2))
    
    pair_table = structure.pair_table
    
    # Track visited positions
    visited = set()
    
    def layout_region(start: int, end: int, x: float, y: float, 
                     direction: float) -> None:
        """Recursively layout a region of the structure."""
        if start > end:
            return
        
        pos = start
        current_x, current_y = x, y
        current_dir = direction
        
        while pos <= end and pos not in visited:
            visited.add(pos)
            coords[pos] = [current_x, current_y]
            
            paired = pair_table.get(pos)
            
            if paired is not None and paired > pos and paired <= end:
                # Start of a stem
                stem_length = 0
                temp_pos = pos
                while temp_pos <= end:
                    p = pair_table.get(temp_pos)
                    if p is not None and p == paired - stem_length:
                        stem_length += 1
                        temp_pos += 1
                    else:
                        break
                
                # Layout stem
                for i in range(stem_length):
                    visited.add(pos + i)
                    visited.add(paired - i)
                    
                    dx = bond_length * math.cos(current_dir)
                    dy = bond_length * math.sin(current_dir)
                    
                    coords[pos + i] = [current_x + dx * i, current_y + dy * i]
                    coords[paired - i] = [current_x + dx * i + bond_length * math.cos(current_dir + math.pi/2),
                                         current_y + dy * i + bond_length * math.sin(current_dir + math.pi/2)]
                
                # Layout internal region (loop)
                loop_start = pos + stem_length
                loop_end = paired - stem_length
                
                if loop_end > loop_start:
                    loop_size = loop_end - loop_start + 1
                    angle_step = math.pi / max(loop_size, 1)
                    
                    center_x = coords[loop_start - 1][0] + loop_radius * math.cos(current_dir)
                    center_y = coords[loop_start - 1][1] + loop_radius * math.sin(current_dir)
                    
                    for i, lpos in enumerate(range(loop_start, loop_end + 1)):
                        if lpos not in visited:
                            visited.add(lpos)
                            angle = current_dir - math.pi/2 + angle_step * (i + 1)
                            coords[lpos] = [
                                center_x + loop_radius * math.cos(angle),
                                center_y + loop_radius * math.sin(angle)
                            ]
                
                pos = paired + 1
                current_x = coords[paired][0] + bond_length * math.cos(current_dir)
                current_y = coords[paired][1] + bond_length * math.sin(current_dir)
            else:
                # Unpaired position
                current_x += bond_length * math.cos(current_dir)
                current_y += bond_length * math.sin(current_dir)
                pos += 1
    
    # Start layout from 5' end
    layout_region(0, n - 1, 0, 0, 0)
    
    # Fill in any remaining positions (shouldn't happen with valid structure)
    for i in range(n):
        if i not in visited:
            coords[i] = [i * bond_length, 0]
    
    # Center coordinates
    coords -= coords.mean(axis=0)
    
    return coords


def _circular_layout(
    structure: RNAStructure,
    radius: float = 10.0,
    **kwargs
) -> np.ndarray:
    """
    Calculate circular layout coordinates.
    
    Places nucleotides evenly around a circle.
    """
    n = structure.length
    coords = np.zeros((n, 2))
    
    for i in range(n):
        angle = 2 * math.pi * i / n - math.pi / 2
        coords[i] = [radius * math.cos(angle), radius * math.sin(angle)]
    
    return coords


def _naview_layout(
    structure: RNAStructure,
    **kwargs
) -> np.ndarray:
    """
    Calculate NAView-style layout coordinates.
    
    This is a simplified NAView implementation that produces
    aesthetically pleasing layouts.
    """
    # For simplicity, use an improved radiate layout
    # A full NAView implementation would be more complex
    return _radiate_layout(structure, bond_length=1.2, loop_radius=2.0, **kwargs)


def _turtle_layout(
    structure: RNAStructure,
    step_size: float = 1.0,
    turn_angle: float = math.pi / 6,
    **kwargs
) -> np.ndarray:
    """
    Calculate turtle graphics-style layout.
    
    Simple layout that walks through the structure turning
    at base pairs.
    """
    n = structure.length
    coords = np.zeros((n, 2))
    
    x, y = 0, 0
    direction = 0
    pair_table = structure.pair_table
    
    for i in range(n):
        coords[i] = [x, y]
        
        # Determine turn based on structure
        paired = pair_table.get(i)
        if paired is not None:
            if paired > i:
                direction += turn_angle
            else:
                direction -= turn_angle
        
        x += step_size * math.cos(direction)
        y += step_size * math.sin(direction)
    
    # Center
    coords -= coords.mean(axis=0)
    
    return coords


# ============================================================================
# Drawing functions
# ============================================================================

def _draw_backbone(
    ax: 'plt.Axes',
    coords: np.ndarray,
    color: str = "#666666",
    linewidth: float = 1.0
) -> None:
    """Draw the backbone connecting nucleotides."""
    for i in range(len(coords) - 1):
        ax.plot(
            [coords[i, 0], coords[i + 1, 0]],
            [coords[i, 1], coords[i + 1, 1]],
            color=color, linewidth=linewidth, zorder=1
        )


def _draw_basepairs(
    ax: 'plt.Axes',
    structure: RNAStructure,
    coords: np.ndarray,
    colors: ColorScheme
) -> None:
    """Draw base pair connections."""
    for bp in structure.base_pairs:
        if bp.is_pseudoknot:
            color = colors.pseudoknot_color
            linestyle = ':'
        else:
            color = colors.basepair_color
            linestyle = '-'
        
        ax.plot(
            [coords[bp.i, 0], coords[bp.j, 0]],
            [coords[bp.i, 1], coords[bp.j, 1]],
            color=color, linewidth=1.5, linestyle=linestyle, zorder=2
        )


def _draw_nucleotides(
    ax: 'plt.Axes',
    structure: RNAStructure,
    coords: np.ndarray,
    colors: ColorScheme,
    show_sequence: bool = True,
    show_modifications: bool = True,
    node_size: float = 0.4
) -> None:
    """Draw nucleotide nodes."""
    for i, nt in enumerate(structure.sequence):
        x, y = coords[i]
        
        # Get color
        if i in structure.modifications and show_modifications:
            mod = structure.modifications[i]
            facecolor = mod.color
            edgecolor = 'black'
            linewidth = 2
        else:
            facecolor = colors.get_nucleotide_color(nt)
            edgecolor = 'black'
            linewidth = 0.5
        
        # Draw circle
        circle = plt.Circle(
            (x, y), node_size,
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=linewidth,
            zorder=3
        )
        ax.add_patch(circle)
        
        # Add nucleotide letter
        if show_sequence:
            ax.text(x, y, nt, ha='center', va='center',
                   fontsize=8, fontweight='bold', zorder=4,
                   color='white' if _is_dark(facecolor) else 'black')


def _is_dark(color: str) -> bool:
    """Check if a color is dark (for text contrast)."""
    # Simple luminance check
    if color.startswith('#'):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5
    return False


def _highlight_positions(
    ax: 'plt.Axes',
    coords: np.ndarray,
    positions: List[int],
    color: str,
    radius: float = 0.6
) -> None:
    """Highlight specific positions with a colored ring."""
    for pos in positions:
        if 0 <= pos < len(coords):
            x, y = coords[pos]
            circle = plt.Circle(
                (x, y), radius,
                facecolor='none',
                edgecolor=color,
                linewidth=3,
                zorder=5
            )
            ax.add_patch(circle)


def _add_numbering(
    ax: 'plt.Axes',
    structure: RNAStructure,
    coords: np.ndarray,
    interval: int = 10,
    offset: float = 0.8
) -> None:
    """Add position numbering to the plot."""
    for i in range(0, structure.length, interval):
        x, y = coords[i]
        
        # Calculate offset direction (away from center)
        center = coords.mean(axis=0)
        dx = x - center[0]
        dy = y - center[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            offset_x = x + offset * dx / dist
            offset_y = y + offset * dy / dist
        else:
            offset_x = x + offset
            offset_y = y
        
        ax.text(offset_x, offset_y, str(i + 1),
               ha='center', va='center',
               fontsize=7, color='gray')


def plot_reactivity_overlay(
    structure: RNAStructure,
    layout: LayoutType = "radiate",
    cmap: str = "RdYlBu_r",
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    **kwargs
) -> 'plt.Figure':
    """
    Plot structure with reactivity data overlay.
    
    Colors nucleotides by their reactivity values (e.g., SHAPE data).
    
    Args:
        structure: RNAStructure with reactivity data
        layout: Layout algorithm
        cmap: Colormap name
        vmin, vmax: Colormap range
    
    Returns:
        matplotlib Figure object
    """
    _check_matplotlib()
    
    if structure.reactivity is None:
        raise ValueError("Structure has no reactivity data")
    
    # Create custom color scheme based on reactivity
    norm = Normalize(
        vmin=vmin or np.nanmin(structure.reactivity),
        vmax=vmax or np.nanmax(structure.reactivity)
    )
    colormap = cm.get_cmap(cmap)
    
    # Create modified color scheme
    base_colors = get_colorscheme("default")
    
    class ReactivityColors(ColorScheme):
        def get_nucleotide_color(self, nt: str, position: int = -1) -> str:
            if position >= 0 and position < len(structure.reactivity):
                val = structure.reactivity[position]
                if not np.isnan(val):
                    rgba = colormap(norm(val))
                    return '#{:02x}{:02x}{:02x}'.format(
                        int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255)
                    )
            return base_colors.get_nucleotide_color(nt)
    
    fig = plot2d(structure, layout=layout, 
                color_scheme=ReactivityColors(), **kwargs)
    
    # Add colorbar
    ax = fig.axes[0]
    sm = cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Reactivity', fontsize=10)
    
    return fig
