

## Stray 2021 guideline row — RESOLVED
- Row `grade12_mathematics_exam_guideline_2021` was a document-level leak
  of the 2021 exam guideline PDF into the exam mapping table.
- Dropped from combined file (261 -> 260 rows).
- Backup at: data/processed/mapped/dropped_rows_from_combined_v1.csv
- Root cause: guideline documents were segmented as if they were papers.
  This should not recur if N03 excludes non-exam document types.
- Action for notebook 14: verify loader rejects any row where
  document_type != 'exam' OR paper is NaN OR question_number is NaN.
