# system modules
from contextlib import contextmanager

# internal modules

# external modules


class Mode:
    """
    Class to hold a mode with different states.
    """

    def __init__(self, states, default):
        self.states = set(states)
        self.default = default
        self.state = self.default

    @property
    def state(self):
        """
        The current state. Can only be set to a state defined in the
        initializer. Raises a ``ValueError`` otherwise.
        """
        try:
            return self._state
        except AttributeError:
            self._state = self.default

    @state.setter
    def state(self, newstate):
        if newstate not in self.states:
            raise ValueError(
                f"No such state {repr(newstate)}. Use one of {self.states}"
            )
        self._state = newstate

    @contextmanager
    def __call__(self, state):
        """
        Context manager to temporarily set the mode
        """
        state_before = self.state
        self.state = state
        try:
            yield
        finally:
            self.state = state_before

    def __eq__(self, state):
        return self.state == state

    def __repr__(self):
        return f"Mode(states={repr(self.states)},default={repr(self.default)})"
