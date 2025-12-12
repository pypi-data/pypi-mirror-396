import logging

from rich.logging import RichHandler


def config_log(level: int = logging.INFO):
    # TODO: 使用 loguru
    logging.basicConfig(level=level, handlers=[RichHandler(rich_tracebacks=True)])
