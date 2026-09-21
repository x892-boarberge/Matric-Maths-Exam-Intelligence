"""
Meta-communication library.

What the tutor says when the learner's input is not an answer, but a
communication about their state: confusion, demand, frustration, silence.

Each function returns one variant from a small pool. The choice is
deterministic per learner: same learner -> same variant, different
learners -> different variants. The tutor stays one voice, but not
identical words for every learner.

Every line follows the persona:
- Do not give laws. Give understanding.
- Be graceful. Be distinct.
- Never shame, never rush.
"""
import hashlib
from typing import Optional


def pick(variants, learner_id=None, salt=""):
    """
    Deterministic variant selection.

    Same (learner_id, salt) -> same variant, forever.
    Different learner_id -> different variant with high probability.
    If learner_id is None, returns the first variant (safe default).
    """
    if not variants:
        return ""
    if learner_id is None:
        return variants[0]
    key = str(learner_id) + "|" + str(salt)
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    idx = int(h[:8], 16) % len(variants)
    return variants[idx]


# ---------- Understanding ----------

_NOT_UNDERSTANDING = [
    "That is okay. Let's make this smaller. Forget the whole question for a moment.",
    "Not a problem. Let's shrink it. What is the first thing the question asks you to find?",
    "Let's slow down together. I will ask one small question. No wrong answer here.",
    "That happens to everyone. Let's step back. What do you see in front of you?",
    "Okay. Let's take it one piece at a time. Read me the very first line of the question.",
    "No rush. Let's find one thing that makes sense to you first. What is it?",
    "Right. Let's start from the top. What is the question asking for, in your own words?",
    "Fine. Forget solving for now. Just tell me what the question gives you.",
    "Let's go small. Read the question to me slowly. What is the first number or letter you see?",
]


def say_not_understanding(learner_id: Optional[str] = None, context=None) -> str:
    return pick(_NOT_UNDERSTANDING, learner_id, "not_understanding")


_NOT_UNDERSTANDING_AFTER_STRUGGLE = [
    "Let's go one step smaller. I will not ask you to solve anything yet. What numbers or symbols do you see?",
    "That is alright. Let's stop trying to solve. Just read the question to me, out loud, one line at a time.",
    "Okay. Different approach. Forget the solution. What is the question telling you it wants?",
    "Let's reset. No solving for now. Which word in the question looks the most important to you?",
]


def say_not_understanding_after_struggle(learner_id: Optional[str] = None, context=None) -> str:
    return pick(_NOT_UNDERSTANDING_AFTER_STRUGGLE, learner_id, "not_understanding_struggle")


# ---------- Answer demand ----------

_ANSWER_DEMAND = [
    "I will not give you the full answer yet, because you are closer than you think. One step is off. Let's find it together. What is your first line of working?",
    "Not yet. You are one move away. Look at your last line. What did you write just before it?",
    "I know it feels slow, but you are almost there. Tell me what you tried first.",
    "I am not going to hand it over. But I will help you find it. Where does your working stop?",
    "I hear you. I will not give the answer, but I can help you find it. What is your last step?",
    "Not this time. What is your first move on this question?",
    "I hear that. Before any answer, one question: what is the operation the question asks for?",
    "Nope. You are the one solving this. But I am right here. What did you try so far?",
]


def say_answer_demand(learner_id: Optional[str] = None, context=None) -> str:
    return pick(_ANSWER_DEMAND, learner_id, "answer_demand")


_ANSWER_DEMAND_REPEAT = [
    "I hear you. I will not solve it for you, but I will give you the first step. Your first step is to isolate the variable. What do you write next?",
    "Okay, one step. Not the answer. Start by writing the equation in a form you recognise. What does that look like?",
    "Alright. First move only. Which operation do you undo first?",
]


def say_answer_demand_repeat(learner_id: Optional[str] = None, context=None) -> str:
    return pick(_ANSWER_DEMAND_REPEAT, learner_id, "answer_demand_repeat")


# ---------- Frustration ----------

