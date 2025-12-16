from midi_utils import midi_arp, midi_chord
from midi_utils.arp import apply_styles, _check_duration

def test_check_duration():
    assert not _check_duration(total_time=100, duration=None)
    assert _check_duration(total_time=100, duration=100)



def test_midi_arp_duration():
    chord_notes = midi_chord("C3", "min")
    notes = list(
        midi_arp(
            chord_notes,
            octaves=[1],
            duration=1000.0,
            styles=["updown"],
            beat_bpm=131,
            beat_count=1 / 16,
            note_bpm=131,
            note_count=3 / 64,
        )
    )
    assert sum(n["duration"] for n in notes) == 1000.0

def test_midi_arp_simple():
    chord_notes = midi_chord("C3", "min")
    notes = list(
        midi_arp(
            chord_notes,
            octaves=[1],
            loops=1,
            styles=["updown"],
            beat_bpm=131,
            beat_count=1 / 16,
            note_bpm=131,
            note_count=3 / 64,
        )
    )
    assert len(notes) == 20
    assert notes[0]["duration"] == 85.87786259541986
    assert notes[-1]["type"] == "silence"



def test_apply_styles_updown_shift_2():
    notes = [60, 63, 67]
    styled_notes = apply_styles(notes, ["updown", "shift_2"])
    assert styled_notes == [67, 60, 63]


def test_apply_styles_downup_shift_4():
    notes = [67, 60, 63]
    styled_notes = apply_styles(notes, ["downup", "shift_4"])
    assert styled_notes == [67, 60, 63]


def test_apply_styles_thumb_up():
    notes = [60, 63, 67, 69, 71]
    styled_notes = apply_styles(notes, ["thumb_up"])
    assert styled_notes == [60, 63, 60, 67, 60, 69, 60, 71]


def test_apply_styles_three_two():
    notes = [60, 63, 67, 69, 71, 69, 71]
    styled_notes = apply_styles(notes, ["three_two"])
    assert styled_notes == [60, 63, 67, 0, 0, 69, 71]


def test_apply_styles_two_three():
    notes = [60, 63, 67, 69, 71, 67, 69]
    styled_notes = apply_styles(notes, ["two_three"])
    assert styled_notes == [60, 63, 0, 0, 0, 67, 69]


def test_apply_styles_middle_up():
    notes = [60, 63, 67]
    styled_notes = apply_styles(notes, ["middle_up"])
    assert styled_notes == [63, 60, 63, 67]
