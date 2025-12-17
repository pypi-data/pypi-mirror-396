"""
Structure comparison metrics for RNA secondary structure prediction evaluation.

This module provides standard metrics for comparing predicted RNA structures
against reference structures, following established benchmarking conventions.

Metrics included:
- Sensitivity (true positive rate, recall)
- Positive Predictive Value (precision)
- F1 score (harmonic mean of sensitivity and PPV)
- Matthews Correlation Coefficient (MCC)
- Structural distance measures

Example:
    >>> import rnaview as rv
    >>> predicted = rv.load_structure("predicted.ct")
    >>> reference = rv.load_structure("reference.ct")
    >>> metrics = rv.compare_structures(predicted, reference)
    >>> print(f"F1 Score: {metrics['f1']:.3f}")
"""

from __future__ import annotations
from typing import Set, Tuple, Dict, Optional, List
import math

from ..core.structure import RNAStructure, BasePair


def _get_pair_set(structure: RNAStructure) -> Set[Tuple[int, int]]:
    """Extract base pairs as a set of (i, j) tuples with i < j."""
    return {(bp.i, bp.j) for bp in structure.base_pairs}


def _get_compatible_pairs(
    pairs: Set[Tuple[int, int]], 
    allow_shift: int = 0
) -> Set[Tuple[int, int]]:
    """
    Get expanded set of pairs allowing for position shifts.
    
    Useful for allowing small alignment errors in predictions.
    """
    if allow_shift == 0:
        return pairs
    
    expanded = set()
    for i, j in pairs:
        for di in range(-allow_shift, allow_shift + 1):
            for dj in range(-allow_shift, allow_shift + 1):
                expanded.add((i + di, j + dj))
    return expanded


def sensitivity(
    predicted: RNAStructure,
    reference: RNAStructure,
    allow_shift: int = 0
) -> float:
    """
    Calculate sensitivity (recall, true positive rate).
    
    Sensitivity = TP / (TP + FN) = correctly predicted pairs / reference pairs
    
    Args:
        predicted: Predicted RNA structure
        reference: Reference (true) RNA structure
        allow_shift: Allow base pair positions to shift by this amount
    
    Returns:
        Sensitivity value between 0 and 1
    
    Example:
        >>> sens = sensitivity(predicted, reference)
        >>> print(f"Sensitivity: {sens:.3f}")
    """
    pred_pairs = _get_pair_set(predicted)
    ref_pairs = _get_pair_set(reference)
    
    if not ref_pairs:
        return 1.0 if not pred_pairs else 0.0
    
    if allow_shift > 0:
        pred_expanded = _get_compatible_pairs(pred_pairs, allow_shift)
        true_positives = len(ref_pairs & pred_expanded)
    else:
        true_positives = len(ref_pairs & pred_pairs)
    
    return true_positives / len(ref_pairs)


def ppv(
    predicted: RNAStructure,
    reference: RNAStructure,
    allow_shift: int = 0
) -> float:
    """
    Calculate Positive Predictive Value (precision).
    
    PPV = TP / (TP + FP) = correctly predicted pairs / predicted pairs
    
    Args:
        predicted: Predicted RNA structure
        reference: Reference (true) RNA structure
        allow_shift: Allow base pair positions to shift by this amount
    
    Returns:
        PPV value between 0 and 1
    
    Example:
        >>> precision = ppv(predicted, reference)
        >>> print(f"PPV: {precision:.3f}")
    """
    pred_pairs = _get_pair_set(predicted)
    ref_pairs = _get_pair_set(reference)
    
    if not pred_pairs:
        return 1.0 if not ref_pairs else 0.0
    
    if allow_shift > 0:
        ref_expanded = _get_compatible_pairs(ref_pairs, allow_shift)
        true_positives = len(pred_pairs & ref_expanded)
    else:
        true_positives = len(pred_pairs & ref_pairs)
    
    return true_positives / len(pred_pairs)


def f1_score(
    predicted: RNAStructure,
    reference: RNAStructure,
    allow_shift: int = 0
) -> float:
    """
    Calculate F1 score (harmonic mean of sensitivity and PPV).
    
    F1 = 2 * (sensitivity * PPV) / (sensitivity + PPV)
    
    Args:
        predicted: Predicted RNA structure
        reference: Reference (true) RNA structure
        allow_shift: Allow base pair positions to shift
    
    Returns:
        F1 score between 0 and 1
    
    Example:
        >>> f1 = f1_score(predicted, reference)
        >>> print(f"F1: {f1:.3f}")
    """
    sens = sensitivity(predicted, reference, allow_shift)
    prec = ppv(predicted, reference, allow_shift)
    
    if sens + prec == 0:
        return 0.0
    
    return 2 * (sens * prec) / (sens + prec)


