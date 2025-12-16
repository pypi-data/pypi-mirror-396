import contextlib
import json
import logging
import os
import sys
from contextvars import ContextVar

from baresquare_sdk.settings import get_settings

# App-configurable log context. Apps can set this to automatically inject fields into all logs.
# Example: log_context.set({"loader": "example_loader", "file": "data.zip"})
log_context: ContextVar[dict] = ContextVar("log_context", default={})


def get_request_context():
    """Get the entire request context dictionary.

    Merges context from:
    1. log_context contextvar (preferred, set by app via log_context.set({...}))
    2. Legacy app.main.request_context (for backwards compatibility)
    """
    context = {}

    # Add log_context if set
    with contextlib.suppress(LookupError):
        context.update(log_context.get())

    # Legacy: check app.main.request_context for backwards compatibility
    try:
        main_module = sys.modules.get("app.main")
        if main_module and hasattr(main_module, "request_context"):
            try:
                legacy_context = main_module.request_context.get()
                if legacy_context:
                    context.update(legacy_context)
            except LookupError:
                pass
            except Exception:
                pass
    except Exception:
        pass

    return context


def sanitise_secret(input_key, input_value):
    key_str = str(input_key).lower()
    if key_str == "authentication":
        return "*REDACTED*"
    if key_str in ["authorization", "authorisation"]:
        return "*REDACTED*" + str(input_value)[-3:]
    if key_str == "client_secret":
        return "*REDACTED*"
    if key_str == "password":
        return "*REDACTED*"
    return input_value


def sanitise_secrets(input_obj):
    """Walk a possibly complex JSON object and return a *copy* of the original JSON object with secrets redacted.

    Example:
        - input: {"password": "value-password"}
        - output: {"password": "*REDACTED*"}

    Note that, since the method returns a copy of the input, passing a big JSON object may consume a lot of memory
    """
    if isinstance(input_obj, dict):
        modified_obj = {}
        for key, value in input_obj.items():
            modified_value = sanitise_secret(key, value)
            if isinstance(value, (dict, list)):
                modified_value = sanitise_secrets(value)
            modified_obj[key] = modified_value
        return modified_obj
    if isinstance(input_obj, list):
        modified_value = []
        for item in input_obj:
            if isinstance(item, dict):
                modified_value.append(sanitise_secrets(item))
            else:
                modified_value.append(item)
        return modified_value

    return input_obj


class JSONFormatter(logging.Formatter):
    """Structured JSON formatter for non-dev environments (GCP/AWS/etc)."""

    def __init__(self, extra_fields=None):
        super().__init__()
        self.extra_fields = extra_fields or {}

    def format(self, record):
        # GCP requires field `severity` instead of `level` (used in AWS). Message is also for GCP.
        log_record = {"level": record.levelname, "severity": record.levelname, "message": record.getMessage()}
        settings = get_settings()
        if settings.pl_env != "dev":
            log_record["env"] = settings.pl_env
            log_record["service"] = settings.pl_service
        if record.exc_info:
            try:
                log_record["exception"] = sanitise_secrets(self.formatException(record.exc_info))
            except Exception:
                # Fallback in case formatException itself fails
                log_record["exception"] = "Exception formatting failed"

        # file (instead of the default filename) is used in datadog alerts
        log_record["file"] = record.filename

        # Add custom fields provided in extra_fields
        log_record.update(self.extra_fields)

        # Add request_context params to log_record
        context = get_request_context()
        if context:
            log_record.update(context)

        # Update with log-specific fields (this also brings in things added via `extra=...`)
        if record.__dict__:
            log_record.update(record.__dict__)

        # Some third party libraries (e.g. requests) include non-serializable objects in records; coerce to string where needed
        # Without it, we are getting  --- Logging error --- in the logs which is super spammy
        for key, value in record.__dict__.items():
            try:
                json.dumps(value)  # Check if value is JSON serializable
                log_record[key] = value
            except TypeError:
                log_record[key] = str(value)

        log_record = sanitise_secrets(log_record)
        return json.dumps(log_record)


class JSONLogger(logging.Logger):
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stack_level=1):
        if extra is None:
            extra = {}
        if isinstance(extra, dict):
            # shallow copy to avoid side-effects
            extra = {**extra}
        super()._log(level, msg, args, exc_info, extra, stack_info, stack_level)


