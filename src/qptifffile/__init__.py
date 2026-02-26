import warnings

from .mxtifffile import MxTiffFile
from .exceptions import MxTiffFormatError
from .format_config import load_formats
from .format_detector import detect_format
from .heuristic import heuristic_detect, ANCHOR_MARKER


class QPTiffFile(MxTiffFile):
    """Deprecated alias for MxTiffFile. Use MxTiffFile instead."""

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "QPTiffFile is deprecated, use MxTiffFile",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


__all__ = [
    'MxTiffFile',
    'QPTiffFile',
    'MxTiffFormatError',
    'load_formats',
    'detect_format',
    'heuristic_detect',
    'ANCHOR_MARKER',
]