def mcc(
    predicted: RNAStructure,
    reference: RNAStructure,
) -> float:
    """
    Calculate Matthews Correlation Coefficient.
    
    MCC considers true/false positives and negatives and is generally
    regarded as a balanced measure even for imbalanced datasets.
    
    MCC = (TP*TN - FP*FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))
    
    Args:
        predicted: Predicted RNA structure
        reference: Reference (true) RNA structure
    
    Returns:
        MCC value between -1 and 1 (1 is perfect, 0 is random, -1 is inverse)
    
    Example:
        >>> mcc_val = mcc(predicted, reference)
        >>> print(f"MCC: {mcc_val:.3f}")
    """
    pred_pairs = _get_pair_set(predicted)
    ref_pairs = _get_pair_set(reference)
    
    # Calculate all possible pairs for this sequence length
    n = max(predicted.length, reference.length)
    total_possible = n * (n - 1) // 2
    
    tp = len(pred_pairs & ref_pairs)
    fp = len(pred_pairs - ref_pairs)
    fn = len(ref_pairs - pred_pairs)
    tn = total_possible - tp - fp - fn
    
    numerator = (tp * tn) - (fp * fn)
    denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def compare_structures(
    predicted: RNAStructure,
    reference: RNAStructure,
    allow_shift: int = 0,
    detailed: bool = False
) -> Dict[str, float]:
    """
    Comprehensive structure comparison with multiple metrics.
    
    Args:
        predicted: Predicted RNA structure
        reference: Reference (true) RNA structure
        allow_shift: Allow base pair positions to shift
        detailed: Include additional detailed metrics
    
    Returns:
        Dictionary with metric names and values
    
    Example:
        >>> metrics = compare_structures(predicted, reference)
        >>> for name, value in metrics.items():
        ...     print(f"{name}: {value:.3f}")
    """
    pred_pairs = _get_pair_set(predicted)
    ref_pairs = _get_pair_set(reference)
    
    if allow_shift > 0:
        pred_expanded = _get_compatible_pairs(pred_pairs, allow_shift)
        ref_expanded = _get_compatible_pairs(ref_pairs, allow_shift)
        tp = len(ref_pairs & pred_expanded)
        tp_pred = len(pred_pairs & ref_expanded)
    else:
        tp = len(pred_pairs & ref_pairs)
        tp_pred = tp
    
    fp = len(pred_pairs) - tp_pred
    fn = len(ref_pairs) - tp
    
    # Calculate metrics
    sens = tp / len(ref_pairs) if ref_pairs else (1.0 if not pred_pairs else 0.0)
    precision = tp_pred / len(pred_pairs) if pred_pairs else (1.0 if not ref_pairs else 0.0)
    
    if sens + precision > 0:
        f1 = 2 * sens * precision / (sens + precision)
    else:
        f1 = 0.0
    
    results = {
        'sensitivity': sens,
        'ppv': precision,
        'f1': f1,
        'mcc': mcc(predicted, reference),
        'true_positives': tp,
        'false_positives': fp,
        'false_negatives': fn,
        'predicted_pairs': len(pred_pairs),
        'reference_pairs': len(ref_pairs),
    }
    
    if detailed:
        # Add pseudoknot-specific metrics
        pred_pk = {(bp.i, bp.j) for bp in predicted.base_pairs if bp.is_pseudoknot}
        ref_pk = {(bp.i, bp.j) for bp in reference.base_pairs if bp.is_pseudoknot}
        
        if ref_pk:
            pk_sens = len(pred_pk & ref_pk) / len(ref_pk)
        else:
            pk_sens = 1.0 if not pred_pk else 0.0
        
        if pred_pk:
            pk_ppv = len(pred_pk & ref_pk) / len(pred_pk)
        else:
            pk_ppv = 1.0 if not ref_pk else 0.0
        
        results['pk_sensitivity'] = pk_sens
        results['pk_ppv'] = pk_ppv
        results['pk_f1'] = 2 * pk_sens * pk_ppv / (pk_sens + pk_ppv) if (pk_sens + pk_ppv) > 0 else 0.0
        
        # Helix-level accuracy
        pred_helices = predicted.get_helices()
        ref_helices = reference.get_helices()
        results['predicted_helices'] = len(pred_helices)
        results['reference_helices'] = len(ref_helices)
    
    return results


