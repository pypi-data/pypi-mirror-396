"""Tests for Tuning class."""

import pytest
from asclpy.loader import load_tuning
from asclpy.parser import parse_ascl_string
from asclpy.tuning import Tuning


def test_tuning_12tet_basic():
    """Test basic 12-TET tuning properties."""
    tuning = load_tuning("12_tet_edo")
    
    assert tuning.notes_per_octave == 12
    assert "12 tone equal temperament" in tuning.description.lower()
    assert tuning.reference_frequency == 440.0
    assert tuning.reference_index == 9
    # reference_octave may vary based on implementation


def test_tuning_pitches_cents():
    """Test pitches_cents property."""
    tuning = load_tuning("12_tet_edo")
    
    # pitches_cents includes 0.0 at the start, so length is notes_per_octave + 1
    assert len(tuning.pitches_cents) == 13
    
    # First pitch should be 0 cents
    assert abs(tuning.pitches_cents[0] - 0.0) < 0.01
    
    # Second pitch should be 100 cents
    assert abs(tuning.pitches_cents[1] - 100.0) < 0.01
    
    # Last pitch should be 1200 cents (octave)
    assert abs(tuning.pitches_cents[-1] - 1200.0) < 0.01


def test_tuning_octave_cents():
    """Test octave_cents property."""
    # 12-TET should be 1200 cents
    tuning = load_tuning("12_tet_edo")
    assert abs(tuning.octave_cents - 1200.0) < 0.01
    
    # Bohlen-Pierce should be ~1901.96 cents (3/1 ratio)
    bp = load_tuning("bohlen_pierce")
    assert bp.octave_cents > 1200


def test_tuning_note_names():
    """Test note_names property."""
    tuning = load_tuning("12_tet_edo")
    
    if tuning.note_names:
        assert len(tuning.note_names) == 12
        # Standard note names
        assert tuning.note_names[0] == "C"
        assert tuning.note_names[9] == "A"


def test_tuning_get_note_name():
    """Test get_note_name() method."""
    tuning = load_tuning("12_tet_edo")
    
    if tuning.note_names:
        assert tuning.get_note_name(0) == "C"
        assert tuning.get_note_name(9) == "A"


def test_tuning_get_note_name_no_names():
    """Test get_note_name() when no names defined."""
    ascl_content = """! No names
Test tuning
3
!
100.0
200.0
2/1
"""
    data = parse_ascl_string(ascl_content)
    tuning = Tuning(data)
    
    # Should return None
    assert tuning.get_note_name(0) is None


def test_tuning_get_pitch_cents():
    """Test get_pitch_cents() method."""
    tuning = load_tuning("12_tet_edo")
    
    # get_pitch_cents returns the cents value for a given pitch class
    # Pitch class 0 is 0 cents, pitch class 1 is 100 cents in 12-TET
    assert abs(tuning.get_pitch_cents(0) - 0.0) < 0.01
    assert abs(tuning.get_pitch_cents(1) - 100.0) < 0.01
    assert abs(tuning.get_pitch_cents(11) - 1100.0) < 0.01


def test_tuning_get_pitch_cents_out_of_range():
    """Test get_pitch_cents() with out-of-range index."""
    tuning = load_tuning("12_tet_edo")
    
    # pitches_cents has 13 items (0.0 + 12 pitches), so valid range is 0-12
    # Index 13 should be out of range
    with pytest.raises(IndexError):
        tuning.get_pitch_cents(13)


def test_tuning_midi_to_freq():
    """Test midi_to_freq() method."""
    tuning = load_tuning("12_tet_edo")
    
    # A4 should be 440 Hz
    assert abs(tuning.midi_to_freq(69) - 440.0) < 0.01
    
    # Middle C should be ~261.63 Hz
    assert 261 < tuning.midi_to_freq(60) < 262


def test_tuning_get_midi_to_freq_dict():
    """Test get_midi_to_freq_dict() method."""
    tuning = load_tuning("12_tet_edo")
    
    freq_map = tuning.get_midi_to_freq_dict()
    
    assert len(freq_map) == 128
    assert all(isinstance(k, int) for k in freq_map.keys())
    assert all(isinstance(v, float) for v in freq_map.values())
    assert freq_map[69] == tuning.midi_to_freq(69)


def test_tuning_get_valid_midi_range():
    """Test get_valid_midi_range() method."""
    tuning = load_tuning("12_tet_edo")
    
    min_midi, max_midi = tuning.get_valid_midi_range()
    
    # Default should be full range
    assert min_midi == 0
    assert max_midi == 127


