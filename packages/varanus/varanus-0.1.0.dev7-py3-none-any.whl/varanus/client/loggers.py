import logging
import sys

from ..events import Log, Query, capture_stack, now
from .context import ONE_MS, current_context


class VaranusHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        if ctx := current_context.get():
            ctx.logs.append(Log.from_logrecord(record, tags=ctx.tags))


class QueryLogger:
    def __init__(self, threshold, log_params, log_stack, metrics):
        # TODO: add callback for tagging?
        if threshold is True:
            self.threshold = 0
        elif threshold is False:
            self.threshold = sys.maxsize
        else:
            self.threshold = int(threshold)
        self.log_params = log_params
        self.log_stack = log_stack
        if isinstance(metrics, str):
            self.metrics_name = metrics
        else:
            self.metrics_name = "queries" if metrics else None

    def __call__(self, execute, sql, params, many, context):
        start = now()
        success = True
        try:
            result = execute(sql, params, many, context)
        except Exception:
            success = False
            raise
        else:
            return result
        finally:
            if ctx := current_context.get():
                elapsed_ms = (now() - start) // ONE_MS
                if self.metrics_name:
                    ctx.metric(self.metrics_name, elapsed_ms)
                if elapsed_ms >= self.threshold:
                    ctx.queries.append(
                        Query(
                            timestamp=start,
                            sql=sql,
                            params=(
                                [repr(p) for p in params]
                                if params and self.log_params
                                else []
                            ),
                            db=context["connection"].alias,
                            elapsed_ms=elapsed_ms,
                            success=success,
                            stack=capture_stack(1) if self.log_stack else [],
                        )
                    )
