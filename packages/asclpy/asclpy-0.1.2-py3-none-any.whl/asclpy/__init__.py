"""
asclpy - Parser for .ascl (Ableton Scala) tuning files

A Python library for parsing .ascl tuning files and computing MIDI-to-frequency
mappings for alternative tuning systems.
"""

from .parser import parse_ascl_file, parse_ascl_string, AsclData
from .tuning import Tuning
from .loader import load_tuning, list_tunings, TuningRegistry, get_default_registry
from .midi import MidiMapper
from .validation import validate_ascl_data, ValidationError, ValidationWarning

__version__ = "0.1.0"
__all__ = [
    # Parsing
    "parse_ascl_file",
    "parse_ascl_string",
    "AsclData",
    # Tuning
    "Tuning",
    # Loading
    "load_tuning",
    "list_tunings",
    "TuningRegistry",
    "get_default_registry",
    # MIDI mapping
    "MidiMapper",
    # Validation
    "validate_ascl_data",
    "ValidationError",
    "ValidationWarning",
]
