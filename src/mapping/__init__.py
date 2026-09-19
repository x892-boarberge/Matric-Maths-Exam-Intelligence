"""
src/mapping — Mapping v2 for NSC Mathematics.

This package implements the CAPS-aligned topic mapping used across
the MatricMath project.

Frozen artefacts live in src/mapping/frozen/ and are read on import
by each module.

Public API:
    from src.mapping.matcher import map_v2_final
    pred = map_v2_final(text, paper, sig_df, token_map, struct_rules)
"""