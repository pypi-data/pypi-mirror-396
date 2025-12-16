"""Tests for MIDI mapping functionality."""

import pytest
import math
from asclpy.parser import parse_ascl_string
from asclpy.midi import MidiMapper
from asclpy.loader import load_tuning


def test_midi_mapper_12tet():
    """Test MIDI mapping for 12-TET."""
    tuning = load_tuning("12_tet_edo")
    
    # A4 (MIDI 69) should be 440 Hz
    assert abs(tuning.midi_to_freq(69) - 440.0) < 0.01
    
    # Middle C (MIDI 60) should be ~261.63 Hz
    freq_c4 = tuning.midi_to_freq(60)
    assert 261 < freq_c4 < 262
    
    # C5 (MIDI 72) should be ~523.25 Hz (octave above middle C)
    freq_c5 = tuning.midi_to_freq(72)
    assert 523 < freq_c5 < 524


def test_midi_mapper_frequency_doubling():
    """Test that frequencies double each octave."""
    tuning = load_tuning("12_tet_edo")
    
    # Test octave doubling
    for midi in [24, 36, 48, 60, 72, 84, 96]:
        freq = tuning.midi_to_freq(midi)
        freq_octave_up = tuning.midi_to_freq(midi + 12)
        
        # Should be approximately 2x
        ratio = freq_octave_up / freq
        assert abs(ratio - 2.0) < 0.001


def test_midi_mapper_19edo():
    """Test MIDI mapping for 19-EDO."""
    tuning = load_tuning("19_edo")
    
    # Reference should still be 440 Hz
    # For 19-EDO, reference is at index 11 (A)
    
    # Test that all valid MIDI notes have valid frequencies
    min_midi, max_midi = tuning.get_valid_midi_range()
    for midi in range(min_midi, max_midi + 1):
        freq = tuning.midi_to_freq(midi)
        assert freq > 0
        assert freq < 20000  # Audible range


def test_midi_mapper_bohlen_pierce():
    """Test MIDI mapping for non-octave scale (Bohlen-Pierce)."""
    tuning = load_tuning("bohlen_pierce")
    
    # BP has 13 notes per tritave (3:1 ratio)
    # Test that 13 notes up is ~3x frequency
    freq_base = tuning.midi_to_freq(60)
    freq_tritave = tuning.midi_to_freq(60 + 13)
    
    ratio = freq_tritave / freq_base
    # Should be close to 3.0 (tritave)
    assert 2.9 < ratio < 3.1


def test_midi_mapper_custom_reference_pitch():
    """Test MIDI mapping with custom reference pitch."""
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
    from asclpy.parser import parse_ascl_string
    from asclpy.tuning import Tuning
    
    data = parse_ascl_string(ascl_content)
    tuning = Tuning(data)
    
    # A (index 9) should be 432 Hz
    # In MIDI, if middle octave is 5, A4 would be MIDI 69
    # But we need to figure out which MIDI note corresponds to index 9
    freq_map = tuning.get_midi_to_freq_dict()
    
    # Find MIDI note that should be 432 Hz
    # For 12-note scale with reference at index 9, octave 4 (MIDI 60-71)
    # Index 9 in that octave would be MIDI 69
    assert abs(freq_map[69] - 432.0) < 0.01


def test_midi_mapper_range_by_frequency():
    """Test MIDI mapping with NOTE_RANGE_BY_FREQUENCY."""
    ascl_content = """! Freq range
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
! @ABL NOTE_RANGE_BY_FREQUENCY 100.0 1000.0
"""
    from asclpy.parser import parse_ascl_string
    from asclpy.tuning import Tuning
    
    data = parse_ascl_string(ascl_content)
    tuning = Tuning(data)
    
    min_midi, max_midi = tuning.get_valid_midi_range()
    
    # Check that the frequency range is respected
    freq_min = tuning.midi_to_freq(min_midi)
    freq_max = tuning.midi_to_freq(max_midi)
    
    assert freq_min >= 100.0
    assert freq_max <= 1000.0


def test_midi_mapper_range_by_index():
    """Test MIDI mapping with NOTE_RANGE_BY_INDEX."""
    ascl_content = """! Index range
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
    from asclpy.parser import parse_ascl_string
    from asclpy.tuning import Tuning
    
    data = parse_ascl_string(ascl_content)
    tuning = Tuning(data)
    
    min_midi, max_midi = tuning.get_valid_midi_range()
    
    assert min_midi == 21
    assert max_midi == 108


def test_midi_mapper_full_range():
    """Test MIDI mapping for full 0-127 range."""
    tuning = load_tuning("12_tet_edo")
    
    freq_map = tuning.get_midi_to_freq_dict()
    
    assert len(freq_map) == 128
    assert all(0 <= midi <= 127 for midi in freq_map.keys())
    
    # Test extremes
    # MIDI 0 (C-1) should be ~8.18 Hz
    assert 8 < freq_map[0] < 9
    
    # MIDI 127 (G9) should be ~12543 Hz
    assert 12000 < freq_map[127] < 13000


def test_midi_mapper_semitone_spacing():
    """Test that semitones are properly spaced in 12-TET."""
    tuning = load_tuning("12_tet_edo")
    
    # Each semitone should be 2^(1/12) ≈ 1.05946
    expected_ratio = 2 ** (1/12)
    
    for midi in range(60, 72):
        freq1 = tuning.midi_to_freq(midi)
        freq2 = tuning.midi_to_freq(midi + 1)
        ratio = freq2 / freq1
        
        assert abs(ratio - expected_ratio) < 0.0001


def test_midi_mapper_negative_midi():
    """Test that negative MIDI numbers are clamped to valid range."""
    tuning = load_tuning("12_tet_edo")
    
    # MIDI mapper validates range [0, 127]
    # Negative MIDI should raise ValueError
    with pytest.raises(ValueError, match="MIDI"):
        tuning.midi_to_freq(-12)


def test_midi_mapper_above_127():
    """Test that MIDI numbers above 127 are clamped to valid range."""
    tuning = load_tuning("12_tet_edo")
    
    # MIDI mapper validates range [0, 127]
    # MIDI > 127 should raise ValueError
    with pytest.raises(ValueError, match="MIDI"):
        tuning.midi_to_freq(140)


def test_is_midi_valid():
    """Test is_midi_valid() method."""
    # 12-TET has full range
    tuning = load_tuning("12_tet_edo")
    assert tuning.is_midi_valid(0)
    assert tuning.is_midi_valid(69)
    assert tuning.is_midi_valid(127)


def test_is_midi_valid_with_range():
    """Test is_midi_valid() with restricted range."""
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
    from asclpy.parser import parse_ascl_string
    from asclpy.tuning import Tuning
    
    data = parse_ascl_string(ascl_content)
    tuning = Tuning(data)
    
    assert not tuning.is_midi_valid(0)
    assert not tuning.is_midi_valid(20)
    assert tuning.is_midi_valid(21)
    assert tuning.is_midi_valid(69)
    assert tuning.is_midi_valid(108)
    assert not tuning.is_midi_valid(109)
    assert not tuning.is_midi_valid(127)
