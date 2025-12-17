#!/usr/bin/env python3
"""
RNAview Quick Start Example
===========================

This script demonstrates the basic features of the RNAview package.
Run: python quick_start.py
"""

import rnaview as rv

print("=" * 60)
print("RNAview Quick Start Example")
print("=" * 60)

# 1. Create RNA Structure
print("\n1. Creating RNA Structure")
print("-" * 40)

rna = rv.RNAStructure(
    sequence="GCGCUUAAGCGC",
    dotbracket="((((....))))",
    name="Example_hairpin"
)

print(f"Name: {rna.name}")
print(f"Sequence: {rna.sequence}")
print(f"Structure: {rna.to_dotbracket()}")
print(f"Length: {rna.length} nt")
print(f"Base pairs: {rna.num_pairs}")

# 2. Analyze Structure
print("\n2. Analyzing Structure")
print("-" * 40)

helices = rna.get_helices()
loops = rna.get_loops()

print(f"Helices: {len(helices)}")
print(f"Loops: {len(loops)}")
print(f"Has pseudoknot: {rna.has_pseudoknot}")

# 3. Add Modifications
print("\n3. Adding Modifications")
print("-" * 40)

rna.add_modification(4, rv.Modification.m6A())
rna.add_modification(5, rv.Modification.pseudouridine())

for pos, mod in rna.modifications.items():
    print(f"Position {pos+1}: {mod.full_name}")

# 4. Structure Prediction
print("\n4. Structure Prediction")
print("-" * 40)

predicted = rv.predict_structure("GCGCUUAAGCGC", method="fallback")
print(f"Predicted: {predicted.to_dotbracket()}")

# 5. Compare Structures
print("\n5. Comparing Structures")
print("-" * 40)

f1 = rv.f1_score(rna, predicted)
sens = rv.sensitivity(rna, predicted)
ppv = rv.ppv(rna, predicted)

print(f"Sensitivity: {sens:.3f}")
print(f"PPV: {ppv:.3f}")
print(f"F1 Score: {f1:.3f}")

# 6. Export
print("\n6. Exporting Structure")
print("-" * 40)

ct = rv.to_ct(rna)
print(f"CT format: {len(ct.split(chr(10)))} lines")

print("\n" + "=" * 60)
print("Quick Start Complete!")
print("=" * 60)