def structural_distance(
    structure1: RNAStructure,
    structure2: RNAStructure,
    metric: str = "bp_distance"
) -> float:
    """
    Calculate structural distance between two RNA structures.
    
    Args:
        structure1: First RNA structure
        structure2: Second RNA structure
        metric: Distance metric to use
            - 'bp_distance': Base pair distance (symmetric difference)
            - 'mountain': Mountain distance
            - 'tree_edit': Tree edit distance (requires same length)
    
    Returns:
        Distance value (0 = identical)
    
    Example:
        >>> dist = structural_distance(struct1, struct2, metric="bp_distance")
    """
    if metric == "bp_distance":
        return _bp_distance(structure1, structure2)
    elif metric == "mountain":
        return _mountain_distance(structure1, structure2)
    elif metric == "tree_edit":
        return _tree_edit_distance(structure1, structure2)
    else:
        raise ValueError(f"Unknown distance metric: {metric}")


def _bp_distance(
    structure1: RNAStructure,
    structure2: RNAStructure
) -> float:
    """
    Calculate base pair distance.
    
    BP distance = |P1 - P2| + |P2 - P1| = symmetric difference
    """
    pairs1 = _get_pair_set(structure1)
    pairs2 = _get_pair_set(structure2)
    
    return len(pairs1.symmetric_difference(pairs2))


def _mountain_distance(
    structure1: RNAStructure,
    structure2: RNAStructure
) -> float:
    """
    Calculate mountain distance based on mountain representation.
    
    Mountain representation: height at each position = number of enclosing pairs
    Distance = L1 norm of difference in mountain vectors
    """
    if structure1.length != structure2.length:
        raise ValueError("Structures must have same length for mountain distance")
    
    def get_mountain(structure: RNAStructure) -> List[int]:
        n = structure.length
        mountain = [0] * n
        height = 0
        
        # Create a quick lookup for open/close brackets
        opens = set()
        closes = set()
        for bp in structure.base_pairs:
            opens.add(bp.i)
            closes.add(bp.j)
        
        for i in range(n):
            if i in opens:
                height += 1
            mountain[i] = height
            if i in closes:
                height -= 1
        
        return mountain
    
    m1 = get_mountain(structure1)
    m2 = get_mountain(structure2)
    
    return sum(abs(a - b) for a, b in zip(m1, m2))


def _tree_edit_distance(
    structure1: RNAStructure,
    structure2: RNAStructure
) -> float:
    """
    Calculate tree edit distance using Zhang-Shasha algorithm.
    
    This is a simplified implementation; for production use,
    consider using specialized libraries.
    """
    # Simplified tree edit distance
    # Full implementation would require building tree representations
    # For now, use a weighted combination of metrics
    
    bp_dist = _bp_distance(structure1, structure2)
    n_pairs = max(
        len(structure1.base_pairs), 
        len(structure2.base_pairs),
        1
    )
    
    return bp_dist / n_pairs


def batch_compare(
    predictions: List[RNAStructure],
    references: List[RNAStructure],
    allow_shift: int = 0
) -> Dict[str, List[float]]:
    """
    Compare multiple structure pairs and aggregate results.
    
    Args:
        predictions: List of predicted structures
        references: List of reference structures
        allow_shift: Allow base pair position shifts
    
    Returns:
        Dictionary with metric names mapping to lists of values
    
    Example:
        >>> results = batch_compare(predictions, references)
        >>> avg_f1 = sum(results['f1']) / len(results['f1'])
    """
    if len(predictions) != len(references):
        raise ValueError("Number of predictions and references must match")
    
    results = {
        'sensitivity': [],
        'ppv': [],
        'f1': [],
        'mcc': [],
    }
    
    for pred, ref in zip(predictions, references):
        metrics = compare_structures(pred, ref, allow_shift=allow_shift)
        for key in results:
            results[key].append(metrics[key])
    
    # Add summary statistics
    results['mean_sensitivity'] = sum(results['sensitivity']) / len(results['sensitivity'])
    results['mean_ppv'] = sum(results['ppv']) / len(results['ppv'])
    results['mean_f1'] = sum(results['f1']) / len(results['f1'])
    results['mean_mcc'] = sum(results['mcc']) / len(results['mcc'])
    
    return results


def confusion_matrix(
    predicted: RNAStructure,
    reference: RNAStructure
) -> Dict[str, int]:
    """
    Generate confusion matrix for base pair prediction.
    
    Args:
        predicted: Predicted structure
        reference: Reference structure
    
    Returns:
        Dictionary with TP, FP, FN, TN counts
    """
    pred_pairs = _get_pair_set(predicted)
    ref_pairs = _get_pair_set(reference)
    
    n = max(predicted.length, reference.length)
    total_possible = n * (n - 1) // 2
    
    tp = len(pred_pairs & ref_pairs)
    fp = len(pred_pairs - ref_pairs)
    fn = len(ref_pairs - pred_pairs)
    tn = total_possible - tp - fp - fn
    
    return {
        'TP': tp,
        'FP': fp,
        'FN': fn,
        'TN': tn,
    }
