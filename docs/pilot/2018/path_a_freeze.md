# 2018 — Path A freeze

Stage: extraction + segmentation only.
Mapping: NOT DONE. Deferred to taxonomy v2.

Artefacts:
- data/interim/extracted_text/2018/
- data/interim/segmented/2018/exam_questions_2018.csv

Counts:
- P1: 57 rows, 135 marks (from OCR/text; may be partial)
- P2: 67 rows, 84 marks (from OCR/text; may be partial)
- OCR used: True

No topic, no sample verification, no vision, no question_force.
Do not run N05/N06/N07 on this year until taxonomy v2 mapping.
Frozen: 2026-09-18T10:38:55.050396+00:00


Segmentation v1.2 note: stems detected and labelled.
Rows with segmentation_status = 'stem' are shared context paragraphs, not questions.
Real question count excludes stems.
Stems preserved for N04 mapping (context will be prepended to children).
