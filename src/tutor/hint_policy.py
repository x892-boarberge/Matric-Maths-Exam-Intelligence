from .schemas import HintLevel, ErrorType

HINT_ESCALATION = {
    0: HintLevel.H0,
    1: HintLevel.H0,
    2: HintLevel.H1,
    3: HintLevel.H2,
    4: HintLevel.H3,
    5: HintLevel.H4,
}

_ORDER = [HintLevel.H0, HintLevel.H1, HintLevel.H2, HintLevel.H3, HintLevel.H4]


def select_hint_level(attempts_total: int, error_type: ErrorType,
                      explicit_request: bool = False) -> HintLevel:
    if explicit_request and attempts_total >= 2:
        return HintLevel.H4
    return HINT_ESCALATION.get(attempts_total, HintLevel.H4)


def is_escalation_allowed(current: HintLevel, target: HintLevel) -> bool:
    return _ORDER.index(target) <= _ORDER.index(current) + 1