_FRUSTRATED = [
    "That feeling is real, and it does not mean you cannot do this. It means the step is too big right now. Let's shrink it. What do you see in front of you?",
    "Take a breath. That reaction usually means we moved too fast. Let's slow down. What is one thing in the question you do understand?",
    "That is okay. Frustration is a signal, not a verdict. Let's find a smaller piece. What is the very first thing the question asks?",
    "I hear you. Let's change the size of the step. Instead of solving, just read me the question slowly.",
    "That is a lot to hold at once. Let's put most of it down. What is one line in the question we could look at?",
    "Yes, this is hard. That is not a verdict on you. What is the smallest piece you can say out loud?",
    "Okay. We are going to slow down more than usual. Read the first sentence. Then stop. Just the first.",
    "I understand. Let's not try to solve anything for a moment. Tell me what you already know.",
]


def say_frustrated(learner_id: Optional[str] = None, context=None) -> str:
    return pick(_FRUSTRATED, learner_id, "frustrated")


_FRUSTRATED_REPEAT = [
    "Let's stop the problem for a second. Take a breath. When you are ready, tell me one thing you do understand about the question. Anything at all.",
    "Okay. We are going to put the problem down for a moment. Not abandon it. Just pause. What is one thing you notice in the question?",
    "Let's step away from solving. Write down the numbers or letters you see. That is all.",
]


def say_frustrated_repeat(learner_id: Optional[str] = None, context=None) -> str:
    return pick(_FRUSTRATED_REPEAT, learner_id, "frustrated_repeat")


# ---------- Silence / empty ----------

_SILENCE = [
    "Take your time. When you are ready, write what you have so far. Even if it is only the first line.",
    "No rush. Type anything you have, even the parts you are unsure about.",
    "Whenever you are ready. What does your working look like so far?",
]


def say_silence(learner_id: Optional[str] = None, context=None) -> str:
    return pick(_SILENCE, learner_id, "silence")


# ---------- Close but not correct ----------

_CLOSE_BUT_NOT_QUITE = [
    "You are almost there. One small thing is off. Look at your last line again. Does it match what the question asked for?",
    "Very close. There is a small slip somewhere. Walk me through your last step.",
    "Nearly right. One detail needs fixing. Which line do you think is the problem?",
    "Close. Before we move on, look at your final line carefully. What did the question ask for, and what did you write?",
    "So near. One thing is off by a little. What does your last line say?",
    "Almost. Something small slipped. Which line are you least sure about?",
    "Right track. One detail is wrong. Read your last two lines out loud to yourself. What do you notice?",
    "Nearly. Take one more look. Does the last line answer the question, or something slightly different?",
]


def say_close_but_not_quite(learner_id: Optional[str] = None, context=None) -> str:
    return pick(_CLOSE_BUT_NOT_QUITE, learner_id, "close_not_quite")


# ---------- Success ----------

_CORRECT_AFTER_STRUGGLE_LONG = [
    "Good - you found it yourself after a few tries. That is how this works, and the struggle is the learning. Let's keep going.",
    "Yes. That is the one. And it came from you, not from me. Keep that feeling.",
    "Good work. You pushed through a few wrong turns and landed on it. That is exactly what the exam will ask of you.",
]

_CORRECT_AFTER_STRUGGLE_SHORT = [
    "Good. That step is correct. Let's keep going.",
    "Right. Let's move to the next step.",
    "Good - onwards.",
]


def say_correct_after_struggle(learner_id: Optional[str] = None, attempts=None, context=None) -> str:
    if attempts and attempts >= 3:
        return pick(_CORRECT_AFTER_STRUGGLE_LONG, learner_id, "correct_struggle_long")
    return pick(_CORRECT_AFTER_STRUGGLE_SHORT, learner_id, "correct_struggle_short")


# ---------- Off-topic input ----------

_OFF_TOPIC = [
    "I am not sure that connects to this question. Let's come back to the problem. What is the first step?",
    "That is outside what we are working on right now. Let's return to the question. Where does your working stop?",
    "Let's stay with the problem. What is the first move?",
]


def say_off_topic(learner_id: Optional[str] = None, context=None) -> str:
    return pick(_OFF_TOPIC, learner_id, "off_topic")


# ---------- Specific praise ----------

_PRAISE_SPECIFIC = [
    "Good. Your {what} is correct. Let's keep going.",
    "Right. Your {what} holds up. Onwards.",
    "Nice. The {what} is right. What comes next?",
]


def say_praise_specific(what_was_correct, learner_id: Optional[str] = None) -> str:
    if not what_was_correct:
        return say_correct_after_struggle(learner_id=learner_id)
    template = pick(_PRAISE_SPECIFIC, learner_id, "praise_specific")
    return template.format(what=what_was_correct)
