"""Tests for ASCL parser."""

import pytest
from pathlib import Path
from asclpy.parser import parse_ascl_file, parse_ascl_string, AsclData, Pitch


def test_parse_12tet():
    """Test parsing 12-TET from file."""
    from asclpy.loader import load_tuning
    tuning = load_tuning("12_tet_edo")
    
    assert tuning.notes_per_octave == 12
    assert len(tuning.pitches_cents) == 13  # includes 0.0
    assert "12 tone equal temperament" in tuning.description.lower()


def test_parse_string():
    """Test parsing ASCL from string."""
    ascl_content = """! Test tuning
Test description with unicode: äöü
7
!
171.43
342.86
514.29
685.71
857.14
1028.57
2/1
"""
    data = parse_ascl_string(ascl_content)
    
    assert data.notes_per_octave == 7
    assert len(data.pitches) == 7
    assert "unicode" in data.description


def test_parse_cents():
    """Test parsing cents values."""
    ascl_content = """! Cents test
Cents only
3
!
100.0
400.5
2/1
"""
    data = parse_ascl_string(ascl_content)
    
    assert len(data.pitches) == 3
    assert abs(data.pitches[0].value - 100.0) < 0.01
    assert abs(data.pitches[1].value - 400.5) < 0.01
    assert abs(data.pitches[2].value - 1200.0) < 0.01


def test_parse_ratios():
    """Test parsing ratio values."""
    ascl_content = """! Ratio test
Ratios only
4
!
9/8
5/4
3/2
2/1
"""
    data = parse_ascl_string(ascl_content)
    
    assert len(data.pitches) == 4
    # 9/8 = 203.91 cents
    assert 203 < data.pitches[0].value < 204
    # 5/4 = 386.31 cents
    assert 386 < data.pitches[1].value < 387
    # 3/2 = 701.96 cents
    assert 701 < data.pitches[2].value < 702


def test_parse_mixed():
    """Test parsing mixed cents and ratios."""
    ascl_content = """! Mixed test
Mix of formats
4
!
100.0
9/8
400.0
2/1
"""
    data = parse_ascl_string(ascl_content)
    
    assert len(data.pitches) == 4
    assert abs(data.pitches[0].value - 100.0) < 0.01
    assert 203 < data.pitches[1].value < 204
    assert abs(data.pitches[2].value - 400.0) < 0.01


def test_parse_with_comments():
    """Test parsing with comments."""
    ascl_content = """! Comment test
Description line
3
!
100.0  ! First pitch
200.0  ! Second pitch (comment with special chars: 你好)
2/1    ! Octave
"""
    data = parse_ascl_string(ascl_content)
    
    assert len(data.pitches) == 3
    assert abs(data.pitches[0].value - 100.0) < 0.01


def test_parse_abl_reference_pitch():
    """Test parsing @ABL REFERENCE_PITCH directive."""
    ascl_content = """! Reference test
Test tuning
3
!
100.0
200.0
2/1
!
! @ABL REFERENCE_PITCH 4 2 432.0
"""
    data = parse_ascl_string(ascl_content)
    
    assert data.reference_pitch is not None
    assert data.reference_pitch.frequency == 432.0
    assert data.reference_pitch.note_index == 2
    assert data.reference_pitch.octave == 4


def test_parse_abl_note_names():
    """Test parsing @ABL NOTE_NAMES directive."""
    ascl_content = """! Note names test
Test tuning
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
! @ABL NOTE_NAMES C C# D D# E F F# G G# A A# B
"""
    data = parse_ascl_string(ascl_content)
    
    assert len(data.note_names) == 12
    assert data.note_names[0] == "C"
    assert data.note_names[9] == "A"


def test_parse_abl_note_range_by_frequency():
    """Test parsing @ABL NOTE_RANGE_BY_FREQUENCY directive."""
    ascl_content = """! Freq range test
Test tuning
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
! @ABL NOTE_RANGE_BY_FREQUENCY 27.5 4186.0
"""
    data = parse_ascl_string(ascl_content)
    
    assert data.note_range is not None
    assert data.note_range.min_freq == 27.5
    assert data.note_range.max_freq == 4186.0


def test_parse_abl_note_range_by_index():
    """Test parsing @ABL NOTE_RANGE_BY_INDEX directive."""
    ascl_content = """! Index range test
Test tuning
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
! @ABL NOTE_RANGE_BY_INDEX 21 108
"""
    data = parse_ascl_string(ascl_content)
    
    assert data.note_range is not None
    assert data.note_range.min_octave == 21
    assert data.note_range.min_index == 108


def test_parse_abl_source_and_link():
    """Test parsing @ABL SOURCE and LINK directives."""
    ascl_content = """! Metadata test
Test tuning
3
!
100.0
200.0
2/1
!
! @ABL SOURCE "Scala Archive"
! @ABL LINK "https://example.com/tuning"
"""
    data = parse_ascl_string(ascl_content)
    
    assert data.source == "Scala Archive"
    assert data.link == "https://example.com/tuning"


def test_parse_non_octave_scale():
    """Test parsing non-octave scale (Bohlen-Pierce)."""
    from asclpy.loader import load_tuning
    tuning = load_tuning("bohlen_pierce")
    
    assert tuning.notes_per_octave == 13
    # Last pitch should be 3/1 (1901.96 cents)
    assert tuning.octave_cents > 1200


def test_pitch_from_string():
    """Test Pitch.from_string() method."""
    # Cents
    p1 = Pitch.from_string("100.5")
    assert abs(p1.value - 100.5) < 0.01
    
    # Ratio
    p2 = Pitch.from_string("3/2")
    assert 701 < p2.value < 702
    
    # With comment
    p3 = Pitch.from_string("200.0  ! comment")
    assert abs(p3.value - 200.0) < 0.01


def test_malformed_pitch():
    """Test handling of malformed pitch values."""
    # Should not crash, might return 0 or skip
    try:
        p = Pitch.from_string("invalid")
        assert p.value >= 0  # Should handle gracefully
    except ValueError:
        pass  # Also acceptable


def test_quoted_directive_args():
    """Test parsing directives with quoted arguments."""
    ascl_content = """! Quoted test
Test tuning
3
!
100.0
200.0
2/1
!
! @ABL SOURCE "Source with spaces"
! @ABL LINK "http://example.com/path with spaces"
! @ABL NOTE_NAMES "C sharp" "D flat" E
"""
    data = parse_ascl_string(ascl_content)
    
    assert data.source == "Source with spaces"
    assert data.link == "http://example.com/path with spaces"
    assert len(data.note_names) == 3
    assert data.note_names[0] == "C sharp"


def test_empty_lines_and_whitespace():
    """Test handling of empty lines and extra whitespace."""
    ascl_content = """! Whitespace test
Test tuning

3

!

100.0

200.0

2/1
"""
    data = parse_ascl_string(ascl_content)
    
    assert data.notes_per_octave == 3
    assert len(data.pitches) == 3
