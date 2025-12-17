"""
RNAview Unit Tests
==================

Run with: pytest tests/
"""

import pytest
import sys
import os

# Ensure package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestImports:
    """Test that all modules import correctly."""
    
    def test_main_import(self):
        import rnaview
        assert hasattr(rnaview, '__version__')
        assert rnaview.__version__ == "1.0.0"
    
    def test_core_imports(self):
        from rnaview.core import RNAStructure, RNASequence, Modification
        assert RNAStructure is not None
        assert RNASequence is not None
        assert Modification is not None
    
    def test_io_imports(self):
        from rnaview.io import load_structure, to_ct, to_bpseq
        assert callable(load_structure)
        assert callable(to_ct)
        assert callable(to_bpseq)
    
    def test_analysis_imports(self):
        from rnaview.analysis import sensitivity, ppv, f1_score, mcc
        assert callable(sensitivity)
        assert callable(ppv)
        assert callable(f1_score)
        assert callable(mcc)


class TestRNAStructure:
    """Tests for RNAStructure class."""
    
    def test_create_simple_structure(self):
        from rnaview import RNAStructure
        
        rna = RNAStructure(
            sequence="GCGCUUAAGCGC",
            dotbracket="((((....))))",
            name="test"
        )
        
        assert rna.length == 12
        assert rna.sequence == "GCGCUUAAGCGC"
        assert rna.num_pairs == 4
        assert rna.name == "test"
    
    def test_base_pairs(self):
        from rnaview import RNAStructure
        
        rna = RNAStructure(
            sequence="GCGCUUAAGCGC",
            dotbracket="((((....))))"
        )
        
        pairs = rna.base_pairs
        assert len(pairs) == 4
        assert pairs[0].i == 0
        assert pairs[0].j == 11
    
    def test_to_dotbracket(self):
        from rnaview import RNAStructure
        
        original = "((((....))))"
        rna = RNAStructure(
            sequence="GCGCUUAAGCGC",
            dotbracket=original
        )
        
        assert rna.to_dotbracket() == original
    
    def test_pseudoknot_detection(self):
        from rnaview import RNAStructure
        
        # Structure without pseudoknot
        rna1 = RNAStructure(
            sequence="GCGCUUAAGCGC",
            dotbracket="((((....))))"
        )
        assert rna1.has_pseudoknot is False
        
        # Structure with pseudoknot
        rna2 = RNAStructure(
            sequence="GGAAGCUGACCAGACAGUCGCCGCUUCGGUCAAUCC",
            dotbracket="..(((((....[[[..))))).......]]]....."
        )
        assert rna2.has_pseudoknot is True


class TestRNASequence:
    """Tests for RNASequence class."""
    
    def test_create_sequence(self):
        from rnaview import RNASequence
        
        seq = RNASequence("AUGCUAGCUA", name="test")
        
        assert seq.length == 10
        assert str(seq) == "AUGCUAGCUA"
    
    def test_gc_content(self):
        from rnaview import RNASequence
        
        seq = RNASequence("GCGCAUAU")
        assert seq.gc_content == 0.5
    
    def test_complement(self):
        from rnaview import RNASequence
        
        seq = RNASequence("AUGC")
        assert seq.complement() == "UACG"


class TestModifications:
    """Tests for RNA modifications."""
    
    def test_create_m6a(self):
        from rnaview import Modification, ModificationType
        
        mod = Modification.m6A()
        
        assert mod.mod_type == ModificationType.M6A
        assert mod.symbol == "m6A"
        assert mod.parent_base == "A"
    
    def test_add_modification_to_structure(self):
        from rnaview import RNAStructure, Modification
        
        rna = RNAStructure(
            sequence="GCGCUUAAGCGC",
            dotbracket="((((....))))"
        )
        
        rna.add_modification(4, Modification.m6A())
        
        assert len(rna.modifications) == 1
        assert rna.get_modification(4) is not None


class TestMetrics:
    """Tests for analysis metrics."""
    
    def test_perfect_prediction(self):
        from rnaview import RNAStructure, sensitivity, ppv, f1_score, mcc
        
        ref = RNAStructure(
            sequence="GCGCUUAAGCGC",
            dotbracket="((((....))))"
        )
        pred = RNAStructure(
            sequence="GCGCUUAAGCGC",
            dotbracket="((((....))))"
        )
        
        assert sensitivity(ref, pred) == 1.0
        assert ppv(ref, pred) == 1.0
        assert f1_score(ref, pred) == 1.0
        assert mcc(ref, pred) == 1.0
    
    def test_imperfect_prediction(self):
        from rnaview import RNAStructure, f1_score
        
        ref = RNAStructure(
            sequence="GCGCUUAAGCGC",
            dotbracket="((((....))))"
        )
        pred = RNAStructure(
            sequence="GCGCUUAAGCGC",
            dotbracket="((((.....)))"
        )
        
        f1 = f1_score(ref, pred)
        assert 0 < f1 < 1


class TestIO:
    """Tests for I/O functions."""
    
    def test_to_ct(self):
        from rnaview import RNAStructure, to_ct
        
        rna = RNAStructure(
            sequence="GCGC",
            dotbracket="(())",
            name="test"
        )
        
        ct = to_ct(rna)
        lines = ct.split('\n')
        
        assert lines[0].startswith("4")
    
    def test_to_bpseq(self):
        from rnaview import RNAStructure, to_bpseq
        
        rna = RNAStructure(
            sequence="GCGC",
            dotbracket="(())",
            name="test"
        )
        
        bpseq = to_bpseq(rna)
        lines = bpseq.split('\n')
        
        assert len(lines) == 4


class TestPrediction:
    """Tests for structure prediction."""
    
    def test_list_predictors(self):
        from rnaview import list_predictors
        
        predictors = list_predictors()
        assert "fallback" in predictors
    
    def test_predict_with_fallback(self):
        from rnaview import predict_structure
        
        rna = predict_structure("GCGCUUAAGCGC", method="fallback")
        
        assert rna.length == 12
        assert rna.sequence == "GCGCUUAAGCGC"


class TestUtils:
    """Tests for utility functions."""
    
    def test_validate_sequence(self):
        from rnaview.utils import validate_sequence
        
        assert validate_sequence("ACGU") is True
        
        with pytest.raises(ValueError):
            validate_sequence("ACGX", allow_iupac=False)
    
    def test_dotbracket_to_pairs(self):
        from rnaview.utils import dotbracket_to_pairs
        
        pairs = dotbracket_to_pairs("((((....))))")
        
        assert len(pairs) == 4
        assert (0, 11) in pairs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
