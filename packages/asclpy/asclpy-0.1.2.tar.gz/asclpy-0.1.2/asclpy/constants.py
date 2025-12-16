"""
Constants for ASCL tuning system calculations.

This module contains only constant values - no business logic.
"""

# MIDI Constants
MIDI_NOTE_COUNT = 128
MIDI_MIN = 0
MIDI_MAX = 127
MIDI_A4 = 69
MIDI_MIDDLE_C = 60

# Standard reference pitch
DEFAULT_REFERENCE_FREQUENCY = 440.0  # A4 in Hz
DEFAULT_REFERENCE_OCTAVE = 3
DEFAULT_REFERENCE_INDEX_12TET = 9  # A in 12-TET (C=0)

# MIDI note numbering: note 0 = C-2, note 12 = C-1, note 60 = C3, note 69 = A3
MIDI_OCTAVE_OFFSET = -2  # MIDI note 0 starts at octave -2

# Standard 12-TET constants
TET_12_NOTES_PER_OCTAVE = 12
CENTS_PER_OCTAVE_2_1 = 1200.0  # Cents in a 2:1 octave
CENTS_PER_SEMITONE_12TET = 100.0

# Frequency constraints from ASCL spec
MIN_FREQUENCY_HZ = 4.0
MAX_FREQUENCY_HZ = 21000.0

# Note: We don't enforce octave range limits because MIDI notes are
# always clamped to [0, 127] regardless of the octave values in the file.
# Ableton tunings use very wide ranges (e.g., octave -10 to 15) that work fine.

# Default MIDI note range (used when NOTE_RANGE is not specified)
# Spec: "64 notes below the center point, and 63 notes above it"
DEFAULT_NOTES_BELOW_CENTER = 64
DEFAULT_NOTES_ABOVE_CENTER = 63
