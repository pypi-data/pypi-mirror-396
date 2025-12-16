import logging
import queue
import threading
import time
from typing import Any
from urllib.parse import SplitResult, parse_qs

import httpx
import msgspec

from varanus import events

from .base import BaseTransport

logger = logging.getLogger(__name__)


class HttpTransport(BaseTransport):
    def __init__(self, url: SplitResult, environment: str, node: str):
        path = url.path.rstrip("/")
        self.ping_url = f"{url.scheme}://{url.netloc}{path}/api/ping/"
        self.event_url = f"{url.scheme}://{url.netloc}{path}/api/ingest/"
        self.options = parse_qs(url.query, keep_blank_values=True)
        timeout = 1.0
        if "timeout" in self.options:
            timeout = float(self.options["timeout"][0])
        self.client = httpx.Client(
            headers={
                "X-Varanus-Key": url.username or "",
                "X-Varanus-Environment": environment,
                "X-Varanus-Node": node,
            },
            timeout=timeout,
        )

    def request(self, url: str, obj: Any):
        try:
            self.client.post(url, content=msgspec.json.encode(obj))
        except Exception:
            logger.exception("error sending to %s", url)

    def ping(self, info: events.NodeInfo):
        self.request(self.ping_url, info)

    def send(self, event: events.Context):
        self.request(self.event_url, [event])


def sender(pending: queue.SimpleQueue, client: httpx.Client, url: str, rate: float):
    while True:
        start = time.time()
        events = []
        while True:
            try:
                events.append(pending.get_nowait())
            except queue.Empty:
                break
            if len(events) >= 100:
                break
        if events:
            try:
                client.post(url, content=msgspec.json.encode(events))
            except Exception:
                logger.exception("error sending to %s", url)
        elapsed = time.time() - start
        time.sleep(max(rate - elapsed, 1.0))


class ThreadedHttpTransport(HttpTransport):
    def __init__(self, url: SplitResult, environment: str, node: str):
        super().__init__(url, environment, node)
        self.pending = queue.SimpleQueue()
        rate = 3.0
        if "rate" in self.options:
            rate = float(self.options["rate"][0])
        threading.Thread(
            target=sender,
            args=(self.pending, self.client, self.event_url, rate),
            daemon=True,
        ).start()

    def send(self, event: events.Context):
        self.pending.put(event)
