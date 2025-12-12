"""Exception code"""

# -- Classes ------------------------------------------------------------------


class IncorrectStateError(Exception):
    """Calling the specific coroutine is not allowed in the current state"""
