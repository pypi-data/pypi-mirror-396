"""
Integration with various RNA structure prediction tools.

This module provides a unified interface for predicting RNA secondary
structures using different tools and methods:
- ViennaRNA Package (RNAfold)
- LinearFold
- SPOT-RNA
- E2Efold
- UFold
- Custom predictors

Example:
    >>> from rnaview.integrations import predict_structure, list_predictors
    >>> list_predictors()
    ['viennarna', 'linearfold', 'contrafold', 'mxfold2', ...]
    >>> rna = predict_structure(sequence, method='viennarna')
"""

from __future__ import annotations
from typing import Optional, List, Dict, Tuple, Union, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import subprocess
import tempfile
import os
from pathlib import Path

from ..core.structure import RNAStructure


@dataclass
class PredictionResult:
    """
    Container for structure prediction results.
    
    Attributes:
        structure: Predicted RNAStructure
        energy: Predicted free energy (if available)
        confidence: Prediction confidence scores (if available)
        method: Prediction method used
        metadata: Additional method-specific data
    """
    structure: RNAStructure
    energy: Optional[float] = None
    confidence: Optional[List[float]] = None
    method: str = "unknown"
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Predictor(ABC):
    """Abstract base class for structure predictors."""
    
    name: str = "base"
    description: str = "Base predictor"
    supports_constraints: bool = False
    supports_modifications: bool = False
    
    @abstractmethod
    def predict(
        self,
        sequence: str,
        constraints: Optional[str] = None,
        **kwargs
    ) -> PredictionResult:
        """
        Predict secondary structure for a sequence.
        
        Args:
            sequence: RNA sequence
            constraints: Optional structure constraints
            **kwargs: Method-specific parameters
        
        Returns:
            PredictionResult object
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the predictor is available/installed."""
        pass


