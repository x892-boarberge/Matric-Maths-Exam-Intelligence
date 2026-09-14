def __init__(
    self,
    phrase_renderer: Optional[Callable[[Dict[str, Any]], str]] = None,
    session_logger: Optional[SessionLogger] = None,
):
    self.phrase_renderer = phrase_renderer or self._default_renderer
    self.logger = session_logger
    