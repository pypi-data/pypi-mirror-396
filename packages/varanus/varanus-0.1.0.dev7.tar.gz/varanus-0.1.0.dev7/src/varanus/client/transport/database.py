import typing
from urllib.parse import SplitResult

import msgspec

from varanus import events

from .base import BaseTransport

if typing.TYPE_CHECKING:
    from varanus.server.models import Node, Site


class ModelTransport(BaseTransport):
    site: "Site"
    node: "Node"

    def __init__(self, url: SplitResult, environment: str, node: str):
        self.slug = url.netloc
        self.environment = environment
        self.node_name = node

    def ensure_site(self):
        if hasattr(self, "site"):
            return

        from varanus.server.models import Site

        self.site, created = Site.objects.get_or_create(
            slug=self.slug,
            defaults={
                "name": self.slug,
                "schema_name": self.slug,
            },
        )

    def ping(self, info: events.NodeInfo):
        from varanus.server.models import Node

        self.ensure_site()

        with self.site.activated():
            self.node, created, updates = Node.update(
                info, site=self.site, environment=self.environment
            )

    def send(self, event: events.Context):
        from varanus.server.tasks import ingest

        ingest.enqueue(
            self.site.pk,
            self.node_name,
            self.environment,
            msgspec.json.encode(event).decode(),
        )
