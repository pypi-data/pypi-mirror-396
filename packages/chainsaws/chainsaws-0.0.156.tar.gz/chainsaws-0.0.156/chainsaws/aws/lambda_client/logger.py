import functools
import logging
import orjson
import random
import resource
import sys
import time
import traceback
from typing import Any, Callable, Optional, Literal, TypedDict, Annotated, Dict

from chainsaws.aws.lambda_client.types import Context as LambdaContext

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

LambdaHandler = Callable[[Dict[str, Any], LambdaContext], Any]


class LogExtra(TypedDict, total=False):
    """Type for extra fields in log records."""
    cold_start: bool
    cold_start_duration_ms: int
    correlation_id: str
    function_name: str
    function_version: str
    function_arn: str
    memory_limit: int
    memory_used_mb: float
    memory_usage_percent: float
    aws_request_id: str
    log_group: str
    log_stream: str
    event: dict
    event_size_bytes: int
    response: Any
    response_size_bytes: int
    duration_ms: int
    remaining_time_ms: int
    timeout_warning: bool
    retry_attempt: int
    error: str


JsonPath = str  # Type alias for JSON path strings like "headers.x-correlation-id"
SampleRate = Annotated[float, "Value between 0.0 and 1.0"]


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(
        self,
        service: str,
        **kwargs: Any,
    ) -> None:
        """Initialize formatter.

        Args:
            service: Service name
            **kwargs: Additional fields to include in logs
        """
        super().__init__()
        self.service = service
        self.additional_fields = kwargs

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record

        Returns:
            JSON formatted log string
        """
        # Base log fields
        log_dict = {
            "level": record.levelname,
            "message": record.getMessage(),
            "service": self.service,
            "timestamp": int(record.created * 1000),  # milliseconds
            "logger": record.name,
        }

        # Add location info
        if record.pathname and record.lineno:
            log_dict["location"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add exception info if present
        if record.exc_info:
            log_dict["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "stacktrace": traceback.format_exception(*record.exc_info),
            }

        # Add additional fields
        log_dict.update(self.additional_fields)

        # Add extra fields from record
        if hasattr(record, "extra"):
            log_dict.update(record.extra)

        return orjson.dumps(log_dict).decode('utf-8')


class Logger:
    """Lambda logger with structured logging and context injection."""

    # Keep track of cold starts
    _cold_start = True
    _cold_start_time: Optional[float] = None

    def __init__(
        self,
        service: str,
        level: LogLevel = "INFO",
        sample_rate: SampleRate = 1.0,
        **kwargs: Any,
    ) -> None:
        """Initialize logger.

        Args:
            service: Service name
            level: Log level (one of "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
            sample_rate: Sampling rate for debug logs (0.0 to 1.0)
            **kwargs: Additional fields to include in logs

        Raises:
            ValueError: If sample_rate is not between 0.0 and 1.0
        """
        if not 0.0 <= sample_rate <= 1.0:
            raise ValueError("sample_rate must be between 0.0 and 1.0")

        self.service = service
        self.sample_rate = sample_rate
        self.logger = logging.getLogger(service)

        # Set log level
        self.logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers
        self.logger.handlers.clear()

        # Add JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter(service, **kwargs))
        self.logger.addHandler(handler)
        
        # Track cold start time at initialization
        if Logger._cold_start_time is None:
            Logger._cold_start_time = time.time()

    def inject_lambda_context(
        self,
        correlation_id_path: Optional[JsonPath] = None,
        log_event: bool = True,
        log_response: bool = True,
        max_event_size_bytes: int = 10000,
        max_response_size_bytes: int = 10000,
        timeout_warning_threshold_ms: int = 1000,
    ) -> Callable[[LambdaHandler], LambdaHandler]:
        """Inject Lambda context into logs with enhanced metrics.

        Args:
            correlation_id_path: JSON path to correlation ID in event (e.g. "headers.x-correlation-id")
            log_event: Whether to log event payload (default: True)
            log_response: Whether to log response payload (default: True)
            max_event_size_bytes: Maximum event size to log fully (default: 10000)
            max_response_size_bytes: Maximum response size to log fully (default: 10000)
            timeout_warning_threshold_ms: Warn if remaining time is below this threshold (default: 1000ms)

        Example:
            ```python
            logger = Logger(service="my-service")

            @logger.inject_lambda_context(
                correlation_id_path="headers.x-correlation-id",
                max_event_size_bytes=5000,
            )
            def handler(event, context):
                logger.info("Processing event")
                return {"statusCode": 200}
            ```
        """
        def decorator(handler: LambdaHandler) -> LambdaHandler:
            @functools.wraps(handler)
            def wrapper(event: dict, context: LambdaContext) -> Any:
                invocation_start = time.time()
                
                # Measure cold start duration
                cold_start_duration_ms = None
                if Logger._cold_start:
                    if Logger._cold_start_time is not None:
                        cold_start_duration_ms = int((invocation_start - Logger._cold_start_time) * 1000)
                    Logger._cold_start = False
                    Logger._cold_start_time = None

                # Add Lambda context
                extra: LogExtra = {
                    "function_name": context.function_name,
                    "function_version": context.function_version,
                    "function_arn": context.invoked_function_arn,
                    "memory_limit": int(context.memory_limit_in_mb) if isinstance(context.memory_limit_in_mb, str) else context.memory_limit_in_mb,
                    "aws_request_id": context.aws_request_id,
                    "log_group": context.log_group_name,
                    "log_stream": context.log_stream_name,
                }

                # Add cold start metrics
                if cold_start_duration_ms is not None:
                    extra["cold_start"] = True
                    extra["cold_start_duration_ms"] = cold_start_duration_ms

                # Measure memory usage
                try:
                    memory_usage = resource.getrusage(resource.RUSAGE_SELF)
                    memory_used_mb = memory_usage.ru_maxrss / 1024  # KB to MB (Linux)
                    memory_limit_mb = extra["memory_limit"]
                    extra["memory_used_mb"] = round(memory_used_mb, 2)
                    extra["memory_usage_percent"] = round((memory_used_mb / memory_limit_mb) * 100, 2)
                except (AttributeError, OSError):
                    # Fallback for non-Linux or if resource module doesn't support it
                    pass

                # Get remaining time (if available)
                try:
                    remaining_time_ms = context.get_remaining_time_in_millis()
                    extra["remaining_time_ms"] = remaining_time_ms
                    if remaining_time_ms < timeout_warning_threshold_ms:
                        extra["timeout_warning"] = True
                except (AttributeError, TypeError):
                    # Context might not have get_remaining_time_in_millis method
                    pass

                # Extract retry attempt from event
                retry_attempt = event.get("retryAttempt") or event.get("requestContext", {}).get("requestId")
                if retry_attempt:
                    extra["retry_attempt"] = retry_attempt if isinstance(retry_attempt, int) else 0

                # Extract correlation ID if path provided
                if correlation_id_path:
                    correlation_id = self._extract_correlation_id(
                        event, correlation_id_path)
                    if correlation_id:
                        extra["correlation_id"] = correlation_id

                # Calculate event size (optimization: avoid logging large events)
                event_size = self._calculate_size(event)
                extra["event_size_bytes"] = event_size

                # Create child logger with context
                child_logger = self.logger.getChild(context.aws_request_id)
                child_logger.extra = extra

                # Replace logger for this invocation
                self.logger = child_logger

                # Log invocation with optimized event logging
                invocation_extra: LogExtra = {}
                if log_event:
                    if event_size <= max_event_size_bytes:
                        invocation_extra["event"] = event
                    else:
                        invocation_extra["event"] = {"_truncated": True, "_size_bytes": event_size}
                
                self.info("Lambda invocation started", extra=invocation_extra)

                try:
                    response = handler(event, context)
                    duration_ms = int((time.time() - invocation_start) * 1000)
                    
                    # Calculate response size
                    response_size = self._calculate_size(response)
                    extra["response_size_bytes"] = response_size
                    
                    # Log completion with optimized response logging
                    completion_extra: LogExtra = {
                        "duration_ms": duration_ms,
                    }
                    if log_response:
                        if response_size <= max_response_size_bytes:
                            completion_extra["response"] = response
                        else:
                            completion_extra["response"] = {"_truncated": True, "_size_bytes": response_size}
                    
                    # Add remaining time at completion
                    try:
                        remaining_time_ms = context.get_remaining_time_in_millis()
                        completion_extra["remaining_time_ms"] = remaining_time_ms
                    except (AttributeError, TypeError):
                        pass
                    
                    self.info("Lambda invocation completed", extra=completion_extra)
                    return response
                except Exception as e:
                    duration_ms = int((time.time() - invocation_start) * 1000)
                    error_extra: LogExtra = {
                        "duration_ms": duration_ms,
                        "error": str(e),
                    }
                    try:
                        remaining_time_ms = context.get_remaining_time_in_millis()
                        error_extra["remaining_time_ms"] = remaining_time_ms
                    except (AttributeError, TypeError):
                        pass
                    self.error("Lambda invocation failed", exc_info=True, extra=error_extra)
                    raise

            return wrapper
        return decorator

    def _extract_correlation_id(
        self, event: dict, path: str
    ) -> Optional[str]:
        """Extract correlation ID from event using JSON path.

        Args:
            event: Lambda event
            path: JSON path to correlation ID

        Returns:
            Correlation ID if found
        """
        try:
            value = event
            for key in path.split("."):
                value = value[key]
            return str(value)
        except (KeyError, TypeError):
            return None

    def _calculate_size(self, obj: Any) -> int:
        """Calculate approximate size of object in bytes.

        Args:
            obj: Object to measure

        Returns:
            Approximate size in bytes
        """
        try:
            return len(orjson.dumps(obj))
        except (TypeError, ValueError):
            # Fallback: estimate based on string representation
            return len(str(obj).encode('utf-8'))

    def debug(
        self, msg: str, *args: Any, extra: Optional[LogExtra] = None, **kwargs: Any
    ) -> None:
        """Log debug message with sampling.

        Args:
            msg: Message to log
            *args: Format args
            extra: Additional structured fields to include in log
            **kwargs: Additional fields
        """
        if self.sample_rate < 1.0:
            if random.random() > self.sample_rate:
                return
        self.logger.debug(msg, *args, extra=extra, **kwargs)

    def info(
        self, msg: str, *args: Any, extra: Optional[LogExtra] = None, **kwargs: Any
    ) -> None:
        """Log info message.

        Args:
            msg: Message to log
            *args: Format args
            extra: Additional structured fields to include in log
            **kwargs: Additional fields
        """
        self.logger.info(msg, *args, extra=extra, **kwargs)

    def warning(
        self, msg: str, *args: Any, extra: Optional[LogExtra] = None, **kwargs: Any
    ) -> None:
        """Log warning message.

        Args:
            msg: Message to log
            *args: Format args
            extra: Additional structured fields to include in log
            **kwargs: Additional fields
        """
        self.logger.warning(msg, *args, extra=extra, **kwargs)

    def error(
        self, msg: str, *args: Any, extra: Optional[LogExtra] = None, **kwargs: Any
    ) -> None:
        """Log error message.

        Args:
            msg: Message to log
            *args: Format args
            extra: Additional structured fields to include in log
            **kwargs: Additional fields
        """
        self.logger.error(msg, *args, extra=extra, **kwargs)

    def critical(
        self, msg: str, *args: Any, extra: Optional[LogExtra] = None, **kwargs: Any
    ) -> None:
        """Log critical message.

        Args:
            msg: Message to log
            *args: Format args
            extra: Additional structured fields to include in log
            **kwargs: Additional fields
        """
        self.logger.critical(msg, *args, extra=extra, **kwargs)

    def exception(
        self, msg: str, *args: Any, extra: Optional[LogExtra] = None, **kwargs: Any
    ) -> None:
        """Log exception message.

        Args:
            msg: Message to log
            *args: Format args
            extra: Additional structured fields to include in log
            **kwargs: Additional fields
        """
        kwargs["exc_info"] = True
        self.logger.exception(msg, *args, extra=extra, **kwargs)
