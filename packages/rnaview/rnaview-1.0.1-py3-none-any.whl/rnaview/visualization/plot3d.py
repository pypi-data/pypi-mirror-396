"""
3D RNA structure visualization.

This module provides functions for visualizing RNA tertiary structures
using various representations including cartoon, ribbon, and surface.

Requires plotly for interactive 3D visualization.

Example:
    >>> import rnaview as rv
    >>> rna = rv.load_structure("example.pdb")
    >>> rv.plot3d(rna, style="ribbon")
"""

from __future__ import annotations
from typing import Optional, Dict, List, Tuple, Union, Literal
import numpy as np

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from ..core.structure import RNAStructure
from .colors import ColorScheme, get_colorscheme


StyleType = Literal["backbone", "ribbon", "surface", "cartoon", "spheres"]


def _check_plotly():
    """Check if plotly is available."""
    if not HAS_PLOTLY:
        raise ImportError(
            "plotly is required for 3D visualization. "
            "Install it with: pip install plotly"
        )


def plot3d(
    structure: RNAStructure,
    style: StyleType = "backbone",
    color_scheme: Union[str, ColorScheme] = "nucleotide",
    show_sequence: bool = False,
    show_basepairs: bool = True,
    show_modifications: bool = True,
    highlight_positions: Optional[List[int]] = None,
    title: Optional[str] = None,
    width: int = 800,
    height: int = 600,
    backend: str = "plotly",
    **kwargs
) -> Union['go.Figure', 'plt.Figure']:
    """
    Plot RNA tertiary structure in 3D.
    
    Args:
        structure: RNAStructure object with 3D coordinates
        style: Visualization style ('backbone', 'ribbon', 'surface', 'spheres')
        color_scheme: Color scheme name or ColorScheme object
        show_sequence: Label nucleotides with letters
        show_basepairs: Draw base pair connections
        show_modifications: Highlight modification sites
        highlight_positions: List of positions to highlight
        title: Plot title
        width: Figure width in pixels
        height: Figure height in pixels
        backend: Plotting backend ('plotly' or 'matplotlib')
    
    Returns:
        plotly Figure or matplotlib Figure
    
    Example:
        >>> fig = plot3d(rna, style="ribbon")
        >>> fig.show()
    """
    if structure.coordinates_3d is None:
        raise ValueError(
            "Structure has no 3D coordinates. "
            "Load a PDB/mmCIF file or use a 2D visualization."
        )
    
    if backend == "plotly":
        return _plot3d_plotly(
            structure, style, color_scheme, show_sequence,
            show_basepairs, show_modifications, highlight_positions,
            title, width, height, **kwargs
        )
    else:
        return _plot3d_matplotlib(
            structure, style, color_scheme, show_sequence,
            show_basepairs, show_modifications, highlight_positions,
            title, **kwargs
        )


