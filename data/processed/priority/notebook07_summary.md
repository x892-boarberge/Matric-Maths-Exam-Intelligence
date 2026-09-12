# Notebook 07 Summary

## Status
Complete (v1)

## Weights (locked)
{
  "exposure": 0.3,
  "difficulty": 0.4,
  "persistence": 0.2,
  "design_weight": 0.1
}

## Combined priority bands
                      topic  priority_score priority_band
               Trigonometry          0.6468        Medium
                   Calculus          0.5571        Medium
        Analytical Geometry          0.5361        Medium
         Functions & Graphs          0.5251        Medium
         Euclidean Geometry          0.5153        Medium
                    Finance          0.4615        Medium
                 Statistics          0.4124        Medium
Number Patterns & Sequences          0.3857         Lower
        Algebra & Equations          0.3732         Lower
                Probability          0.2933         Lower

## Paper 1 top cluster
                      topic  priority_score priority_band
                   Calculus          0.6000        Medium
         Functions & Graphs          0.5680        Medium
                    Finance          0.4615        Medium
Number Patterns & Sequences          0.4071        Medium
        Algebra & Equations          0.3946         Lower
                Probability          0.2933         Lower

## Paper 2 top cluster
              topic  priority_score priority_band
       Trigonometry          0.6468        Medium
Analytical Geometry          0.5314        Medium
 Euclidean Geometry          0.5106        Medium
         Statistics          0.3981         Lower

## Sensitivity
Min top-5 overlap under ±20% weight shift: 3/5
Interpretation: borderline stable → report clusters, not rigid ranks.

## Limitations
- Difficulty from documented DBE error commentary (not national mean %)
- Window: 2023–2025 only
- Persistence = within this window, not full 2014–2025 history
- Unmapped excluded from final deliverables

## Core insight
Trigonometry leads the priority cluster through high design weight + documented error pressure.
Calculus remains high mainly via exposure/design weight, with lower severe-language difficulty in the current extract.
Analytical Geometry, Functions & Graphs and Euclidean Geometry form a strong secondary cluster.
