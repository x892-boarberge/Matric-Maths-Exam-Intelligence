# src/tutor/slash_commands.py
"""
Slash-command notation expander for the CLI drill.

A learner typing working on a physical keyboard cannot easily type
unicode maths symbols. Instead they type slash commands that expand
to the notation the NSC memo uses.

    /sqrt      ->  sqrt(
    /theta     ->  theta
    /therefore ->  therefore
    /or        ->  " or "
    /deg       ->  deg

Expansion happens at submission time, before grading. The engine
stores ASCII-safe tokens internally so the math_grader and
step_grader stay stable.

Design rules:
  * Only expands /name followed by a non-word char or end-of-string.
  * Unknown /foo is left alone (learner can still write /paths).
  * /help, /?, /commands prints the full list.
"""
from __future__ import annotations
import re


SLASH_COMMANDS = {
    "sqrt":    "sqrt",
    "cbrt":    "cbrt",
    "pi":      "pi",
    "pm":      "+/-",
    "le":      "<=",
    "ge":      ">=",
    "ne":      "!=",
    "in":      "in",
    "R":       "R",
    "sum":     "sum",
    "inf":     "inf",
    "or":      " or ",
    "then":    " therefore ",
    "because": " because ",
    "implies": " => ",
    "iff":     " <=> ",
    "deg":     "deg",
    "cdot":    " x ",
    "times":   " x ",
    "div":     " / ",
    "theta":   "theta",
    "alpha":   "alpha",
    "beta":    "beta",
    "gamma":   "gamma",
    "sin":     "sin",
    "cos":     "cos",
    "tan":     "tan",
    "asin":    "asin",
    "acos":    "acos",
    "atan":    "atan",
    "dy":      "dy/dx",
    "dx":      "d/dx",
    "d2y":     "d2y/dx2",
    "lim":     "lim",
    "to":      "->",
    "angle":   "angle",
    "tri":     "triangle",
    "para":    "parallel",
    "perp":    "perp",
    "cong":    "cong",
    "sim":     "similar",
    "arc":     "arc ",
    "chord":   "chord ",
    "tchord":  "tan chord",
    "atcentre":"angle at centre",
    "xbar":    "xbar",
    "sigma":   "sigma",
    "sigma2":  "sigma^2",
}


HELP_TEXT = (
    "\nMethodKeyboard - slash commands\n"
    "\n  Algebra"
    "\n    /sqrt     sqrt(         /cbrt     cbrt("
    "\n    /pi       pi            /pm       +/-"
    "\n    /le       <=            /ge       >="
    "\n    /ne       !=            /in       in"
    "\n    /R        R             /sum      sum"
    "\n    /inf      inf           /deg      deg"
    "\n    /or       or            /then     therefore"
    "\n    /because  because       /implies  =>"
    "\n    /iff      <=>           /cdot     x"
    "\n"
    "\n  Trig"
    "\n    /theta    theta         /alpha    alpha"
    "\n    /beta     beta          /gamma    gamma"
    "\n    /sin      sin(          /cos      cos("
    "\n    /tan      tan(          /asin     asin("
    "\n    /acos     acos(         /atan     atan("
    "\n"
    "\n  Calculus"
    "\n    /dy       dy/dx         /dx       d/dx"
    "\n    /d2y      d2y/dx2       /lim      lim"
    "\n    /to       ->"
    "\n"
    "\n  Geometry"
    "\n    /angle    angle         /tri      triangle"
    "\n    /para     parallel      /perp     perp"
    "\n    /cong     cong          /sim      similar"
    "\n    /arc      arc           /chord    chord"
    "\n    /tchord   tan chord     /atcentre angle at centre"
    "\n"
    "\n  Stats"
    "\n    /xbar     xbar          /sigma    sigma"
    "\n    /sigma2   sigma^2"
    "\n"
    "\nType /help for this list."
    "\n"
)


_CMD_PATTERN = re.compile(r"/([A-Za-z][A-Za-z0-9_]*)(?![A-Za-z0-9_])")


def expand(text: str) -> str:
    """Expand every /command in text. Unknown commands are left alone."""
    if not text or "/" not in text:
        return text

    def _replace(match):
        name = match.group(1)
        return SLASH_COMMANDS.get(name, match.group(0))

    return _CMD_PATTERN.sub(_replace, text)


def expand_lines(lines):
    """Expand a list of learner lines. Returns a new list."""
    return [expand(line) for line in lines]


def is_help(text: str) -> bool:
    """Is this submission just a help request?"""
    return text.strip() in ("/help", "/?", "/commands")


__all__ = [
    "SLASH_COMMANDS", "HELP_TEXT",
    "expand", "expand_lines", "is_help",
]
