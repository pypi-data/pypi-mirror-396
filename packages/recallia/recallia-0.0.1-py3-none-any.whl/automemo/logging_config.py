import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog

JSON_LOG_FILENAME = 'pipeline.jsonl'


def configure_logging(log_dir: Path) -> structlog.stdlib.BoundLogger:
    """Configure structlog with colored console + JSONL file output."""
    log_dir.mkdir(parents=True, exist_ok=True)
    json_log_path = log_dir / JSON_LOG_FILENAME

    shared_processors = [
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    console_renderer = structlog.dev.ConsoleRenderer(colors=True)
    json_renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors +
        [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    console_handler = StreamHandler()
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=console_renderer,
            foreign_pre_chain=shared_processors,
        ),
    )

    json_handler = RotatingFileHandler(
        json_log_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8',
    )
    json_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=json_renderer,
            foreign_pre_chain=shared_processors,
        ),
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(json_handler)

    logger = structlog.get_logger('recallia')
    logger.info('logging_configured', json_log=str(json_log_path))
    return logger