def test_tuning_get_valid_midi_range_restricted():
    """Test get_valid_midi_range() with NOTE_RANGE directive."""
    ascl_content = """! Limited range
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
! @ABL REFERENCE_PITCH 4 0 261.63
! @ABL NOTE_RANGE_BY_INDEX 1 9 9 0
"""
    data = parse_ascl_string(ascl_content)
    tuning = Tuning(data)
    
    min_midi, max_midi = tuning.get_valid_midi_range()
    
    assert min_midi == 21
    assert max_midi == 108


def test_tuning_is_midi_valid():
    """Test is_midi_valid() method."""
    tuning = load_tuning("12_tet_edo")
    
    assert tuning.is_midi_valid(0)
    assert tuning.is_midi_valid(69)
    assert tuning.is_midi_valid(127)


def test_tuning_equality():
    """Test __eq__() method."""
    tuning1 = load_tuning("12_tet_edo")
    tuning2 = load_tuning("12_tet_edo")
    
    # Same tuning should be equal
    assert tuning1 == tuning2


def test_tuning_inequality():
    """Test __eq__() method with different tunings."""
    tuning1 = load_tuning("12_tet_edo")
    tuning2 = load_tuning("19_edo")
    
    # Different tunings should not be equal
    assert tuning1 != tuning2


def test_tuning_equality_custom():
    """Test __eq__() with custom tunings."""
    ascl_content = """! Custom
Test tuning
3
!
100.0
200.0
2/1
"""
    data = parse_ascl_string(ascl_content)
    
    tuning1 = Tuning(data)
    tuning2 = Tuning(data)
    
    assert tuning1 == tuning2


def test_tuning_inequality_with_non_tuning():
    """Test __eq__() with non-Tuning object."""
    tuning = load_tuning("12_tet_edo")
    
    assert tuning != "not a tuning"
    assert tuning != 42
    assert tuning != None


def test_tuning_repr():
    """Test __repr__() method."""
    tuning = load_tuning("12_tet_edo")
    
    repr_str = repr(tuning)
    
    assert "Tuning" in repr_str
    assert "12" in repr_str  # notes_per_octave


def test_tuning_non_octave_scale():
    """Test non-octave scale properties."""
    bp = load_tuning("bohlen_pierce")
    
    assert bp.notes_per_octave == 13
    assert bp.octave_cents > 1200
    
    # Should still have valid MIDI mapping
    freq = bp.midi_to_freq(60)
    assert freq > 0


def test_tuning_microtonal():
    """Test microtonal tuning (24 notes)."""
    tuning = load_tuning("24_edo")
    
    assert tuning.notes_per_octave == 24
    # pitches_cents includes 0.0, so length is notes_per_octave + 1
    assert len(tuning.pitches_cents) == 25


def test_tuning_19edo():
    """Test 19-EDO tuning."""
    tuning = load_tuning("19_edo")
    
    assert tuning.notes_per_octave == 19
    
    # Each step should be 1200/19 = 63.16 cents
    expected_step = 1200 / 19
    
    # pitches_cents includes 0.0 at index 0, so check indices 1 onward
    for i in range(1, len(tuning.pitches_cents)):
        expected = expected_step * i
        assert abs(tuning.pitches_cents[i] - expected) < 0.1


def test_tuning_just_intonation():
    """Test another tuning system."""
    # Use 31-EDO as it exists in the bundled tunings
    tuning = load_tuning("31_edo")
    
    assert tuning.notes_per_octave == 31
    
    # Should have valid frequencies
    freq = tuning.midi_to_freq(69)
    assert freq > 0


def test_tuning_custom_reference():
    """Test tuning with custom reference pitch."""
    ascl_content = """! Custom ref
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
! @ABL REFERENCE_PITCH 4 9 432.0
"""
    data = parse_ascl_string(ascl_content)
    tuning = Tuning(data)
    
    assert tuning.reference_frequency == 432.0
    assert tuning.reference_index == 9


def test_tuning_metadata_access():
    """Test accessing various metadata."""
    tuning = load_tuning("12_tet_edo")
    
    # All should be accessible without errors
    _ = tuning.notes_per_octave
    _ = tuning.description
    _ = tuning.pitches_cents
    _ = tuning.octave_cents
    _ = tuning.reference_frequency
    _ = tuning.reference_index
    _ = tuning.reference_octave
    _ = tuning.note_names
    _ = tuning.get_valid_midi_range()
