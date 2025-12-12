class RagaException(Exception):
    """Base class for all raga exceptions."""
    def __init__(self, msg, *args):
        assert msg
        self.msg = f"{msg}"
        super().__init__(msg, *args)
