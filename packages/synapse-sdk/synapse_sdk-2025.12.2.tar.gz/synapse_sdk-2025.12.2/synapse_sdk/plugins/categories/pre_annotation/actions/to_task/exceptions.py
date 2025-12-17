class CriticalError(Exception):
    """Critical error."""

    def __init__(self, message: str = 'Critical error occured while processing task'):
        self.message = message
        super().__init__(self.message)


class PreAnnotationToTaskFailed(Exception):
    """Pre-annotation to task failed."""

    def __init__(self, message: str = 'Pre-annotation to task failed'):
        self.message = message
        super().__init__(self.message)
