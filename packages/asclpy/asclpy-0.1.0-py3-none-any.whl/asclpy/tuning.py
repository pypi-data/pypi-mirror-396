"""
Tuning system representation.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .parser import AsclData
from .midi import MidiMapper


class Tuning:
    """
    Represents a tuning system parsed from an .ascl file.

    This class provides:
    - Tuning system metadata (description, pitch classes, note names)
    - MIDI note to frequency conversion
    - Access to tuning structure information
    - Validation warnings about the tuning data

    Example:
        >>> from asclpy import load_tuning
        >>> tuning = load_tuning("12_tet_edo")
        >>> tuning.midi_to_freq(69)  # A4
        440.0
        >>> tuning.notes_per_octave
        12
        >>> tuning.validation_warnings  # List of any validation issues
        []
    """

    def __init__(self, data: AsclData):
        """
        Initialize a Tuning from parsed .ascl data.

        Args:
            data: Parsed AsclData object from parse_ascl_file() or parse_ascl_string()
        """
        self.data = data

        # Basic tuning properties
        self.description = data.description
        self.notes_per_octave = data.notes_per_octave

        # Build full pitch list including implied 0-cent first pitch
        self.pitches_cents = [0.0] + [p.value for p in data.pitches]

        # Pseudo-octave size (last pitch)
        self.octave_cents = self.pitches_cents[-1]

        # Note names (if provided)
        self.note_names = data.note_names

        # Metadata
        self.source = data.source
        self.link = data.link
        
        # Validation warnings
        self.validation_warnings = data.validation_warnings or []

        # Create MIDI mapper for frequency conversion
        self._midi_mapper = MidiMapper(data)

        # Reference pitch properties (from mapper)
        self.reference_octave = self._midi_mapper.reference_octave
        self.reference_index = self._midi_mapper.reference_index
        self.reference_frequency = self._midi_mapper.reference_frequency

    def get_note_name(self, pitch_class: int) -> Optional[str]:
        """
        Get the name of a pitch class if NOTE_NAMES was specified.

        Args:
            pitch_class: Index of the pitch class (0 to notes_per_octave - 1)

        Returns:
            Note name string, or None if NOTE_NAMES not specified

        Raises:
            IndexError: If pitch_class is out of range
        """
        if not self.note_names:
            return None

        if not (0 <= pitch_class < self.notes_per_octave):
            raise IndexError(
                f"Pitch class {pitch_class} out of range [0, {self.notes_per_octave})"
            )

        # note_names includes the 0th degree
        return self.note_names[pitch_class]

    def get_pitch_cents(self, pitch_class: int) -> float:
        """
        Get the pitch in cents for a pitch class.

        Args:
            pitch_class: Index of the pitch class (0 to notes_per_octave - 1)

        Returns:
            Pitch in cents relative to the 0th degree

        Raises:
            IndexError: If pitch_class is out of range
        """
        if not (0 <= pitch_class < len(self.pitches_cents)):
            raise IndexError(
                f"Pitch class {pitch_class} out of range [0, {len(self.pitches_cents)})"
            )

        return self.pitches_cents[pitch_class]

    def get_valid_midi_range(self) -> Tuple[int, int]:
        """
        Get the valid MIDI note range for this tuning.

        Returns:
            Tuple of (min_midi, max_midi) inclusive

        Example:
            >>> tuning = load_tuning("12_tet_edo")
            >>> tuning.get_valid_midi_range()
            (0, 127)
        """
        return self._midi_mapper.get_valid_range()

    def is_midi_valid(self, midi_num: int) -> bool:
        """
        Check if a MIDI note number is valid for this tuning.

        Args:
            midi_num: MIDI note number to check

        Returns:
            True if the MIDI note is in the valid range for this tuning
        """
        return self._midi_mapper.is_midi_valid(midi_num)

    def midi_to_freq(self, midi_num: int) -> float:
        """
        Convert MIDI note number to frequency in Hz.
 for this tuning

        Example:
            >>> tuning = load_tuning("12_tet_edo")
            >>> tuning.midi_to_freq(69)  # A4
            440.0
            >>> tuning.midi_to_freq(60)  # Middle C
            261.6255653005986
        """
        return self._midi_mapper.midi_to_freq(midi_num)

    def get_midi_to_freq_dict(self) -> Dict[int, float]:
        """
        Get a dictionary mapping MIDI notes to frequencies.

        Only includes MIDI notes in the valid range for this tuning.

        Returns:
            Dictionary {midi_num: frequency_hz}

        Example:
            >>> tuning = load_tuning("12_tet_edo")
            >>> freq_map = tuning.get_midi_to_freq_dict()
            >>> len(freq_map)
            128
        """
        return self._midi_mapper.get_frequency_map()

    def has_warnings(self) -> bool:
        """Check if this tuning has any validation warnings."""
        return len(self.validation_warnings) > 0

    def __repr__(self) -> str:
        warnings_str = f", {len(self.validation_warnings)} warnings" if self.has_warnings() else ""
        return f"Tuning({self.notes_per_octave} notes, '{self.description[:50]}...'{warnings_str})"

    def __eq__(self, other) -> bool:
        """Check if two tunings are equal based on their pitch definitions."""
        if not isinstance(other, Tuning):
            return False
        return (
            self.notes_per_octave == other.notes_per_octave
            and self.pitches_cents == other.pitches_cents
            and self.reference_frequency == other.reference_frequency
            and self.reference_index == other.reference_index
            and self.reference_octave == other.reference_octave
        )
