"""Send two learner messages to the LLM with tools. Show what it does."""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tutor.llm_caller import converse_turn
from src.tutor.llm_conversation_prompt import (
    CONVERSATION_PROMPT, build_first_user_message
)

problem_prompt = "Solve for x: (x+5)(x-2)=0"
problem_skill = "algebra.quadratic.solve"
expected = "x = -5 or x = 2"

history = [
    {"role": "user", "content": build_first_user_message(
        problem_prompt, problem_skill, expected)},
    {"role": "user", "content": "My answer: x = 5 or x = 2"},
]

print("=== Turn 1 ===")
r1 = converse_turn(history, CONVERSATION_PROMPT, learner_id="L001")
print("Error:", r1.get("error"))
print("Tool calls:")
for c in r1["tool_calls_made"]:
    print("  ", c["name"], "->", str(c["result"])[:120])
print("Tutor says:")
print(r1["assistant_text"])
print()

# Turn 2 - same wrong answer
history2 = list(r1["raw_messages"])
history2.append({"role": "user", "content": "My answer: x = 5 or x = 2"})

print("=== Turn 2 (same wrong answer) ===")
r2 = converse_turn(history2, CONVERSATION_PROMPT, learner_id="L001")
print("Error:", r2.get("error"))
print("Tool calls:")
for c in r2["tool_calls_made"]:
    print("  ", c["name"], "->", str(c["result"])[:120])
print("Tutor says:")
print(r2["assistant_text"])
