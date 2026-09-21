"""
Meta-communication library.

What the tutor says when the learner's input is not an answer, but a
communication about their state: confusion, demand, frustration, silence.

This is not the hint library. The hint library answers "what to say about
the maths". This answers "what to say about the moment".

Every line follows the persona:
- Do not give laws. Give understanding.
- Be graceful. Be distinct.
- Never shame, never rush.
"""


def say_not_understanding(context=None):
    """
    Learner said they do not understand.
    context: optional dict with keys skill_id, subtopic, last_response.
    """
    lines = [
        "That is okay. Let's make this smaller. Forget the whole question for a moment.",
        "What is the very first thing the question asks you to find?",
    ]
    return " ".join(lines)


def say_not_understanding_after_struggle(context=None):
    """Second 'I do not understand' in a row. Reduce complexity."""
    lines = [
        "Let's go one step smaller. I will not ask you to solve anything yet.",
        "Look at the question. What are the numbers or symbols you see?",
        "Just read them out to me.",
    ]
    return " ".join(lines)


def say_answer_demand(context=None):
    """Learner asked for the answer directly."""
    return (
        "I will not give you the full answer yet, because you are closer than you think. "
        "One step is off. Let's find it together. "
        "What is your first line of working?"
    )


def say_answer_demand_repeat(context=None):
    """Learner asked for the answer a second time."""
    return (
        "I hear you. Here is what I can do: I will not solve it for you, "
        "but I will give you the first step. "
        "Your first step is to isolate the variable. What do you write next?"
    )


def say_frustrated(context=None):
    """Learner expressed frustration — 'this is too hard', 'I am stupid'."""
    return (
        "That feeling is real, and it does not mean you cannot do this. "
        "It means the step is too big right now. Let's shrink it. "
        "I will ask one small question. There is no wrong answer. "
        "What do you see in front of you?"
    )


def say_frustrated_repeat(context=None):
    """Second frustration signal. Reduce further."""
    return (
        "Let's stop the problem for a second. "
        "Take a breath. When you are ready, tell me one thing you do understand "
        "about the question. Anything at all."
    )


def say_silence(context=None):
    """Learner gave empty input or long pause."""
    return (
        "Take your time. When you are ready, write what you have so far — "
        "even if it is only the first line."
    )


def say_close_but_not_quite(context=None):
    """Answer is close to correct but has a small error."""
    return (
        "You are almost there. One small thing is off. "
        "Look at your last line again. Does it match what the question asked for?"
    )


def say_correct_after_struggle(attempts=None):
    """Correct response after two or more failed attempts."""
    if attempts and attempts >= 3:
        return (
            "There it is. And you found it yourself after a few tries. "
            "That is how this works. The struggle is the learning. "
            "Let's keep going."
        )
    return (
        "Good — that step is correct. Let's keep going."
    )


def say_off_topic(context=None):
    """Learner wrote something unrelated to the maths."""
    return (
        "I am not sure that connects to this question. "
        "Let's come back to the problem. What is the first step?"
    )


def say_praise_specific(what_was_correct):
    """Praise a specific correct step, not the person."""
    if not what_was_correct:
        return "Good — that step is correct. Let's keep going."
    return "Good — your " + str(what_was_correct) + " is correct. Let's keep going."
