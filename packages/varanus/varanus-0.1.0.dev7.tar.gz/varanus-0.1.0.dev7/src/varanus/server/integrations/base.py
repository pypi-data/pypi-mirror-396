from typing import TYPE_CHECKING, Any

from varanus import events

if TYPE_CHECKING:
    from ..models import Context


class IntegrationError(Exception):
    pass


class DuplicateIntegration(IntegrationError):
    pass


class Integration:
    def __init__(self, settings: dict[str, Any]):
        self.settings = settings

    def is_valid(self, context: events.Context) -> bool:
        """
        Returns whether the integration should be scheduled to run for the given
        Context event (not the Context model).
        """
        return True

    def fingerprint(self, context: "Context") -> str | None:
        """
        Given a Context model, returns a fingerprint for debouncing integration calls.
        """
        return None

    def execute(self, context: "Context") -> Any:
        """
        Runs the integration for the given Context model.
        """
        raise NotImplementedError()
