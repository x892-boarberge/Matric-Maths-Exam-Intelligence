# 01 – Problem Framing

## System Name
**MatricMath Intelligence**  
NSC Mathematics Examination Intelligence, Learner-Error Mining and Intervention System

---

## 1. Purpose
Construct a structured, evidence-based intelligence system for South African NSC Mathematics using official examination papers, marking guidelines, diagnostic reports and curriculum documents.

The system must support:
- curriculum and assessment analysis;
- identification of persistent learner errors and misconceptions;
- estimation of high-priority preparation areas; and
- targeted instructional intervention.

The AI tutoring layer is a downstream application of the intelligence system, not the primary product.

---

## 2. Core Analytical Question
Which mathematical concepts, question structures and learner misconceptions have consistently contributed to weak performance in NSC Mathematics, and how can official historical evidence be used to prioritise targeted preparation and intervention?

---

## 3. Supporting Questions
1. Which topics are assessed most frequently?
2. Which topics carry the highest mark weight?
3. Which question structures recur across examination cycles?
4. Which learner errors are repeatedly documented in official sources?
5. Which misconceptions are most damaging in mark terms?
6. Which misconceptions persist across multiple years?
7. How do patterns differ across curriculum and assessment regimes?
8. Which topics and error types should receive highest preparation priority?
9. Can learner responses be matched to known misconception patterns?
10. Can matched patterns drive personalised intervention sequences?

---

## 4. Explicit Non-Objectives
The system will not:
- predict exact future examination questions;
- claim that any specific question will appear;
- treat topic frequency alone as proof of learner weakness;
- treat all years as one homogeneous assessment regime;
- present generic chatbot tutoring as the core product; or
- claim guaranteed performance improvement without validation evidence.

Forecast outputs must be expressed as assessment priorities or risk levels, with supporting evidence.

---

## 5. Evidence Rules

### 5.1 Examination evidence
Examination papers may support claims about:
- topic presence;
- topic frequency;
- mark allocation;
- question structure;
- command verbs;
- topic combinations; and
- changes over time.

Examination papers alone may **not** support claims that learners commonly failed a topic.

### 5.2 Learner-performance evidence
Claims about common errors or misconceptions must be supported by:
- DBE diagnostic reports;
- examiner/moderator commentary;
- marking-guideline notes where explicitly diagnostic; or
- other valid performance evidence.

### 5.3 Combined evidence
Highest-priority findings require both:
- assessment presence/weight, and
- documented learner-performance difficulty.

---

## 6. Curriculum-Regime Control (Grade 12 / Matric)

CAPS implementation timeline:
- **2011:** CAPS approved/published as national policy
- **2012:** CAPS implementation starts (Grade 10)
- **2013:** Grade 11 moves to CAPS
- **2014:** Grade 12 / matric first fully assessed under CAPS

### Regime labels used in this system

| Years | Regime label | Analytical use |
|-------|--------------|----------------|
| Before 2012 | `pre-CAPS` | Historical context only |
| 2012–2013 | `CAPS-transition` | Separate / transitional analysis |
| **2014 onward** | `CAPS-Grade12` | Primary CAPS-era Matric analysis |

### Analytical rule
- Primary pattern analysis and CAPS claims: **2014–2025 (`CAPS-Grade12`) only**
- Transition years may be inventoried and analysed separately
- Pre-CAPS material is optional historical context
- Never claim a “persistent CAPS misconception” using only pre-2014 evidence

---

## 7. Source Hierarchy

### Tier 1
- DBE examination papers
- DBE marking guidelines
- DBE diagnostic reports
- DBE CAPS documents
- DBE examination guidelines
- Umalusi reports

### Tier 2
- Provincial official repositories
- Other official education repositories

### Tier 3
- Trusted educational archives for backfill only

Tier 1 is mandatory where available.

---

## 8. Build Order
1. Source inventory  
2. Verified document collection  
3. Extraction / OCR  
4. Question segmentation  
5. Question structuring  
6. CAPS mapping  
7. Error and misconception mining  
8. Misconception ranking  
9. Historical pattern analysis  
10. Assessment-priority estimation  
11. Learner diagnostic engine  
12. Targeted practice engine  
13. AI tutor interface  

The tutor is downstream of the intelligence layers.

---

## 9. Phase 1 Operating Rule
**Inventory first. No bulk PDF collection before the control register is audited.**

Control table:

`data/metadata/exam_document_register.csv`

This register is the single source of truth for collection status.

---

## 10. Initial Inventory Scope
- Practical start window: **2014–2025** for CAPS-Grade12 analysis
- Inventory may include additional sessions and supporting documents
- Missing documents must be marked `missing`, not silently dropped

### Priority logic
- 2023–2025: high
- 2018–2022: medium
- 2014–2017: medium-low / medium
- Pre-2014: low (later expansion)

---

## 11. Success Criteria for Phase 1
- Complete candidate inventory for target years and sessions
- Transparent collection-status field (`queued` / `downloaded` / `verified` / `missing`)
- Correct curriculum-regime tags (`pre-CAPS` / `CAPS-transition` / `CAPS-Grade12`)
- Priority tags for collection order
- No silent exclusion of missing documents