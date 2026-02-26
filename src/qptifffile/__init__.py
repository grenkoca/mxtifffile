from .qptifffile import QPTiffFile
from .exceptions import MxTiffFormatError
from .format_config import load_formats
from .format_detector import detect_format
from .heuristic import heuristic_detect, ANCHOR_MARKER

__all__ = ['QPTiffFile', 'MxTiffFormatError', 'load_formats', 'detect_format', 'heuristic_detect', 'ANCHOR_MARKER']
