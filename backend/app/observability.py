import json
import logging
import time
import uuid

from datetime import (
    datetime,
    timezone,
)

from fastapi import Request

from prometheus_client import (
    Counter,
    Histogram,
)

from app.config import settings


HTTP_REQUESTS = Counter(
    "modelcontrol_http_requests_total",
    "Total number of HTTP requests",
    [
        "method",
        "path",
        "status",
    ],
)


HTTP_REQUEST_DURATION = Histogram(
    "modelcontrol_http_request_duration_seconds",
    "HTTP request latency in seconds",
    [
        "method",
        "path",
    ],
)


class JsonFormatter(
    logging.Formatter
):
    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        payload = {
            "timestamp": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            "level": record.levelname,
            "logger": record.name,
            "message": (
                record.getMessage()
            ),
        }

        for field in (
            "request_id",
            "method",
            "path",
            "status_code",
            "duration_ms",
        ):
            value = getattr(
                record,
                field,
                None,
            )

            if value is not None:
                payload[field] = value

        if record.exc_info:
            payload["exception"] = (
                self.formatException(
                    record.exc_info
                )
            )

        return json.dumps(
            payload
        )


def configure_logging() -> logging.Logger:
    logger = logging.getLogger(
        "modelcontrol"
    )

    level_name = (
        settings.log_level.upper()
    )

    level = getattr(
        logging,
        level_name,
        logging.INFO,
    )

    logger.setLevel(level)

    logger.handlers.clear()

    handler = (
        logging.StreamHandler()
    )

    handler.setFormatter(
        JsonFormatter()
    )

    logger.addHandler(handler)

    logger.propagate = False

    return logger


logger = configure_logging()


async def observability_middleware(
    request: Request,
    call_next,
):
    start = time.perf_counter()

    incoming_request_id = (
        request.headers.get(
            "X-Request-ID"
        )
    )

    if (
        incoming_request_id
        and len(incoming_request_id)
        <= 128
    ):
        request_id = (
            incoming_request_id
        )
    else:
        request_id = str(
            uuid.uuid4()
        )

    request.state.request_id = (
        request_id
    )

    status_code = 500

    try:
        response = await call_next(
            request
        )

        status_code = (
            response.status_code
        )

        response.headers[
            "X-Request-ID"
        ] = request_id

        return response

    except Exception:
        logger.exception(
            "Unhandled request exception",
            extra={
                "request_id":
                    request_id,
                "method":
                    request.method,
                "path":
                    request.url.path,
                "status_code":
                    500,
            },
        )

        raise

    finally:
        duration = (
            time.perf_counter()
            - start
        )

        route = (
            request.scope.get(
                "route"
            )
        )

        route_path = getattr(
            route,
            "path",
            request.url.path,
        )

        HTTP_REQUESTS.labels(
            method=request.method,
            path=route_path,
            status=str(
                status_code
            ),
        ).inc()

        HTTP_REQUEST_DURATION.labels(
            method=request.method,
            path=route_path,
        ).observe(
            duration
        )

        logger.info(
            "HTTP request completed",
            extra={
                "request_id":
                    request_id,
                "method":
                    request.method,
                "path":
                    route_path,
                "status_code":
                    status_code,
                "duration_ms":
                    round(
                        duration * 1000,
                        2,
                    ),
            },
        )