def _plot3d_plotly(
    structure: RNAStructure,
    style: StyleType,
    color_scheme: Union[str, ColorScheme],
    show_sequence: bool,
    show_basepairs: bool,
    show_modifications: bool,
    highlight_positions: Optional[List[int]],
    title: Optional[str],
    width: int,
    height: int,
    **kwargs
) -> 'go.Figure':
    """Create 3D plot using plotly."""
    _check_plotly()
    
    coords = structure.coordinates_3d
    
    if isinstance(color_scheme, str):
        colors = get_colorscheme(color_scheme)
    else:
        colors = color_scheme
    
    fig = go.Figure()
    
    # Get nucleotide colors
    nt_colors = [colors.get_nucleotide_color(nt) for nt in structure.sequence]
    
    # Draw based on style
    if style == "backbone":
        # Backbone trace
        fig.add_trace(go.Scatter3d(
            x=coords[:, 0],
            y=coords[:, 1],
            z=coords[:, 2],
            mode='lines+markers',
            marker=dict(
                size=6,
                color=nt_colors,
                opacity=0.9,
            ),
            line=dict(
                color=colors.backbone_color,
                width=3,
            ),
            text=[f"{i+1}: {nt}" for i, nt in enumerate(structure.sequence)],
            hoverinfo='text',
            name='Backbone'
        ))
    
    elif style == "spheres":
        # Sphere representation
        fig.add_trace(go.Scatter3d(
            x=coords[:, 0],
            y=coords[:, 1],
            z=coords[:, 2],
            mode='markers',
            marker=dict(
                size=10,
                color=nt_colors,
                opacity=0.9,
            ),
            text=[f"{i+1}: {nt}" for i, nt in enumerate(structure.sequence)],
            hoverinfo='text',
            name='Nucleotides'
        ))
        
        # Add backbone
        fig.add_trace(go.Scatter3d(
            x=coords[:, 0],
            y=coords[:, 1],
            z=coords[:, 2],
            mode='lines',
            line=dict(
                color=colors.backbone_color,
                width=2,
            ),
            hoverinfo='none',
            name='Backbone'
        ))
    
    elif style == "ribbon":
        # Ribbon representation (smoothed backbone)
        fig = _plot_ribbon(fig, structure, coords, colors)
    
    elif style == "surface":
        # Surface representation
        fig = _plot_surface(fig, structure, coords, colors)
    
    # Draw base pairs
    if show_basepairs and structure.base_pairs:
        for bp in structure.base_pairs:
            color = colors.pseudoknot_color if bp.is_pseudoknot else colors.basepair_color
            
            fig.add_trace(go.Scatter3d(
                x=[coords[bp.i, 0], coords[bp.j, 0]],
                y=[coords[bp.i, 1], coords[bp.j, 1]],
                z=[coords[bp.i, 2], coords[bp.j, 2]],
                mode='lines',
                line=dict(
                    color=color,
                    width=3,
                    dash='dash' if bp.is_pseudoknot else 'solid'
                ),
                hoverinfo='none',
                showlegend=False
            ))
    
    # Highlight modifications
    if show_modifications and structure.modifications:
        mod_positions = list(structure.modifications.keys())
        mod_coords = coords[mod_positions]
        mod_colors = [structure.modifications[p].color for p in mod_positions]
        mod_labels = [structure.modifications[p].symbol for p in mod_positions]
        
        fig.add_trace(go.Scatter3d(
            x=mod_coords[:, 0],
            y=mod_coords[:, 1],
            z=mod_coords[:, 2],
            mode='markers+text',
            marker=dict(
                size=12,
                color=mod_colors,
                symbol='diamond',
                line=dict(color='black', width=1)
            ),
            text=mod_labels,
            textposition='top center',
            name='Modifications'
        ))
    
    # Highlight specific positions
    if highlight_positions:
        hl_coords = coords[highlight_positions]
        fig.add_trace(go.Scatter3d(
            x=hl_coords[:, 0],
            y=hl_coords[:, 1],
            z=hl_coords[:, 2],
            mode='markers',
            marker=dict(
                size=15,
                color='yellow',
                opacity=0.7,
                symbol='circle',
                line=dict(color='orange', width=2)
            ),
            text=[f"Position {p+1}" for p in highlight_positions],
            hoverinfo='text',
            name='Highlighted'
        ))
    
    # Add sequence labels
    if show_sequence:
        fig.add_trace(go.Scatter3d(
            x=coords[:, 0],
            y=coords[:, 1],
            z=coords[:, 2],
            mode='text',
            text=list(structure.sequence),
            textposition='top center',
            textfont=dict(size=10),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Layout
    fig.update_layout(
        title=title or structure.name or "RNA 3D Structure",
        width=width,
        height=height,
        scene=dict(
            xaxis_title='X (Å)',
            yaxis_title='Y (Å)',
            zaxis_title='Z (Å)',
            aspectmode='data'
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig


def _plot_ribbon(
    fig: 'go.Figure',
    structure: RNAStructure,
    coords: np.ndarray,
    colors: ColorScheme
) -> 'go.Figure':
    """Add ribbon representation to plotly figure."""
    from scipy.interpolate import splprep, splev
    
    # Smooth the backbone with spline interpolation
    try:
        # Parameterize by arc length
        tck, u = splprep([coords[:, 0], coords[:, 1], coords[:, 2]], s=0, k=3)
        
        # Generate smooth curve
        u_new = np.linspace(0, 1, len(coords) * 5)
        smooth_coords = np.array(splev(u_new, tck)).T
        
        # Create ribbon as tube
        fig.add_trace(go.Scatter3d(
            x=smooth_coords[:, 0],
            y=smooth_coords[:, 1],
            z=smooth_coords[:, 2],
            mode='lines',
            line=dict(
                color=colors.backbone_color,
                width=8,
            ),
            hoverinfo='none',
            name='Ribbon'
        ))
    except:
        # Fall back to simple backbone if spline fails
        fig.add_trace(go.Scatter3d(
            x=coords[:, 0],
            y=coords[:, 1],
            z=coords[:, 2],
            mode='lines',
            line=dict(
                color=colors.backbone_color,
                width=5,
            ),
            hoverinfo='none',
            name='Backbone'
        ))
    
    # Add nucleotide markers
    nt_colors = [colors.get_nucleotide_color(nt) for nt in structure.sequence]
    fig.add_trace(go.Scatter3d(
        x=coords[:, 0],
        y=coords[:, 1],
        z=coords[:, 2],
        mode='markers',
        marker=dict(
            size=8,
            color=nt_colors,
            opacity=0.9,
        ),
        text=[f"{i+1}: {nt}" for i, nt in enumerate(structure.sequence)],
        hoverinfo='text',
        name='Nucleotides'
    ))
    
    return fig


def _plot_surface(
    fig: 'go.Figure',
    structure: RNAStructure,
    coords: np.ndarray,
    colors: ColorScheme,
    probe_radius: float = 1.4
) -> 'go.Figure':
    """Add surface representation to plotly figure."""
    # Simplified surface using convex hull or mesh
    # Full molecular surface calculation would require more complex algorithms
    
    from scipy.spatial import ConvexHull
    
    try:
        hull = ConvexHull(coords)
        
        # Get hull vertices and faces
        vertices = coords[hull.vertices]
        
        fig.add_trace(go.Mesh3d(
            x=coords[:, 0],
            y=coords[:, 1],
            z=coords[:, 2],
            alphahull=5,
            opacity=0.3,
            color=colors.surface_color,
            name='Surface'
        ))
    except:
        pass
    
    # Still show backbone
    fig.add_trace(go.Scatter3d(
        x=coords[:, 0],
        y=coords[:, 1],
        z=coords[:, 2],
        mode='lines+markers',
        marker=dict(
            size=6,
            color=[colors.get_nucleotide_color(nt) for nt in structure.sequence],
            opacity=0.9,
        ),
        line=dict(
            color=colors.backbone_color,
            width=3,
        ),
        text=[f"{i+1}: {nt}" for i, nt in enumerate(structure.sequence)],
        hoverinfo='text',
        name='Backbone'
    ))
    
    return fig


def _plot3d_matplotlib(
    structure: RNAStructure,
    style: StyleType,
    color_scheme: Union[str, ColorScheme],
    show_sequence: bool,
    show_basepairs: bool,
    show_modifications: bool,
    highlight_positions: Optional[List[int]],
    title: Optional[str],
    **kwargs
) -> 'plt.Figure':
    """Create 3D plot using matplotlib."""
    if not HAS_MATPLOTLIB:
        raise ImportError(
            "matplotlib is required for matplotlib backend. "
            "Install it with: pip install matplotlib"
        )
    
    coords = structure.coordinates_3d
    
    if isinstance(color_scheme, str):
        colors = get_colorscheme(color_scheme)
    else:
        colors = color_scheme
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Get colors for nucleotides
    nt_colors = [colors.get_nucleotide_color(nt) for nt in structure.sequence]
    
    # Plot backbone
    ax.plot(coords[:, 0], coords[:, 1], coords[:, 2],
           color=colors.backbone_color, linewidth=2, alpha=0.7)
    
    # Plot nucleotides as spheres
    if style in ['backbone', 'spheres']:
        ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2],
                  c=nt_colors, s=50 if style == 'backbone' else 100,
                  edgecolors='black', linewidth=0.5)
    
    # Plot base pairs
    if show_basepairs:
        for bp in structure.base_pairs:
            color = colors.pseudoknot_color if bp.is_pseudoknot else colors.basepair_color
            linestyle = ':' if bp.is_pseudoknot else '-'
            
            ax.plot([coords[bp.i, 0], coords[bp.j, 0]],
                   [coords[bp.i, 1], coords[bp.j, 1]],
                   [coords[bp.i, 2], coords[bp.j, 2]],
                   color=color, linewidth=1.5, linestyle=linestyle)
    
    # Highlight modifications
    if show_modifications and structure.modifications:
        mod_positions = list(structure.modifications.keys())
        mod_coords = coords[mod_positions]
        mod_colors = [structure.modifications[p].color for p in mod_positions]
        
        ax.scatter(mod_coords[:, 0], mod_coords[:, 1], mod_coords[:, 2],
                  c=mod_colors, s=150, marker='D',
                  edgecolors='black', linewidth=1)
    
    # Highlight positions
    if highlight_positions:
        hl_coords = coords[highlight_positions]
        ax.scatter(hl_coords[:, 0], hl_coords[:, 1], hl_coords[:, 2],
                  c='yellow', s=200, marker='o', alpha=0.5,
                  edgecolors='orange', linewidth=2)
    
    # Labels
    ax.set_xlabel('X (Å)')
    ax.set_ylabel('Y (Å)')
    ax.set_zlabel('Z (Å)')
    ax.set_title(title or structure.name or "RNA 3D Structure")
    
    plt.tight_layout()
    return fig


def plot_ribbon(
    structure: RNAStructure,
    **kwargs
) -> Union['go.Figure', 'plt.Figure']:
    """
    Plot RNA structure with ribbon representation.
    
    Convenience function for ribbon-style visualization.
    """
    return plot3d(structure, style="ribbon", **kwargs)


def plot_surface(
    structure: RNAStructure,
    **kwargs
) -> Union['go.Figure', 'plt.Figure']:
    """
    Plot RNA structure with surface representation.
    
    Convenience function for surface visualization.
    """
    return plot3d(structure, style="surface", **kwargs)


def animate_trajectory(
    structures: List[RNAStructure],
    interval: int = 100,
    **kwargs
) -> 'go.Figure':
    """
    Create animated 3D visualization from multiple structures.
    
    Useful for visualizing MD trajectories or conformational changes.
    
    Args:
        structures: List of RNAStructure objects (must have 3D coords)
        interval: Frame interval in milliseconds
    
    Returns:
        Animated plotly Figure
    """
    _check_plotly()
    
    if not all(s.coordinates_3d is not None for s in structures):
        raise ValueError("All structures must have 3D coordinates")
    
    # Create frames
    frames = []
    for i, struct in enumerate(structures):
        coords = struct.coordinates_3d
        frame = go.Frame(
            data=[go.Scatter3d(
                x=coords[:, 0],
                y=coords[:, 1],
                z=coords[:, 2],
                mode='lines+markers',
                marker=dict(size=6),
                line=dict(width=3),
            )],
            name=f"frame_{i}"
        )
        frames.append(frame)
    
    # Initial figure
    initial_coords = structures[0].coordinates_3d
    fig = go.Figure(
        data=[go.Scatter3d(
            x=initial_coords[:, 0],
            y=initial_coords[:, 1],
            z=initial_coords[:, 2],
            mode='lines+markers',
            marker=dict(size=6),
            line=dict(width=3),
        )],
        frames=frames
    )
    
    # Add animation controls
    fig.update_layout(
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': interval},
                        'fromcurrent': True
                    }]
                },
                {
                    'label': 'Pause',
                    'method': 'animate',
                    'args': [[None], {
                        'frame': {'duration': 0},
                        'mode': 'immediate'
                    }]
                }
            ]
        }],
        sliders=[{
            'steps': [
                {'args': [[f.name], {'frame': {'duration': 0}, 'mode': 'immediate'}],
                 'label': str(i), 'method': 'animate'}
                for i, f in enumerate(frames)
            ]
        }]
    )
    
    return fig