class DevFormatter(logging.Formatter):
    """Human-friendly formatter for dev: concise line + optional inline traceback.

    Shows: level initial, time, logger:lineno — message
    Appends traceback as a new line when available, using either:
      - extra["traceback"] if provided, or
      - record.exc_info if set via logger.*(..., exc_info=True)
    """

    default_fmt = "%(levelname).1s %(asctime)s %(filename)-20s:%(lineno)4d │ %(message)s"
    default_datefmt = "%H:%M:%S"

    def __init__(self):
        super().__init__(fmt=self.default_fmt, datefmt=self.default_datefmt)

    def format(self, record):
        # Temporarily clear exc_info to prevent the base class from formatting it,
        # allowing our custom logic below to handle tracebacks exclusively.
        # Without this, the traceback is formatted twice for the "fallback" (i.e. not rich-based) formatter.
        original_exc_info = record.exc_info
        record.exc_info = None

        base = super().format(record)

        # Restore exc_info for our custom handling
        record.exc_info = original_exc_info

        tb = None
        # Prefer explicit traceback provided via extra
        if "traceback" in record.__dict__ and record.__dict__["traceback"]:
            tb = record.__dict__["traceback"]
        # Otherwise, render from exc_info if present
        elif record.exc_info:
            try:
                tb = self.formatException(record.exc_info)
            except Exception:
                tb = None

        if tb:
            base += f"\n{tb}"

        return base


def create_dev_handler():
    """Create a dev handler. Use Rich if available; otherwise plain StreamHandler."""
    try:
        # Rich adds colors and nicer tracebacks if exc_info is set
        from rich.logging import RichHandler  # optional dependency

        handler = RichHandler(
            rich_tracebacks=True,
            show_time=False,
            show_level=False,
            show_path=False,
            markup=False,
        )
        # Use our DevFormatter to control the message layout and append extra["traceback"]
        handler.setFormatter(DevFormatter())
        return handler
    except Exception:
        handler = logging.StreamHandler()
        handler.setFormatter(DevFormatter())
        return handler


def setup_logger(extra_fields=None):
    """Configure the root logger for the application.

    This function resets the logging configuration, sets a custom logger class,
    and configures a handler that formats logs as JSON in production or as
    human-readable text in a local TTY development environment.

    Args:
        extra_fields (dict, optional): A dictionary of extra fields to include
            in every log record. Defaults to None.
    """
    settings = get_settings()
    is_dev = settings.pl_env == "dev" and sys.stderr.isatty()
    level = (os.getenv("LOG_LEVEL") or "INFO").upper()

    logging.setLoggerClass(JSONLogger)

    # Create the appropriate handler for the environment
    if is_dev:
        handler = create_dev_handler()
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter(extra_fields))

    # Use basicConfig to cleanly set up the root logger.
    # The `force=True` argument removes any existing handlers.
    logging.basicConfig(level=level, handlers=[handler], force=True)

    # In dev, silence noisy libraries to reduce spam. In production, we let
    # them log at the default level, and our handler will format them as JSON.
    if is_dev:
        for logger_name in ["urllib3", "botocore", "boto3", "asyncio"]:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

    logging.getLogger().extra_fields = dict(extra_fields or {})
    return logging.getLogger()


def get_logger():
    """Get the module logger, initializing it if necessary."""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


# For backward compatibility, expose logger as a property-like access
class LoggerProxy:
    """Proxy to provide lazy logger access while maintaining attribute access."""

    def __getattr__(self, name):
        return getattr(get_logger(), name)

    def __call__(self, *args, **kwargs):
        return get_logger()(*args, **kwargs)


# Module-level logger - initialized lazily
_logger = None

logger = LoggerProxy()


if __name__ == "__main__":
    # Example of adding extra fields during setup
    xf = {"app_version": "1.2.3", "team": "platform"}
    my_logger = setup_logger(xf)
    my_logger.info("Application started")

    my_logger.info("Extras provided (but not printed in dev)", extra={"test": 1})

    try:
        1 / 0
    except Exception:
        # Demonstrate both mechanisms:
        # 1) exc_info=True (auto captured & pretty in dev)
        my_logger.error("Division failed (exc_info example)", exc_info=True)
