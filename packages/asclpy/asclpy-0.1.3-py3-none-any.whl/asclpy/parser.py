"""
Parser for .ascl (Ableton Scala) tuning files.

ASCL is an Ableton-specific extension to the SCL (Scala) file format.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union


@dataclass
class Pitch:
    """Represents a pitch definition in cents or as a ratio."""

    value: float  # in cents
    original: str  # original string representation

    @classmethod
    def from_string(cls, s: str) -> "Pitch":
        """Parse a pitch from a string (cents or ratio)."""
        s = s.strip()

        # Extract just the first part (before any whitespace/comments)
        first_part = s.split()[0] if s else s

        # Check if it's a ratio (contains /)
        if "/" in first_part:
            try:
                numerator, denominator = first_part.split("/")
                ratio = float(numerator) / float(denominator)
                # Convert ratio to cents: cents = 1200 * log2(ratio)
                import math

                cents = 1200.0 * math.log2(ratio) if ratio > 0 else 0.0
                return cls(value=cents, original=s)
            except (ValueError, ZeroDivisionError) as e:
                raise ValueError(f"Invalid ratio format: {s}") from e
        else:
            # It's in cents - extract just the numeric part
            try:
                # Handle malformed values like "267.4.39999" by trying to fix them
                if first_part.count(".") > 1:
                    # Multiple decimal points - likely a typo, keep first occurrence
                    parts = first_part.split(".")
                    first_part = f"{parts[0]}.{parts[1]}"
                cents = float(first_part)
                return cls(value=cents, original=s)
            except (ValueError, IndexError) as e:
                raise ValueError(f"Invalid cents format: {s}") from e


@dataclass
class ReferencePitch:
    """Represents an @ABL REFERENCE_PITCH directive."""

    octave: int  # -2 to 8
    note_index: int  # 0-indexed within octave
    frequency: float  # in Hz


@dataclass
class NoteRange:
    """Represents note range constraints."""

    # For frequency-based range
    min_freq: Optional[float] = None
    max_freq: Optional[float] = None

    # For index-based range
    min_octave: Optional[int] = None
    min_index: Optional[int] = None
    max_octave: Optional[int] = None
    max_index: Optional[int] = None


@dataclass
class AsclData:
    """Parsed data from an .ascl file."""

    description: str
    notes_per_octave: int
    pitches: List[Pitch]  # Does NOT include the implied 0-cent first pitch

    # Ableton extensions
    reference_pitch: Optional[ReferencePitch] = None
    note_names: Optional[List[str]] = None
    note_range: Optional[NoteRange] = None
    source: Optional[str] = None
    link: Optional[str] = None

    # Validation warnings
    validation_warnings: List[str] = None


def parse_ascl_string(content: str) -> AsclData:
    """
    Parse .ascl file content into structured data.

    Args:
        content: String content of an .ascl file

    Returns:
        AsclData object with parsed tuning information

    Raises:
        ValueError: If the file format is invalid
    """
    lines = content.splitlines()

    if not lines:
        raise ValueError("Empty file")

    # Parse description (first non-comment line)
    description = ""
    line_idx = 0
    while line_idx < len(lines):
        line = lines[line_idx].strip()
        if line and not line.startswith("!"):
            description = line
            line_idx += 1
            break
        line_idx += 1

    if not description:
        raise ValueError("Missing description line")

    # Parse notes per octave (next non-comment line)
    notes_per_octave = None
    while line_idx < len(lines):
        line = lines[line_idx].strip()
        if line and not line.startswith("!"):
            try:
                notes_per_octave = int(line)
                line_idx += 1
                break
            except ValueError as e:
                raise ValueError(f"Invalid notes per octave: {line}") from e
        line_idx += 1

    if notes_per_octave is None:
        raise ValueError("Missing notes per octave")

    # Parse pitch definitions
    pitches: List[Pitch] = []
    while line_idx < len(lines) and len(pitches) < notes_per_octave:
        line = lines[line_idx].strip()
        line_idx += 1

        if not line or line.startswith("!"):
            continue

        # Remove inline comments
        if "!" in line:
            line = line.split("!", 1)[0].strip()

        if line:
            try:
                pitch = Pitch.from_string(line)
                pitches.append(pitch)
            except ValueError as e:
                raise ValueError(f"Invalid pitch definition: {line}") from e

    if len(pitches) != notes_per_octave:
        raise ValueError(
            f"Expected {notes_per_octave} pitch definitions, found {len(pitches)}"
        )

    # Parse Ableton extensions (from remaining comment lines)
    reference_pitch = None
    note_names = None
    note_range = None
    source = None
    link = None

    for line in lines[line_idx:]:
        line = line.strip()
        if not line.startswith("!"):
            continue

        # Remove leading ! and whitespace
        line = line[1:].strip()

        if not line.startswith("@ABL"):
            continue

        # Parse ABL directive
        line = line[4:].strip()  # Remove @ABL

        # Split by spaces, respecting quotes
        parts = _split_with_quotes(line)

        if not parts:
            continue

        directive = parts[0]
        args = parts[1:]

        try:
            if directive == "REFERENCE_PITCH":
                if len(args) != 3:
                    raise ValueError(
                        f"REFERENCE_PITCH requires 3 arguments, got {len(args)}"
                    )
                reference_pitch = ReferencePitch(
                    octave=int(args[0]),
                    note_index=int(args[1]),
                    frequency=float(args[2]),
                )

            elif directive == "NOTE_NAMES":
                note_names = args

            elif directive == "NOTE_RANGE_BY_FREQUENCY":
                if len(args) < 1 or len(args) > 2:
                    raise ValueError("NOTE_RANGE_BY_FREQUENCY requires 1-2 arguments")
                note_range = NoteRange(
                    min_freq=float(args[0]),
                    max_freq=float(args[1]) if len(args) > 1 else None,
                )

            elif directive == "NOTE_RANGE_BY_INDEX":
                if len(args) < 2 or len(args) > 4:
                    raise ValueError("NOTE_RANGE_BY_INDEX requires 2-4 arguments")
                note_range = NoteRange(
                    min_octave=int(args[0]),
                    min_index=int(args[1]),
                    max_octave=int(args[2]) if len(args) > 2 else None,
                    max_index=int(args[3]) if len(args) > 3 else None,
                )

            elif directive == "SOURCE":
                source = " ".join(args)

            elif directive == "LINK":
                link = args[0] if args else None

        except (ValueError, IndexError) as e:
            # Graceful error handling - log but don't fail
            import warnings

            warnings.warn(f"Failed to parse ABL directive '{directive}': {e}")

    return AsclData(
        description=description,
        notes_per_octave=notes_per_octave,
        pitches=pitches,
        reference_pitch=reference_pitch,
        note_names=note_names,
        note_range=note_range,
        source=source,
        link=link,
    )


def parse_ascl_file(filepath: Union[str, Path]) -> AsclData:
    """
    Parse an .ascl file.

    Args:
        filepath: Path to the .ascl file

    Returns:
        AsclData object with parsed tuning information
    """
    filepath = Path(filepath)

    try:
        content = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"File must be UTF-8 encoded: {filepath}") from e

    return parse_ascl_string(content)


def _split_with_quotes(s: str) -> List[str]:
    """
    Split a string by spaces, respecting double-quoted segments.

    Example:
        'A B "C D" E' -> ['A', 'B', 'C D', 'E']
    """
    parts = []
    current = []
    in_quotes = False

    for char in s:
        if char == '"':
            in_quotes = not in_quotes
        elif char == " " and not in_quotes:
            if current:
                parts.append("".join(current))
                current = []
        else:
            current.append(char)

    if current:
        parts.append("".join(current))

    return parts
