"""
Engine tools exposed to the LLM driver (Path C).
"""
from typing import Optional


TOOL_VERSION = "0.2.0"


def tool_diagnose(skill_id: str, response: str, expected: str) -> dict:
    from .diagnosis import diagnose
    d = diagnose(skill_id, response, expected)
    return {
        "error_type": d.error_type.value,
        "misconception_id": d.misconception_id,
        "confidence": d.confidence,
        "rule_id": d.rule_id,
        "explanation": d.explanation,
    }


def tool_hint_level(attempts: int, error_type: str,
                    explicit_request: bool = False) -> dict:
    from .hint_policy import select_hint_level
    from .schemas import ErrorType
    try:
        et = ErrorType(error_type)
    except ValueError:
        et = ErrorType.UNKNOWN
    lvl = select_hint_level(attempts, et, explicit_request)
    return {"hint_level": lvl.value if lvl else None}


def tool_intervention(misconception_id: str) -> dict:
    if not misconception_id:
        return {"intervention_pattern": "IP_GENERIC_PROMPT",
                "n08_intervention_id": None,
                "provenance": "generic_fallback"}
    from .schemas import DiagnosisResult, ErrorType
    from .intervention_selector import select_intervention
    d = DiagnosisResult(
        error_type=ErrorType.UNKNOWN,
        misconception_id=misconception_id,
        confidence=1.0,
        rule_id="LLM_REQUEST",
        explanation="",
    )
    sel = select_intervention(d)
    return {
        "intervention_pattern": sel.intervention_pattern,
        "n08_intervention_id": sel.n08_intervention_id,
        "provenance": sel.provenance.value,
        "notes": sel.notes,
    }


def tool_misconception_context(misconception_id: str) -> dict:
    if not misconception_id:
        return {"misconception_id": None, "label": None,
                "hints": {}, "presentation_rules": []}
    from .misconception_hints import HINTS
    hints = HINTS.get(misconception_id, {})
    return {
        "misconception_id": misconception_id,
        "label": misconception_id,
        "hints": hints,
        "presentation_rules": [],
    }


def tool_presentation_rules(misconception_id: str) -> dict:
    return {"rules": [], "status": "not_implemented"}


def tool_record_attempt(learner_id: str, skill_id: str,
                        response: str, diagnosis: dict) -> dict:
    return {"recorded": False, "status": "not_implemented"}


def tool_learner_state(learner_id: str) -> dict:
    return {"status": "not_implemented"}


def list_tools():
    return [
        "tool_diagnose",
        "tool_hint_level",
        "tool_intervention",
        "tool_misconception_context",
        "tool_presentation_rules",
        "tool_record_attempt",
        "tool_learner_state",
    ]


def call_tool(name, args):
    """Dispatch a tool call from the LLM."""
    fn = globals().get(name)
    if not callable(fn) or name not in list_tools():
        return {"error": "unknown tool: " + str(name)}
    try:
        return fn(**args)
    except TypeError as e:
        return {"error": "bad arguments: " + str(e)}
    except Exception as e:
        return {"error": "tool failed: " + str(e)}

def tool_schema():
    """Return the tool definitions in Ollama/OpenAI-compatible schema."""
    return [
        {"type": "function", "function": {
            "name": "tool_diagnose",
            "description": "Diagnose a learner response against the expected answer.",
            "parameters": {"type": "object", "properties": {
                "skill_id": {"type": "string"},
                "response": {"type": "string"},
                "expected": {"type": "string"}},
                "required": ["skill_id", "response", "expected"]}}},
        {"type": "function", "function": {
            "name": "tool_hint_level",
            "description": "Choose the hint level for this attempt.",
            "parameters": {"type": "object", "properties": {
                "attempts": {"type": "integer"},
                "error_type": {"type": "string"},
                "explicit_request": {"type": "boolean"}},
                "required": ["attempts", "error_type"]}}},
        {"type": "function", "function": {
            "name": "tool_intervention",
            "description": "Get the intervention pattern for a misconception.",
            "parameters": {"type": "object", "properties": {
                "misconception_id": {"type": "string"}},
                "required": ["misconception_id"]}}},
        {"type": "function", "function": {
            "name": "tool_misconception_context",
            "description": "Get label, hints and rules for a misconception.",
            "parameters": {"type": "object", "properties": {
                "misconception_id": {"type": "string"}},
                "required": ["misconception_id"]}}},
        {"type": "function", "function": {
            "name": "tool_presentation_rules",
            "description": "Layout or notation advice for a misconception.",
            "parameters": {"type": "object", "properties": {
                "misconception_id": {"type": "string"}},
                "required": ["misconception_id"]}}},
        {"type": "function", "function": {
            "name": "tool_record_attempt",
            "description": "Record this attempt against the learner.",
            "parameters": {"type": "object", "properties": {
                "learner_id": {"type": "string"},
                "skill_id": {"type": "string"},
                "response": {"type": "string"},
                "diagnosis": {"type": "object"}},
                "required": ["learner_id", "skill_id", "response", "diagnosis"]}}},
        {"type": "function", "function": {
            "name": "tool_learner_state",
            "description": "Get the learner current state: mastery, errors, hints.",
            "parameters": {"type": "object", "properties": {
                "learner_id": {"type": "string"}},
                "required": ["learner_id"]}}},
    ]
