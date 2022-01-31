import logging
import logging.config
import socket

import structlog
from structlog.processors import CallsiteParameter
from structlog_sentry import SentryJsonProcessor

from .processors import inject_context_dict


def _add_hostname(_, __, event_dict):
    event_dict['host'] = socket.gethostname()
    return event_dict


def _add_application_name(_, __, event_dict):
    record = event_dict["_record"]
    event_dict["application"] = record.app
    return event_dict


def _add_application_type(_, __, event_dict):
    record = event_dict["_record"]
    event_dict['application_type'] = record.app_type
    return event_dict


def _add_environment(_, __, event_dict):
    record = event_dict["_record"]
    event_dict["environment"] = record.environment
    return event_dict


class AppFilter(logging.Filter):
    def __init__(self, name=None):
        self.app = name

    def filter(self, record):
        record.app = self.app
        return True


class AppTypeFilter(logging.Filter):
    def __init__(self, type=None):
        self.app_type = type

    def filter(self, record):
        record.app_type = self.app_type
        return True


class EnvFilter(logging.Filter):
    def __init__(self, env=None):
        self.environment = env

    def filter(self, record):
        record.environment = self.environment
        return True


def configure_struct_logging(app_name, app_type, env, log_level="INFO", enable_log_file=False, formatter=None):
    pre_chain = [
        inject_context_dict,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        structlog.processors.CallsiteParameterAdder({
            CallsiteParameter.PATHNAME,
            CallsiteParameter.FILENAME,
            CallsiteParameter.FUNC_NAME,
            CallsiteParameter.PROCESS,
            CallsiteParameter.THREAD,
            CallsiteParameter.LINENO,
        }),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
    ]

    handlers = ["console"]
    if enable_log_file:
        handlers.append("jsonFile")

    if formatter is None:
        formatter = "json_formatter"

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json_formatter": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    _add_hostname,
                    _add_application_name,
                    _add_application_type,
                    _add_environment,
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.JSONRenderer(),
                ],
                "foreign_pre_chain": pre_chain,
            },
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    _add_hostname,
                    _add_application_name,
                    _add_application_type,
                    _add_environment,
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.dev.ConsoleRenderer(colors=True),
                ],
                "foreign_pre_chain": pre_chain,
            }
        },
        "filters": {
            'app': {
                '()': AppFilter,
                'name': app_name
            },
            'app_type': {
                '()': AppTypeFilter,
                'type': app_type
            },
            'env': {
                '()': EnvFilter,
                'env': env
            }
        },
        "handlers": {
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": formatter,
                "filters": [
                    "app",
                    "app_type",
                    "env"
                ]
            },
            "jsonFile": {
                "level": log_level,
                "class": "logging.handlers.WatchedFileHandler",
                "filename": "logs/{}.log".format(app_name),
                "formatter": "json_formatter",
                "filters": [
                    "app",
                    "app_type",
                    "env"
                ]
            }
        },
        "loggers": {
            "django_structlog": {
                "handlers": handlers,
                "level": log_level,
                "propagate": False
            },
            "foreign_logger": {
                "handlers": handlers,
                "level": log_level,
                "propagate": False
            },
            "": {
                "handlers": handlers,
                "level": log_level,
            }
        },
    })

    structlog.configure_once(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.CallsiteParameterAdder({
                CallsiteParameter.PATHNAME,
                CallsiteParameter.FILENAME,
                CallsiteParameter.FUNC_NAME,
                CallsiteParameter.PROCESS,
                CallsiteParameter.THREAD,
                CallsiteParameter.LINENO,
            }),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
            SentryJsonProcessor(level=logging.ERROR),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

