"""Tests for tuning loader and registry."""

import pytest
from asclpy.loader import TuningRegistry, get_default_registry, load_tuning, list_tunings
from asclpy.parser import parse_ascl_string


def test_default_registry_loads_tunings():
    """Test that default registry loads bundled tunings."""
    registry = get_default_registry()
    tunings = registry.list()
    
    assert len(tunings) > 100
    assert "12_tet_edo" in tunings
    assert "bohlen_pierce" in tunings


def test_list_tunings_function():
    """Test list_tunings() convenience function."""
    tunings = list_tunings()
    
    assert len(tunings) > 100
    assert isinstance(tunings, list)
    assert all(isinstance(name, str) for name in tunings)


def test_load_tuning_function():
    """Test load_tuning() convenience function."""
    tuning = load_tuning("12_tet_edo")
    
    assert tuning.notes_per_octave == 12
    assert "12 tone equal temperament" in tuning.description.lower()


def test_registry_load_existing():
    """Test loading existing tuning from registry."""
    registry = get_default_registry()
    tuning = registry.load("12_tet_edo")
    
    assert tuning is not None
    assert tuning.notes_per_octave == 12


def test_registry_load_nonexistent():
    """Test loading non-existent tuning raises error."""
    registry = get_default_registry()
    
    with pytest.raises(KeyError):
        registry.load("nonexistent_tuning")


def test_registry_caching():
    """Test that registry caches loaded tunings."""
    registry = get_default_registry()
    
    tuning1 = registry.load("12_tet_edo")
    tuning2 = registry.load("12_tet_edo")
    
    # Should be the same object (cached)
    assert tuning1 is tuning2


# Removed test_registry_get_with_cache - TuningRegistry doesn't have .get() method


# Removed test_registry_get_not_loaded - TuningRegistry doesn't have .get() method


def test_registry_register_custom():
    """Test registering custom tuning."""
    registry = TuningRegistry()
    
    ascl_content = """! Custom
Custom 7-EDO
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
    registry.register("custom_7edo", data)
    
    assert "custom_7edo" in registry.list()
    tuning = registry.load("custom_7edo")
    assert tuning.notes_per_octave == 7


def test_registry_register_overwrites():
    """Test that register overwrites existing entry."""
    registry = TuningRegistry()
    
    # Register first version
    ascl_v1 = """! V1
Version 1
3
!
100.0
200.0
2/1
"""
    data_v1 = parse_ascl_string(ascl_v1)
    registry.register("test", data_v1)
    
    tuning_v1 = registry.load("test")
    assert tuning_v1.notes_per_octave == 3
    
    # Register second version (overwrite)
    ascl_v2 = """! V2
Version 2
5
!
100.0
200.0
300.0
400.0
2/1
"""
    data_v2 = parse_ascl_string(ascl_v2)
    registry.register("test", data_v2)
    
    tuning_v2 = registry.load("test")
    assert tuning_v2.notes_per_octave == 5


def test_empty_registry():
    """Test empty registry."""
    registry = TuningRegistry(auto_load=False)
    
    assert len(registry.list()) == 0


def test_registry_loads_from_package():
    """Test that registry loads from bundled tunings."""
    registry = get_default_registry()
    tunings = registry.list()
    
    # Test various categories exist
    assert "12_tet_edo" in tunings  # EDO
    assert "19_edo" in tunings  # Another EDO
    assert "bohlen_pierce" in tunings  # Non-octave
    assert any("maqam" in t for t in tunings)  # Arabic Maqam category
    assert len(tunings) > 100  # Should have many tunings


def test_tuning_names_are_snake_case():
    """Test that all tuning names use snake_case."""
    tunings = list_tunings()
    
    for name in tunings:
        # Should be lowercase with underscores
        assert name.islower() or "_" in name
        assert " " not in name
        assert "-" not in name or name.startswith("_")  # Allow in private names


def test_load_multiple_tunings():
    """Test loading multiple different tunings."""
    tunings_to_test = [
        "12_tet_edo",
        "19_edo",
        "31_edo",
        "bohlen_pierce",
    ]
    
    for name in tunings_to_test:
        tuning = load_tuning(name)
        assert tuning is not None
        assert tuning.notes_per_octave > 0


def test_registry_list_is_sorted():
    """Test that registry.list() returns sorted names."""
    tunings = list_tunings()
    
    assert tunings == sorted(tunings)


def test_singleton_registry():
    """Test that get_default_registry() returns singleton."""
    registry1 = get_default_registry()
    registry2 = get_default_registry()
    
    assert registry1 is registry2
