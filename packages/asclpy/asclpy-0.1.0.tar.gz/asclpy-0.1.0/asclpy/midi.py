"""
MIDI note to frequency mapping logic for tuning systems.
"""

from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

from .parser import AsclData, NoteRange
from .constants import (
    MIDI_NOTE_COUNT,
    MIDI_MIN,
    MIDI_MAX,
    MIDI_A4,
    MIDI_OCTAVE_OFFSET,
    TET_12_NOTES_PER_OCTAVE,
    DEFAULT_REFERENCE_FREQUENCY,
    DEFAULT_REFERENCE_OCTAVE,
    DEFAULT_REFERENCE_INDEX_12TET,
    DEFAULT_NOTES_BELOW_CENTER,
    DEFAULT_NOTES_ABOVE_CENTER,
)


class MidiMapper:
    """
    Maps MIDI note numbers to frequencies using a tuning system.

    Handles:
    - Reference pitch anchoring
    - NOTE_RANGE constraints from ASCL spec
    - Special handling for 12-note systems (MIDI compatibility)
    - Non-octave (pseudo-octave) scales
    """

    def __init__(self, tuning_data: AsclData):
        """
        Initialize MIDI mapper for a tuning system.

        Args:
            tuning_data: Parsed ASCL tuning data
        """
        self.data = tuning_data
        self.notes_per_octave = tuning_data.notes_per_octave

        # Build full pitch list including implied 0-cent first pitch
        self.pitches_cents = [0.0] + [p.value for p in tuning_data.pitches]

        # Get pseudo-octave size (last pitch)
        self.octave_cents = self.pitches_cents[-1]

        # Determine reference pitch
        self._setup_reference_pitch()

        # Calculate MIDI range
        self._min_midi, self._max_midi = self._calculate_midi_range()

        # Pre-calculate MIDI to frequency mapping
        self._freq_cache = self._build_frequency_map()

    def _setup_reference_pitch(self) -> None:
        """Set up reference pitch for the tuning system."""
        if self.data.reference_pitch:
            self.reference_octave = self.data.reference_pitch.octave
            self.reference_index = self.data.reference_pitch.note_index
            self.reference_frequency = self.data.reference_pitch.frequency
            
            # Determine if this is a loader-added default (MIDI octaves) or user-specified (ASCL octaves)
            # Loader defaults use: octave=3, index varies, freq=440.0 (for 12TET) or other patterns
            # Check if this matches the default pattern
            is_loader_default = (
                self.reference_octave == DEFAULT_REFERENCE_OCTAVE and 
                abs(self.reference_frequency - DEFAULT_REFERENCE_FREQUENCY) < 1.0
            )
            
            # Calculate which MIDI note corresponds to this octave/index
            if self.notes_per_octave == TET_12_NOTES_PER_OCTAVE:
                if is_loader_default:
                    # Loader defaults use MIDI octave numbering (octave 3 = MIDI 48-59)
                    self.reference_midi_note = (self.reference_octave - MIDI_OCTAVE_OFFSET) * 12 + self.reference_index
                else:
                    # User-specified REFERENCE_PITCH uses ASCL octave numbers where:
                    # octave N spans MIDI notes (N+1)*12 to (N+2)*12-1
                    # E.g., ASCL octave 4 = MIDI 60-71 (C4-B4 in scientific pitch notation)
                    self.reference_midi_note = (self.reference_octave + 1) * 12 + self.reference_index
            else:
                if is_loader_default:
                    self.reference_midi_note = MIDI_A4
                else:
                    # For non-12 systems, use approximation with ASCL octaves
                    self.reference_midi_note = (self.reference_octave + 1) * 12 + self.reference_index
        else:
            # Default: center around A3 440 Hz (MIDI 69)
            # Default uses MIDI octave numbering where octave 3 = MIDI 48-59
            # But A3 = MIDI 69, which uses the formula (octave - MIDI_OCTAVE_OFFSET) * 12 + index
            if self.notes_per_octave == TET_12_NOTES_PER_OCTAVE:
                self.reference_octave = DEFAULT_REFERENCE_OCTAVE
                self.reference_index = DEFAULT_REFERENCE_INDEX_12TET
                self.reference_frequency = DEFAULT_REFERENCE_FREQUENCY
                self.reference_midi_note = (DEFAULT_REFERENCE_OCTAVE - MIDI_OCTAVE_OFFSET) * 12 + DEFAULT_REFERENCE_INDEX_12TET
            else:
                # For non-12-note systems, center around A440
                # Use MIDI 69 as the anchor point
                self.reference_octave = DEFAULT_REFERENCE_OCTAVE
                self.reference_index = 0
                self.reference_frequency = DEFAULT_REFERENCE_FREQUENCY
                self.reference_midi_note = MIDI_A4

    def _calculate_midi_range(self) -> Tuple[int, int]:
        """
        Calculate the valid MIDI note range based on NOTE_RANGE directives.

        Returns:
            Tuple of (min_midi, max_midi) inclusive
        """
        note_range = self.data.note_range

        if not note_range:
            # Default: center around MIDI 69 with 64 below, 63 above
            if self.notes_per_octave == TET_12_NOTES_PER_OCTAVE:
                # Special case: for 12-note systems, use standard MIDI range
                # but center the closest note to A440 at MIDI 69
                return (MIDI_MIN, MIDI_MAX)
            else:
                center = MIDI_A4
                return (
                    max(MIDI_MIN, center - DEFAULT_NOTES_BELOW_CENTER),
                    min(MIDI_MAX, center + DEFAULT_NOTES_ABOVE_CENTER),
                )

        # NOTE_RANGE_BY_FREQUENCY
        if note_range.min_freq is not None:
            return self._midi_range_by_frequency(note_range)

        # NOTE_RANGE_BY_INDEX
        if note_range.min_octave is not None:
            return self._midi_range_by_index(note_range)

        # No range specified
        return (MIDI_MIN, MIDI_MAX)

    def _midi_range_by_frequency(self, note_range: NoteRange) -> Tuple[int, int]:
        """Calculate MIDI range from frequency constraints."""
        # Find MIDI notes that fall within the frequency range
        # For now, use a simple approach: generate all frequencies and filter
        min_midi = MIDI_MIN
        max_midi = MIDI_MAX

        # Calculate frequency for each MIDI note and find the range
        for midi_num in range(MIDI_MIN, MIDI_MAX + 1):
            freq = self._calculate_frequency_for_midi(midi_num)
            if freq >= note_range.min_freq:
                min_midi = midi_num
                break

        if note_range.max_freq:
            for midi_num in range(MIDI_MAX, MIDI_MIN - 1, -1):
                freq = self._calculate_frequency_for_midi(midi_num)
                if freq <= note_range.max_freq:
                    max_midi = midi_num
                    break

        return (min_midi, max_midi)

    def _midi_range_by_index(self, note_range: NoteRange) -> Tuple[int, int]:
        """Calculate MIDI range from octave/index constraints."""
        # Convert octave/index to MIDI note number
        # For 12-note systems, we can use standard MIDI numbering
        if self.notes_per_octave == TET_12_NOTES_PER_OCTAVE:
            # ASCL octave numbering: octave N, index I → MIDI (N * 12 + I)
            # Octave 0 starts at MIDI 0, Octave 1 at MIDI 12, etc.
            min_midi = note_range.min_octave * 12 + note_range.min_index

            if note_range.max_octave is not None and note_range.max_index is not None:
                max_midi = note_range.max_octave * 12 + note_range.max_index
            else:
                # No max specified, use default
                max_midi = min(MIDI_MAX, min_midi + MIDI_NOTE_COUNT - 1)

            return (max(MIDI_MIN, min_midi), min(MIDI_MAX, max_midi))
        else:
            # For non-12-note systems, map to MIDI range centered around reference
            # This is approximate - the spec doesn't fully define this
            ref_midi = self._octave_index_to_midi(self.reference_octave, self.reference_index)
            min_midi = self._octave_index_to_midi(note_range.min_octave, note_range.min_index)

            if note_range.max_octave is not None and note_range.max_index is not None:
                max_midi = self._octave_index_to_midi(note_range.max_octave, note_range.max_index)
            else:
                max_midi = min(MIDI_MAX, min_midi + MIDI_NOTE_COUNT - 1)

            return (max(MIDI_MIN, min_midi), min(MIDI_MAX, max_midi))

    def _octave_index_to_midi(self, octave: int, index: int) -> int:
        """Convert octave and note index to approximate MIDI note number."""
        # Calculate offset from reference in terms of pitch classes
        octave_offset = octave - self.reference_octave
        total_pitch_classes = octave_offset * self.notes_per_octave + (index - self.reference_index)

        # Map to MIDI centered around reference pitch
        if self.notes_per_octave == TET_12_NOTES_PER_OCTAVE:
            # ASCL octave numbering: octave N, index I → MIDI (N * 12 + I)
            return octave * 12 + index
        else:
            # For non-12 systems, approximate mapping relative to reference
            ref_midi = self.reference_octave * 12 + self.reference_index
            return ref_midi + total_pitch_classes

    def _build_frequency_map(self) -> Dict[int, float]:
        """Build a mapping of MIDI note numbers to frequencies."""
        freq_map = {}

        for midi_num in range(self._min_midi, self._max_midi + 1):
            freq_map[midi_num] = self._calculate_frequency_for_midi(midi_num)

        return freq_map

    def _calculate_frequency_for_midi(self, midi_num: int) -> float:
        """
        Calculate frequency for a MIDI note number.

        This implements the core tuning algorithm.
        """
        # Get the reference pitch in cents
        reference_pitch_cents = self.pitches_cents[self.reference_index]

        if self.notes_per_octave == TET_12_NOTES_PER_OCTAVE:
            # Standard MIDI numbering for 12-note systems
            # For 12TET, each MIDI semitone is exactly 100 cents
            midi_offset = midi_num - self.reference_midi_note
            cents_from_ref = midi_offset * 100.0
        else:
            # For non-12-note systems, center around the reference
            # Calculate which degree of the scale this MIDI note maps to
            midi_offset = midi_num - MIDI_A4

            # Calculate pseudo-octaves and pitch class from MIDI offset
            octaves_from_ref = midi_offset // self.notes_per_octave
            index = midi_offset % self.notes_per_octave

            if index < 0:
                index += self.notes_per_octave
                octaves_from_ref -= 1

            # Calculate cents from reference
            cents_from_ref_note = self.pitches_cents[index] - reference_pitch_cents
            cents_from_ref = (octaves_from_ref * self.octave_cents) + cents_from_ref_note

        # Convert cents to frequency ratio: 2^(cents/1200)
        freq_ratio = 2.0 ** (cents_from_ref / 1200.0)
        return self.reference_frequency * freq_ratio

    def midi_to_freq(self, midi_num: int) -> float:
        """
        Convert MIDI note number to frequency in Hz.

        Args:
            midi_num: MIDI note number (0-127)

        Returns:
            Frequency in Hz

        Raises:
            ValueError: If MIDI number is outside valid range for this tuning
        """
        if not (MIDI_MIN <= midi_num <= MIDI_MAX):
            raise ValueError(
                f"MIDI note number must be {MIDI_MIN}-{MIDI_MAX}, got {midi_num}"
            )

        if midi_num not in self._freq_cache:
            raise ValueError(
                f"MIDI note {midi_num} is outside the valid range "
                f"[{self._min_midi}, {self._max_midi}] for this tuning"
            )

        return self._freq_cache[midi_num]

    def get_frequency_map(self) -> Dict[int, float]:
        """
        Get the complete MIDI-to-frequency mapping.

        Returns:
            Dictionary mapping MIDI note numbers to frequencies in Hz
        """
        return self._freq_cache.copy()

    def get_valid_range(self) -> Tuple[int, int]:
        """
        Get the valid MIDI note range for this tuning.

        Returns:
            Tuple of (min_midi, max_midi) inclusive
        """
        return (self._min_midi, self._max_midi)

    def is_midi_valid(self, midi_num: int) -> bool:
        """
        Check if a MIDI note number is valid for this tuning.

        Args:
            midi_num: MIDI note number to check

        Returns:
            True if the MIDI note is in the valid range
        """
        return self._min_midi <= midi_num <= self._max_midi
