import itertools
import logging

import httpx

from varanus import events
from varanus.utils import make_fingerprint

from ..models import Context
from .base import Integration

logger = logging.getLogger(__name__)


class SquishIntegration(Integration):
    def is_valid(self, context: events.Context) -> bool:
        return (
            (len(context.errors) > 0)
            and bool(self.settings.get("endpoint"))
            and bool(self.settings.get("api_key"))
            and bool(self.settings.get("user_key"))
        )

    def fingerprint(self, context: "Context") -> str | None:
        return make_fingerprint(
            itertools.chain.from_iterable(
                err.fingerprint_parts() for err in context.errors.all()
            )
        )

    def execute(self, context: Context):
        lines = []

        for err in context.errors.all():
            lines.append(f"### {err.kind} in {err.module}")
            lines.append(f"> {err.message}")
            lines.append("```")
            for line in err.stack:
                lines.append(
                    "{module}.{func} - {file}:{lineno}".format(
                        module=line["module"],
                        func=line["function"],
                        file=line["file"],
                        lineno=line["lineno"],
                    )
                )
                lines.append("    " + line["linesrc"])
            lines.append("```")

        for idx, log in enumerate(context.logs.all()):
            if idx == 0:
                lines.append("### Request Logs")
            lines.append(
                "* `{level} - {name}:{lineno}`: *{msg}*".format(
                    level=log.get_level_display(),  # type: ignore
                    name=log.name,
                    lineno=log.lineno,
                    msg=log.message,
                )
            )

        subject = f"{context.site.name} ({context.environment}) - {context.name}"
        return httpx.post(
            self.settings["endpoint"],
            json={
                "issue_type": self.settings.get("issue_type", "bug"),
                "subject": subject,
                "description": {"comment": "\n".join(lines), "format": "markdown"},
            },
            headers={
                "X-Squish-API-Key": self.settings["api_key"],
                "X-Squish-User-Key": self.settings["user_key"],
            },
        ).json()
