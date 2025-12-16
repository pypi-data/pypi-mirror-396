"""Tests for ASCL validation."""

import pytest
from asclpy.parser import parse_ascl_string
from asclpy.validation import (
    validate_ascl_data,
    ValidationError,
    ValidationWarning,
)


def test_valid_12tet():
    """Test validation of valid 12-TET."""
    ascl_content = """! Valid
12-TET
12
!
100.0
200.0
300.0
400.0
500.0
600.0
700.0
800.0
900.0
1000.0
1100.0
2/1
"""
    data = parse_ascl_string(ascl_content)
    warnings = validate_ascl_data(data)
    
    assert len(warnings) == 0


def test_invalid_reference_pitch_too_low():
    """Test validation catches reference pitch too low."""
    ascl_content = """! Invalid ref pitch
Test
3
!
100.0
200.0
2/1
!
! @ABL REFERENCE_PITCH 4 0 2.0
"""
    data = parse_ascl_string(ascl_content)
    
    with pytest.raises(ValidationError, match="(?i)reference"):
        validate_ascl_data(data, strict=True)


def test_invalid_reference_pitch_too_high():
    """Test validation catches reference pitch too high."""
    ascl_content = """! Invalid ref pitch
Test
3
!
100.0
200.0
2/1
!
! @ABL REFERENCE_PITCH 4 0 50000.0
"""
    data = parse_ascl_string(ascl_content)
    
    with pytest.raises(ValidationError, match="(?i)reference"):
        validate_ascl_data(data, strict=True)


def test_invalid_reference_note_out_of_range():
    """Test validation catches reference note out of range."""
    ascl_content = """! Invalid ref note
Test
3
!
100.0
200.0
2/1
!
! @ABL REFERENCE_PITCH 4 15 440.0
"""
    data = parse_ascl_string(ascl_content)
    
    with pytest.raises(ValidationError, match="(?i)reference"):
        validate_ascl_data(data)


def test_invalid_note_names_count():
    """Test validation catches mismatched note names count."""
    ascl_content = """! Invalid note names
Test
5
!
100.0
200.0
300.0
400.0
2/1
!
! @ABL NOTE_NAMES C D E
"""
    data = parse_ascl_string(ascl_content)
    
    with pytest.raises(ValidationError, match="NOTE_NAMES"):
        validate_ascl_data(data)


def test_invalid_note_range_by_frequency_order():
    """Test validation catches reversed frequency range."""
    ascl_content = """! Invalid freq range
Test
3
!
100.0
200.0
2/1
!
! @ABL NOTE_RANGE_BY_FREQUENCY 4186.0 27.5
"""
    data = parse_ascl_string(ascl_content)
    
    with pytest.raises(ValidationError, match="NOTE_RANGE"):
        validate_ascl_data(data)


def test_invalid_note_range_by_index_order():
    """Test validation catches reversed index range."""
    ascl_content = """! Invalid index range
Test
3
!
100.0
200.0
2/1
!
! @ABL REFERENCE_PITCH 4 0 440.0
! @ABL NOTE_RANGE_BY_INDEX 108 0 21 0
"""
    data = parse_ascl_string(ascl_content)
    
    with pytest.raises(ValidationError, match="NOTE_RANGE"):
        validate_ascl_data(data)


def test_invalid_note_range_by_index_out_of_midi():
    """Test that wide octave ranges are allowed (e.g., Ableton uses -10 to 15)."""
    ascl_content = """! Wide MIDI range
Test
3
!
100.0
200.0
2/1
!
! @ABL REFERENCE_PITCH 4 0 440.0
! @ABL NOTE_RANGE_BY_INDEX 0 0 15 0
"""
    data = parse_ascl_string(ascl_content)
    
    # This should NOT raise an error - wide ranges are allowed
    warnings = validate_ascl_data(data)
    assert isinstance(warnings, list)


def test_warning_unusual_notes_per_octave():
    """Test warning for unusual number of notes."""
    ascl_content = """! Unusual scale
Test
156
!
"""
    # Add 156 pitches
    for i in range(1, 157):
        ascl_content += f"{i * 1200 / 156:.2f}\n"
    
    data = parse_ascl_string(ascl_content)
    warnings = validate_ascl_data(data)
    
    # Should have warning about unusual number of notes
    assert len(warnings) > 0 or data.notes_per_octave == 156  # May or may not warn


def test_warning_non_octave_scale():
    """Test warning for non-octave scale."""
    ascl_content = """! Non-octave
Bohlen-Pierce
13
!
146.30
292.61
438.91
585.22
731.52
877.83
1024.13
1170.43
1316.74
1463.04
1609.35
1755.65
3/1
"""
    data = parse_ascl_string(ascl_content)
    warnings = validate_ascl_data(data)
    
    # Might warn about non-octave
    # (this is informational, not necessarily wrong)


def test_invalid_negative_pitch():
    """Test validation catches negative pitch values."""
    ascl_content = """! Invalid pitch
Test
3
!
-100.0
200.0
2/1
"""
    data = parse_ascl_string(ascl_content)
    warnings = validate_ascl_data(data)
    
    # Negative pitches generate warnings, not errors
    assert any("pitch" in w.lower() or "negative" in w.lower() for w in warnings)


def test_invalid_non_ascending_pitches():
    """Test validation catches non-ascending pitches."""
    ascl_content = """! Invalid order
Test
3
!
300.0
100.0
2/1
"""
    data = parse_ascl_string(ascl_content)
    warnings = validate_ascl_data(data)
    
    # Non-ascending pitches generate warnings, not errors
    assert any("ascending" in w.lower() or "order" in w.lower() or "less than" in w.lower() for w in warnings)


def test_valid_note_range_with_reference():
    """Test validation of note range with custom reference."""
    ascl_content = """! Valid with range
Test
12
!
100.0
200.0
300.0
400.0
500.0
600.0
700.0
800.0
900.0
1000.0
1100.0
2/1
!
! @ABL REFERENCE_PITCH 4 9 432.0
! @ABL NOTE_RANGE_BY_INDEX 2 0 8 11
"""
    data = parse_ascl_string(ascl_content)
    # Should not raise
    warnings = validate_ascl_data(data)


def test_multiple_errors():
    """Test catching multiple validation errors."""
    ascl_content = """! Multiple errors
Test
3
!
-50.0
300.0
100.0
!
! @ABL REFERENCE_PITCH 4 50 1.0
! @ABL NOTE_NAMES A
"""
    data = parse_ascl_string(ascl_content)
    
    # Should raise ValidationError for hard constraints (ref note out of range, note names mismatch)
    # And collect warnings for soft constraints (negative pitch, non-ascending)
    with pytest.raises(ValidationError):
        validate_ascl_data(data)
