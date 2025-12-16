from urllib.parse import SplitResult

from varanus import events


class BaseTransport:
    def __init__(self, url: SplitResult, environment: str, node: str):
        pass

    def ping(self, info: events.NodeInfo):
        pass

    def send(self, event: events.Context):
        pass
