"""Expand the variant pools for the four most-used meta functions."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "src" / "tutor" / "meta_library.py"
src = META.read_text(encoding="utf-8")

# ---------- not_understanding (5 -> 9) ----------
old = '''_NOT_UNDERSTANDING = [
    "That is okay. Let's make this smaller. Forget the whole question for a moment.",
    "Not a problem. Let's shrink it. What is the first thing the question asks you to find?",
    "Let's slow down together. I will ask one small question. No wrong answer here.",
    "That happens to everyone. Let's step back. What do you see in front of you?",
    "Okay. Let's take it one piece at a time. Read me the very first line of the question.",
]'''

new = '''_NOT_UNDERSTANDING = [
    "That is okay. Let's make this smaller. Forget the whole question for a moment.",
    "Not a problem. Let's shrink it. What is the first thing the question asks you to find?",
    "Let's slow down together. I will ask one small question. No wrong answer here.",
    "That happens to everyone. Let's step back. What do you see in front of you?",
    "Okay. Let's take it one piece at a time. Read me the very first line of the question.",
    "No rush. Let's find one thing that makes sense to you first. What is it?",
    "Right. Let's start from the top. What is the question asking for, in your own words?",
    "Fine. Forget solving for now. Just tell me what the question gives you.",
    "Let's go small. Read the question to me slowly. What is the first number or letter you see?",
]'''

if old in src:
    src = src.replace(old, new, 1)
    print("Expanded not_understanding to 9")
else:
    print("WARNING - not_understanding pool not found")

# ---------- frustrated (4 -> 8) ----------
old_f = '''_FRUSTRATED = [
    "That feeling is real, and it does not mean you cannot do this. It means the step is too big right now. Let's shrink it. What do you see in front of you?",
    "Take a breath. That reaction usually means we moved too fast. Let's slow down. What is one thing in the question you do understand?",
    "That is okay. Frustration is a signal, not a verdict. Let's find a smaller piece. What is the very first thing the question asks?",
    "I hear you. Let's change the size of the step. Instead of solving, just read me the question slowly.",
]'''

new_f = '''_FRUSTRATED = [
    "That feeling is real, and it does not mean you cannot do this. It means the step is too big right now. Let's shrink it. What do you see in front of you?",
    "Take a breath. That reaction usually means we moved too fast. Let's slow down. What is one thing in the question you do understand?",
    "That is okay. Frustration is a signal, not a verdict. Let's find a smaller piece. What is the very first thing the question asks?",
    "I hear you. Let's change the size of the step. Instead of solving, just read me the question slowly.",
    "That is a lot to hold at once. Let's put most of it down. What is one line in the question we could look at?",
    "Yes, this is hard. That is not a verdict on you. What is the smallest piece you can say out loud?",
    "Okay. We are going to slow down more than usual. Read the first sentence. Then stop. Just the first.",
    "I understand. Let's not try to solve anything for a moment. Tell me what you already know.",
]'''

if old_f in src:
    src = src.replace(old_f, new_f, 1)
    print("Expanded frustrated to 8")
else:
    print("WARNING - frustrated pool not found")

# ---------- answer_demand (4 -> 8) ----------
old_a = '''_ANSWER_DEMAND = [
    "I will not give you the full answer yet, because you are closer than you think. One step is off. Let's find it together. What is your first line of working?",
    "Not yet. You are one move away. Look at your last line. What did you write just before it?",
    "I know it feels slow, but you are almost there. Tell me what you tried first.",
    "I am not going to hand it over. But I will help you find it. Where does your working stop?",
]'''

new_a = '''_ANSWER_DEMAND = [
    "I will not give you the full answer yet, because you are closer than you think. One step is off. Let's find it together. What is your first line of working?",
    "Not yet. You are one move away. Look at your last line. What did you write just before it?",
    "I know it feels slow, but you are almost there. Tell me what you tried first.",
    "I am not going to hand it over. But I will help you find it. Where does your working stop?",
    "No. But here is what I will do: I will help you see where you went wrong. Show me your last step.",
    "Not this time. What is your first move on this question?",
    "I hear that. Before any answer, one question: what is the operation the question asks for?",
    "Nope. You are the one solving this. But I am right here. What did you try so far?",
]'''

if old_a in src:
    src = src.replace(old_a, new_a, 1)
    print("Expanded answer_demand to 8")
else:
    print("WARNING - answer_demand pool not found")

# ---------- close_but_not_quite (4 -> 8) ----------
old_c = '''_CLOSE_BUT_NOT_QUITE = [
    "You are almost there. One small thing is off. Look at your last line again. Does it match what the question asked for?",
    "Very close. There is a small slip somewhere. Walk me through your last step.",
    "Nearly right. One detail needs fixing. Which line do you think is the problem?",
    "Close. Before we move on, look at your final line carefully. What did the question ask for, and what did you write?",
]'''

new_c = '''_CLOSE_BUT_NOT_QUITE = [
    "You are almost there. One small thing is off. Look at your last line again. Does it match what the question asked for?",
    "Very close. There is a small slip somewhere. Walk me through your last step.",
    "Nearly right. One detail needs fixing. Which line do you think is the problem?",
    "Close. Before we move on, look at your final line carefully. What did the question ask for, and what did you write?",
    "So near. One thing is off by a little. Check your arithmetic in the last line.",
    "Almost. Something small slipped. Which line are you least sure about?",
    "Right track. One detail is wrong. Read your last two lines out loud to yourself. What do you notice?",
    "Nearly. Take one more look. Does the last line answer the question, or something slightly different?",
]'''

if old_c in src:
    src = src.replace(old_c, new_c, 1)
    print("Expanded close_but_not_quite to 8")
else:
    print("WARNING - close_but_not_quite pool not found")

META.write_text(src, encoding="utf-8")
print("meta_library.py updated")
