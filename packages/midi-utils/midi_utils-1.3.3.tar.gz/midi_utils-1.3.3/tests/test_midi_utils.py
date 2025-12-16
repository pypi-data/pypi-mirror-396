from midi_utils import midi_scale, map_to_midi_scale, sharp_to_flat
from midi_utils.utils import midi_to_freq


def test_midi_scale_simple():
    expected = [60, 62, 64]
    scale = midi_scale("C", "MAJOR", "C3", "E3")
    assert scale == expected


def test_midi_scale_root_int():
    expected = [60, 62, 64]
    scale = midi_scale(0, "MAJOR", "C3", "E3")
    assert scale == expected


def test_midi_scale_min_max_int():
    expected = [60, 62, 64]
    scale = midi_scale(0, "MAJOR", 60, 64)
    assert scale == expected


def test_midi_scale_int_list():
    expected = [60, 62, 64]
    scale = midi_scale(0, [0, 2, 4], 60, 64)
    assert scale == expected


def test_map_to_midi_scale_low():
    expected = 60
    scale = midi_scale("C", "MAJOR", "C3", "E3")
    note = map_to_midi_scale(0, scale, 0, 100)
    assert expected == note


def test_map_to_midi_scale_mid():
    expected = 62
    scale = midi_scale("C", "MAJOR", "C3", "E3")
    note = map_to_midi_scale(49, scale, 0, 100)
    assert expected == note


def test_map_to_midi_scale_max():
    expected = 64
    scale = midi_scale("C", "MAJOR", "C3", "E3")
    note = map_to_midi_scale(99, scale, 0, 100)
    assert expected == note


def test_sharp_to_flat():
    assert sharp_to_flat("C#3") == "DB3"
    assert sharp_to_flat("A#") == "BB"


def test_midi_to_freq():
    assert midi_to_freq(84) == 1046.5
