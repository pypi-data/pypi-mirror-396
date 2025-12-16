from midi_utils import midi_chord


def test_midi_chord_str():
    chord = midi_chord("C3", "min")
    assert chord == [60, 63, 67]


def test_midi_chord_int():
    chord = midi_chord(60, "min")
    assert chord == [60, 63, 67]


def test_midi_chord_inversion():
    chord = midi_chord(60, "min", inversions=[0, -1, 0])
    assert chord == [51, 60, 67]


def test_midi_chord_stack_up():
    chord = midi_chord(60, "min", stack=1)
    assert chord == [60, 63, 67, 72, 75, 79]


def test_midi_chord_stack_down():
    chord = midi_chord(60, "min", stack=-1)
    assert chord == [48, 51, 55, 60, 63, 67]
