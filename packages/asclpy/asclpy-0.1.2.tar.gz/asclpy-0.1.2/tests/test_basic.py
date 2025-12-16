"""
Integration tests for asclpy library.

Tests the full workflow from loading tunings to computing frequencies.
For detailed unit tests, see test_parser.py, test_validation.py, test_loader.py,
test_midi.py, and test_tuning.py.
"""

import asclpy


def test_load_tunings():
    """Test that tunings load correctly."""
    tunings = asclpy.list_tunings()
    assert len(tunings) > 100, f"Expected >100 tunings, got {len(tunings)}"


def test_12tet():
    """Test 12-TET tuning."""
    tet = asclpy.load_tuning("12_tet_edo")
    assert tet.notes_per_octave == 12
    assert abs(tet.midi_to_freq(69) - 440.0) < 0.01


def test_midi_to_freq_dict():
    """Test MIDI-to-frequency dictionary generation."""
    tet = asclpy.load_tuning("12_tet_edo")
    midi_to_freq = tet.get_midi_to_freq_dict()
    assert len(midi_to_freq) == 128
    assert all(0 <= k <= 127 for k in midi_to_freq.keys())


def test_non_octave_scale():
    """Test non-octave scale (Bohlen-Pierce)."""
    bp = asclpy.load_tuning("bohlen_pierce")
    assert bp.notes_per_octave == 13
    assert bp.octave_cents > 1200  # Non-octave scale


def test_microtonal():
    """Test microtonal historical tuning."""
    helm = asclpy.load_tuning("helmholtz_temperament")
    assert helm.notes_per_octave == 24


def test_parse_string():
    """Test parsing ASCL from string."""
    ascl_content = """! Test tuning
Test description
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
    data = asclpy.parse_ascl_string(ascl_content)
    assert data.notes_per_octave == 12
    assert len(data.pitches) == 12


def test_custom_tuning():
    """Test creating custom tuning object."""
    ascl_content = """! Custom
Custom 7-EDO tuning
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
    data = asclpy.parse_ascl_string(ascl_content)
    tuning = asclpy.Tuning(data)
    assert tuning.notes_per_octave == 7
    freq = tuning.midi_to_freq(60)
    assert freq > 0


def test_frequency_ranges():
    """Test frequency values are reasonable."""
    tet = asclpy.load_tuning("12_tet_edo")

    # MIDI 0 should be very low
    assert 8 < tet.midi_to_freq(0) < 9

    # MIDI 127 should be very high
    assert 12000 < tet.midi_to_freq(127) < 13000

    # Middle C (MIDI 60) should be around 261.63 Hz
    assert 261 < tet.midi_to_freq(60) < 262
