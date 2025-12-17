from __future__ import annotations

__version__ = "0.1.0"

from .cli import main
from .utils import (
    save_time_statistics,
    send_wecom_markdown,
    send_wecom_text,
    send_wecom_text_for_file,
    time_statistics,
)

__all__ = [
    "__version__",
    "main",
    "time_statistics",
    "save_time_statistics",
    "send_wecom_text_for_file",
    "send_wecom_markdown",
    "send_wecom_text",
]
