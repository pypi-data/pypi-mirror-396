"""Tests for midi_to_freq with tuning support."""

import pytest
from midi_utils import midi_to_freq


def test_midi_to_freq_default_tuning():
    """Test midi_to_freq with default 12-TET tuning for backwards compatibility."""
    # A4 should be 440 Hz in standard tuning
    assert midi_to_freq(69) == 440.0

    # C4 (middle C) in standard tuning
    freq_c4 = midi_to_freq(60)
    assert abs(freq_c4 - 261.63) < 0.01


def test_midi_to_freq_alternative_tuning():
    """Test midi_to_freq with alternative tuning systems."""
    # Test with 19-EDO (19-tone equal temperament)
    freq_19edo = midi_to_freq(69, tuning="19_edo")
    assert isinstance(freq_19edo, float)
    assert freq_19edo > 0

    # Test with 31-EDO (31-tone equal temperament)
    freq_31edo = midi_to_freq(60, tuning="31_edo")
    assert isinstance(freq_31edo, float)
    assert freq_31edo > 0

    # Test with 12-TET from asclpy (should match default)
    freq_12tet_asclpy = midi_to_freq(69, tuning="12_tet_edo")
    assert abs(freq_12tet_asclpy - 440.0) < 0.01

    # Frequencies should differ from 12-TET for most notes in alternative tunings
    freq_12tet = midi_to_freq(62)  # D4 in standard tuning
    freq_19edo_d = midi_to_freq(62, tuning="19_edo")
    # In 19-EDO, note spacing is different from 12-TET
    assert freq_12tet != freq_19edo_d


def test_midi_to_freq_invalid_tuning():
    """Test midi_to_freq raises appropriate error for unsupported tuning."""
    with pytest.raises(ValueError) as exc_info:
        midi_to_freq(69, tuning="nonexistent_tuning_system")

    error_msg = str(exc_info.value)
    assert "Unsupported tuning" in error_msg
    assert "nonexistent_tuning_system" in error_msg
    assert "github.com/gltd/asclpy" in error_msg
