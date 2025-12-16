"""client specific logger"""

from ..logging._logger import get_library_logger

__all__ = ("logger",)

logger = get_library_logger()