class ViennaRNAPredictor(Predictor):
    """ViennaRNA Package predictor using RNAfold."""
    
    name = "viennarna"
    description = "ViennaRNA Package - thermodynamic MFE prediction"
    supports_constraints = True
    supports_modifications = False
    
    def __init__(self, rnafold_path: str = "RNAfold"):
        self.rnafold_path = rnafold_path
    
    def is_available(self) -> bool:
        """Check if RNAfold is installed."""
        try:
            result = subprocess.run(
                [self.rnafold_path, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def predict(
        self,
        sequence: str,
        constraints: Optional[str] = None,
        temperature: float = 37.0,
        dangles: int = 2,
        no_lp: bool = False,
        **kwargs
    ) -> PredictionResult:
        """
        Predict structure using RNAfold.
        
        Args:
            sequence: RNA sequence
            constraints: Dot-bracket constraints (. for unconstrained)
            temperature: Folding temperature in Celsius
            dangles: Dangling end treatment (0, 1, 2, 3)
            no_lp: Disallow lonely pairs
        """
        # Build command
        cmd = [
            self.rnafold_path,
            f"--temp={temperature}",
            f"--dangles={dangles}",
            "--noPS",  # Don't generate PostScript
        ]
        
        if no_lp:
            cmd.append("--noLP")
        
        if constraints:
            cmd.append("-C")
        
        # Prepare input
        input_data = f">seq\n{sequence}"
        if constraints:
            input_data += f"\n{constraints}"
        
        # Run RNAfold
        try:
            result = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=60
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("RNAfold timed out")
        
        if result.returncode != 0:
            raise RuntimeError(f"RNAfold failed: {result.stderr}")
        
        # Parse output
        lines = result.stdout.strip().split('\n')
        structure_line = lines[-1]
        
        # Extract structure and energy
        # Format: "..(((...))).. (-5.60)"
        parts = structure_line.split()
        dotbracket = parts[0]
        energy = None
        
        if len(parts) > 1:
            energy_str = parts[-1].strip('()')
            try:
                energy = float(energy_str)
            except ValueError:
                pass
        
        rna = RNAStructure(
            sequence=sequence,
            dotbracket=dotbracket,
            name="RNAfold_prediction"
        )
        rna.metadata['method'] = 'RNAfold'
        rna.metadata['temperature'] = temperature
        
        return PredictionResult(
            structure=rna,
            energy=energy,
            method=self.name,
            metadata={'temperature': temperature, 'dangles': dangles}
        )


class LinearFoldPredictor(Predictor):
    """LinearFold predictor for fast folding."""
    
    name = "linearfold"
    description = "LinearFold - O(n) time complexity prediction"
    supports_constraints = False
    supports_modifications = False
    
    def __init__(self, linearfold_path: str = "linearfold"):
        self.linearfold_path = linearfold_path
    
    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                [self.linearfold_path],
                input="ACGU",
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def predict(
        self,
        sequence: str,
        constraints: Optional[str] = None,
        beam_size: int = 100,
        **kwargs
    ) -> PredictionResult:
        """
        Predict structure using LinearFold.
        
        Args:
            sequence: RNA sequence
            beam_size: Beam search size (larger = more accurate, slower)
        """
        try:
            result = subprocess.run(
                [self.linearfold_path, "-b", str(beam_size)],
                input=sequence,
                capture_output=True,
                text=True,
                timeout=60
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("LinearFold timed out")
        except FileNotFoundError:
            raise RuntimeError("LinearFold not found. Install from https://github.com/LinearFold/LinearFold")
        
        if result.returncode != 0:
            raise RuntimeError(f"LinearFold failed: {result.stderr}")
        
        # Parse output
        lines = result.stdout.strip().split('\n')
        dotbracket = lines[-1].split()[0] if lines else '.' * len(sequence)
        
        rna = RNAStructure(
            sequence=sequence,
            dotbracket=dotbracket,
            name="LinearFold_prediction"
        )
        
        return PredictionResult(
            structure=rna,
            method=self.name,
            metadata={'beam_size': beam_size}
        )


class ContraFoldPredictor(Predictor):
    """CONTRAfold predictor."""
    
    name = "contrafold"
    description = "CONTRAfold - machine learning based prediction"
    supports_constraints = False
    supports_modifications = False
    
    def __init__(self, contrafold_path: str = "contrafold"):
        self.contrafold_path = contrafold_path
    
    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                [self.contrafold_path, "predict"],
                capture_output=True,
                timeout=5
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def predict(
        self,
        sequence: str,
        constraints: Optional[str] = None,
        **kwargs
    ) -> PredictionResult:
        """Predict structure using CONTRAfold."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(f">seq\n{sequence}\n")
            input_file = f.name
        
        try:
            result = subprocess.run(
                [self.contrafold_path, "predict", input_file],
                capture_output=True,
                text=True,
                timeout=60
            )
        finally:
            os.unlink(input_file)
        
        if result.returncode != 0:
            raise RuntimeError(f"CONTRAfold failed: {result.stderr}")
        
        # Parse output
        lines = result.stdout.strip().split('\n')
        dotbracket = '.' * len(sequence)
        for line in lines:
            if line and not line.startswith('>'):
                if set(line).issubset(set('().')):
                    dotbracket = line
                    break
        
        rna = RNAStructure(
            sequence=sequence,
            dotbracket=dotbracket,
            name="CONTRAfold_prediction"
        )
        
        return PredictionResult(structure=rna, method=self.name)


class FallbackPredictor(Predictor):
    """
    Simple fallback predictor using basic pairing rules.
    
    Used when no external tools are available.
    Implements a simple dynamic programming MFE algorithm.
    """
    
    name = "fallback"
    description = "Basic built-in predictor (no external dependencies)"
    supports_constraints = False
    supports_modifications = False
    
    def is_available(self) -> bool:
        return True  # Always available
    
    def predict(
        self,
        sequence: str,
        constraints: Optional[str] = None,
        min_loop_size: int = 3,
        **kwargs
    ) -> PredictionResult:
        """
        Predict structure using simple DP algorithm.
        
        This is a basic implementation for demonstration.
        For production use, prefer ViennaRNA or other validated tools.
        """
        n = len(sequence)
        seq = sequence.upper()
        
        # Scoring (simplified)
        def can_pair(i: int, j: int) -> bool:
            pair = (seq[i], seq[j])
            return pair in {('A', 'U'), ('U', 'A'), ('G', 'C'), ('C', 'G'), 
                           ('G', 'U'), ('U', 'G')}
        
        # DP table
        dp = [[0] * n for _ in range(n)]
        trace = [[None] * n for _ in range(n)]
        
        # Fill DP table
        for length in range(min_loop_size + 2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                
                # Option 1: j is unpaired
                dp[i][j] = dp[i][j-1] if j > i else 0
                trace[i][j] = ('unpaired', j)
                
                # Option 2: i pairs with k (where k < j)
                for k in range(i + min_loop_size + 1, j + 1):
                    if can_pair(i, k):
                        score = 1  # Simplified scoring
                        if k < j:
                            score += dp[k+1][j]
                        if i + 1 <= k - 1:
                            score += dp[i+1][k-1]
                        
                        if score > dp[i][j]:
                            dp[i][j] = score
                            trace[i][j] = ('pair', i, k)
        
        # Traceback
        structure = ['.'] * n
        
        def traceback(i: int, j: int):
            if i >= j:
                return
            
            if trace[i][j] is None:
                return
            
            action = trace[i][j]
            if action[0] == 'unpaired':
                traceback(i, j - 1)
            elif action[0] == 'pair':
                _, pi, pj = action
                structure[pi] = '('
                structure[pj] = ')'
                if pi + 1 <= pj - 1:
                    traceback(pi + 1, pj - 1)
                if pj < j:
                    traceback(pj + 1, j)
        
        if n > 0:
            traceback(0, n - 1)
        
        dotbracket = ''.join(structure)
        
        rna = RNAStructure(
            sequence=sequence,
            dotbracket=dotbracket,
            name="Fallback_prediction"
        )
        
        return PredictionResult(
            structure=rna,
            method=self.name,
            metadata={'min_loop_size': min_loop_size}
        )


# Registry of available predictors
PREDICTORS: Dict[str, Predictor] = {
    'viennarna': ViennaRNAPredictor(),
    'linearfold': LinearFoldPredictor(),
    'contrafold': ContraFoldPredictor(),
    'fallback': FallbackPredictor(),
}


def list_predictors(available_only: bool = False) -> List[str]:
    """
    List available structure prediction methods.
    
    Args:
        available_only: Only list predictors that are installed/available
    
    Returns:
        List of predictor names
    
    Example:
        >>> list_predictors()
        ['viennarna', 'linearfold', 'contrafold', 'fallback']
        >>> list_predictors(available_only=True)
        ['viennarna', 'fallback']  # if only these are installed
    """
    if available_only:
        return [name for name, pred in PREDICTORS.items() if pred.is_available()]
    return list(PREDICTORS.keys())


def get_predictor(name: str) -> Predictor:
    """Get a predictor by name."""
    if name not in PREDICTORS:
        raise ValueError(
            f"Unknown predictor: {name}. "
            f"Available: {list(PREDICTORS.keys())}"
        )
    return PREDICTORS[name]


def predict_structure(
    sequence: str,
    method: str = "auto",
    constraints: Optional[str] = None,
    **kwargs
) -> RNAStructure:
    """
    Predict RNA secondary structure.
    
    This is the main entry point for structure prediction.
    Automatically selects the best available method if 'auto' is specified.
    
    Args:
        sequence: RNA sequence (A, C, G, U)
        method: Prediction method ('auto', 'viennarna', 'linearfold', etc.)
        constraints: Optional structure constraints in dot-bracket notation
        **kwargs: Method-specific parameters
    
    Returns:
        RNAStructure object with predicted structure
    
    Example:
        >>> rna = predict_structure("GCGCUUAAGCGC")
        >>> print(rna.to_dotbracket())
        '((((....))))'
        
        >>> rna = predict_structure("GCGC", method="viennarna", temperature=25)
    """
    # Auto-select method
    if method == "auto":
        # Preference order
        for name in ['viennarna', 'linearfold', 'contrafold', 'fallback']:
            if PREDICTORS[name].is_available():
                method = name
                break
    
    # Get predictor
    predictor = get_predictor(method)
    
    if not predictor.is_available():
        available = list_predictors(available_only=True)
        raise RuntimeError(
            f"Predictor '{method}' is not available. "
            f"Available predictors: {available}"
        )
    
    # Run prediction
    result = predictor.predict(sequence, constraints=constraints, **kwargs)
    
    return result.structure


def predict_multiple(
    sequences: List[str],
    method: str = "auto",
    **kwargs
) -> List[RNAStructure]:
    """
    Predict structures for multiple sequences.
    
    Args:
        sequences: List of RNA sequences
        method: Prediction method
        **kwargs: Method-specific parameters
    
    Returns:
        List of RNAStructure objects
    
    Example:
        >>> seqs = ["GCGCUUAAGCGC", "ACGUACGU"]
        >>> structures = predict_multiple(seqs)
    """
    return [predict_structure(seq, method=method, **kwargs) for seq in sequences]


def register_predictor(predictor: Predictor) -> None:
    """
    Register a custom predictor.
    
    Args:
        predictor: Predictor instance to register
    
    Example:
        >>> class MyPredictor(Predictor):
        ...     name = "mymethod"
        ...     def predict(self, seq, **kwargs):
        ...         ...
        >>> register_predictor(MyPredictor())
    """
    PREDICTORS[predictor.name] = predictor


def compare_predictions(
    sequence: str,
    methods: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, RNAStructure]:
    """
    Compare predictions from multiple methods.
    
    Args:
        sequence: RNA sequence
        methods: List of methods to compare (default: all available)
        **kwargs: Parameters passed to all predictors
    
    Returns:
        Dictionary mapping method name to predicted structure
    
    Example:
        >>> results = compare_predictions("GCGCUUAAGCGC")
        >>> for method, struct in results.items():
        ...     print(f"{method}: {struct.to_dotbracket()}")
    """
    if methods is None:
        methods = list_predictors(available_only=True)
    
    results = {}
    for method in methods:
        try:
            structure = predict_structure(sequence, method=method, **kwargs)
            results[method] = structure
        except Exception as e:
            print(f"Warning: {method} failed: {e}")
    
    return results
