"""
Validation logic for ASCL file data according to the specification.
"""

from __future__ import annotations

from typing import List, Optional
import warnings

from .parser import AsclData, ReferencePitch, NoteRange
from .constants import (
    MIN_FREQUENCY_HZ,
    MAX_FREQUENCY_HZ,
)


class ValidationError(ValueError):
    """Raised when ASCL data violates specification constraints."""

    pass


class ValidationWarning(UserWarning):
    """Warning for non-critical validation issues."""

    pass


def validate_ascl_data(data: AsclData, strict: bool = False) -> List[str]:
    """
    Validate ASCL data according to specification.

    Args:
        data: Parsed ASCL data to validate
        strict: If True, raise exceptions for warnings. If False, collect warnings.

    Returns:
        List of validation warning messages

    Raises:
        ValidationError: If data violates hard constraints (always raised)
        ValidationError: If strict=True and data violates soft constraints
    """
    warnings_list = []

    # Validate reference pitch
    if data.reference_pitch:
        _validate_reference_pitch(data.reference_pitch, data.notes_per_octave, strict)

    # Validate note range
    if data.note_range:
        _validate_note_range(data.note_range, data.reference_pitch, strict)

    # Validate note names count
    if data.note_names:
        if len(data.note_names) != data.notes_per_octave:
            raise ValidationError(
                f"NOTE_NAMES count {len(data.note_names)} does not match "
                f"notes_per_octave {data.notes_per_octave}"
            )

    # Validate pitch definitions and collect warnings
    pitch_warnings = _validate_pitches(data.pitches, data.notes_per_octave, strict)
    warnings_list.extend(pitch_warnings)

    return warnings_list


def _validate_reference_pitch(
    ref: ReferencePitch, notes_per_octave: int, strict: bool
) -> None:
    """Validate REFERENCE_PITCH directive constraints."""
    # Hard constraints from spec
    # Note: We don't validate octave range because MIDI notes are clamped to [0, 127]

    if not (0 <= ref.note_index < notes_per_octave):
        raise ValidationError(
            f"Reference pitch note_index {ref.note_index} outside valid range "
            f"[0, {notes_per_octave})"
        )

    if ref.frequency <= 0:
        raise ValidationError(
            f"Reference pitch frequency must be positive, got {ref.frequency}"
        )

    # Soft constraints - emit warnings
    if not (MIN_FREQUENCY_HZ <= ref.frequency <= MAX_FREQUENCY_HZ):
        msg = (
            f"Reference pitch frequency {ref.frequency} Hz outside typical range "
            f"[{MIN_FREQUENCY_HZ}, {MAX_FREQUENCY_HZ}] Hz"
        )
        if strict:
            raise ValidationError(msg)
        warnings.warn(msg, ValidationWarning)


def _validate_note_range(
    note_range: NoteRange, reference_pitch: Optional[ReferencePitch], strict: bool
) -> None:
    """Validate NOTE_RANGE directive constraints."""
    # Check for both frequency and index ranges (should only have one)
    has_freq_range = note_range.min_freq is not None
    has_index_range = note_range.min_octave is not None

    if has_freq_range and has_index_range:
        raise ValidationError(
            "Cannot have both NOTE_RANGE_BY_FREQUENCY and NOTE_RANGE_BY_INDEX"
        )

    # Validate frequency-based range
    if has_freq_range:
        if note_range.min_freq < MIN_FREQUENCY_HZ:
            msg = (
                f"NOTE_RANGE min_freq {note_range.min_freq} below minimum "
                f"{MIN_FREQUENCY_HZ} Hz"
            )
            if strict:
                raise ValidationError(msg)
            warnings.warn(msg, ValidationWarning)

        if note_range.max_freq and note_range.max_freq > MAX_FREQUENCY_HZ:
            msg = (
                f"NOTE_RANGE max_freq {note_range.max_freq} above maximum "
                f"{MAX_FREQUENCY_HZ} Hz"
            )
            if strict:
                raise ValidationError(msg)
            warnings.warn(msg, ValidationWarning)

        if note_range.max_freq and note_range.max_freq < note_range.min_freq:
            raise ValidationError(
                f"NOTE_RANGE max_freq {note_range.max_freq} less than "
                f"min_freq {note_range.min_freq}"
            )

    # Validate index-based range
    if has_index_range:
        # Spec: NOTE_RANGE_BY_INDEX requires REFERENCE_PITCH
        if not reference_pitch:
            raise ValidationError(
                "NOTE_RANGE_BY_INDEX requires REFERENCE_PITCH to be defined"
            )

        # Note: We don't validate octave ranges because MIDI notes are clamped to [0, 127]
        # Ableton tunings use wide ranges (e.g., octave -10 to 15) that work fine.

        if note_range.max_octave and note_range.max_octave < note_range.min_octave:
            raise ValidationError(
                f"NOTE_RANGE max_octave {note_range.max_octave} must be >= min_octave {note_range.min_octave}"
            )


def _validate_pitches(pitches: List, notes_per_octave: int, strict: bool) -> List[str]:
    """Validate pitch definitions and return warnings."""
    warnings_list = []

    if not pitches:
        raise ValidationError("No pitch definitions found")

    if len(pitches) != notes_per_octave:
        raise ValidationError(
            f"Expected {notes_per_octave} pitches, got {len(pitches)}"
        )

    # Check that pitches are monotonically increasing
    prev_cents = 0.0
    for i, pitch in enumerate(pitches):
        if pitch.value < prev_cents:
            msg = (
                f"Pitch {i} ({pitch.value} cents) is less than previous pitch "
                f"({prev_cents} cents). Pitches should be monotonically increasing."
            )
            if strict:
                raise ValidationError(msg)
            warnings_list.append(msg)
        prev_cents = pitch.value

    # Check that last pitch defines a reasonable pseudo-octave
    octave_cents = pitches[-1].value
    if octave_cents <= 0:
        raise ValidationError(
            f"Pseudo-octave size must be positive, got {octave_cents} cents"
        )

    # Warn about unusual pseudo-octave sizes
    if octave_cents < 600 or octave_cents > 2400:
        msg = (
            f"Unusual pseudo-octave size: {octave_cents} cents. "
            f"Typical range is 600-2400 cents."
        )
        if strict:
            raise ValidationError(msg)
        warnings_list.append(msg)

    return warnings_list
