import json, shutil
from pathlib import Path
from datetime import datetime

path = Path("data/processed/tutor/playbooks/2025_P1_Q11.json")
ts = datetime.now().strftime("%Y%m%d%H%M%S")
shutil.copy(path, path.with_suffix(f".json.bak_{ts}"))

data = json.loads(path.read_text(encoding="utf-8-sig"))
existing = set(data["subquestions"].keys())

q11_1_1 = {
    "variant_question": "In a survey of 200 learners, the events 'male' and 'preferring tea' are independent. The table shows: Male-Tea = 30, Male-Coffee = 70, Male total = 100; Female-Tea = 30, Female-Coffee = k, Female total = 100; Total Tea = 60, Total Coffee = 140. Show that k = 70.",
    "demonstration": "Independence means P(male and tea) = P(male)·P(tea).\nP(male) = 100/200 = 1/2.\nP(tea) = 60/200 = 3/10.\nP(male and tea) = 30/200 = 3/20.\nCheck: (1/2)·(3/10) = 3/20 ✓.\nFor the Female-Coffee cell: total = 200, so 30+70+30+k = 200 → k = 70.",
    "memo_marks": [
        "1 mark for P(male and tea) = P(male)·P(tea) statement",
        "1 mark for computing 30/200 = (100/200)·(60/200)",
        "1 mark for k = 70"
    ],
    "fast_path": "Independence: multiply the two marginals, compare to the joint cell. Then the missing cell comes from the total.",
    "fatal_error": "DBE says: Candidates confuse independent with mutually exclusive. Independent means P(A and B) = P(A)·P(B). Mutually exclusive means P(A and B) = 0. Very different.",
    "answer_book_layout": [
        "P(male and tea) = 30/200",
        "P(male)·P(tea) = (100/200)·(60/200) = 3/20",
        "Since 30/200 = 3/20, the events are independent",
        "Total = 30 + 70 + 30 + k = 200 → k = 70"
    ],
    "hack": "Independent = multiply. Find P(A)·P(B). If it equals P(A and B), the events are independent. Then use row/column totals to fill any missing cell.",
    "trap": "Mutually exclusive vs independent. Mutually exclusive = can't both happen (P=0). Independent = one happening doesn't change the probability of the other. Don't mix them up.",
    "presentation": "State the independence rule explicitly. Show the multiplication. The marker needs to see P(A)·P(B) before any arithmetic."
}

q11_1_2 = {
    "variant_question": "From the contingency table (200 learners: Male-Tea = 30, Male-Coffee = 70, Female-Tea = 30, Female-Coffee = 70), calculate the probability that a female learner, chosen at random, will prefer coffee.",
    "demonstration": "Look at only the female row (since we're conditioning on female).\nFemale total = 100. Female-Coffee = 70.\nP(coffee | female) = 70/100 = 7/10 = 0.7 = 70%.",
    "memo_marks": [
        "1 mark for identifying the female total (100)",
        "1 mark for 70/100",
        "1 mark for simplified answer 7/10 or 0.7"
    ],
    "fast_path": "'Given female' means look ONLY at the female row. Numerator = female-coffee cell. Denominator = female row total.",
    "fatal_error": "DBE says: Candidates use the grand total (200) as the denominator instead of the conditional group's total (100). The phrase 'chosen at random from the group of females' means females are the sample space.",
    "answer_book_layout": [
        "Condition on females: denominator = 100",
        "Female and coffee = 70",
        "P = 70/100 = 7/10 = 0.7"
    ],
    "hack": "'Given [group]' means the denominator is the group's total, not the grand total. Read what group the question fixes, then use that row or column.",
    "trap": "If the question says 'a female chosen at random', the denominator is females, not everyone. If it says 'a random learner AND she is female', the denominator is 200.",
    "presentation": "State the conditional group's total first. Then the specific cell. Then the ratio."
}

added = []
if "11.1.1" not in existing:
    data["subquestions"]["11.1.1"] = q11_1_1
    added.append("11.1.1")
if "11.1.2" not in existing:
    data["subquestions"]["11.1.2"] = q11_1_2
    added.append("11.1.2")

path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Added: {added}")
print(f"Q11 now has: {sorted(data['subquestions'].keys())}")
print(f"Total subqs: {len(data['subquestions'])}")
