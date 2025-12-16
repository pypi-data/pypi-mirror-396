from functools import partial
from optparse import Option
import random
import copy
from typing import List, Union, Optional
import logging

from .utils import bpm_to_time, note_to_midi
from .chord import midi_chord

log = logging.getLogger(__name__)


def _random_chance(prob):
    return random.randint(1, 100) <= prob


def _oddeven(notes, even_first=False, **kwargs):
    odd = []
    even = []
    for i, n in enumerate(notes, start=1):
        if i % 2:
            even.append(n)
        else:
            odd.append(n)
    if even_first:
        return even + odd
    return odd + even


def oddeven(notes: List[int], **kwargs) -> List[int]:
    """
    odd indexed notes followed by even indexed notes
    """
    return _oddeven(notes)


def evenodd(notes: List[int], **kwargs) -> List[int]:
    """
    even indexed notes followed by odd indexed notes
    """
    return _oddeven(notes, even_first=True)


def _shift_n(notes: List[int], n: int = 1, **kwargs) -> List[int]:
    """
    switch the last n notes with the first n notes
    """
    n = min(n, len(notes))
    return notes[n:] + notes[:n]


def thumb_up(notes: List[int], **kwargs) -> List[int]:
    """
    alternate between the lowest note and an ascending scale
    """
    sorted_notes = list(sorted(notes))
    ordered_notes = []
    for note in sorted_notes[1:]:
        ordered_notes.extend([sorted_notes[0], note])
    return ordered_notes


def thumb_down(notes: List[int], **kwargs) -> List[int]:
    """
    alternate between the lowest note and a descending scale
    """
    sorted_notes = list(reversed(sorted(notes)))
    ordered_notes = []
    for note in sorted_notes[:-1]:
        ordered_notes.extend([sorted_notes[-1], note])
    return ordered_notes


def thumb_updown(notes: List[int], **kwargs) -> List[int]:
    """
    thumb up then down, without repeating highest and lowest notes.
    """
    return thumb_up(notes, **kwargs) + thumb_down(notes, **kwargs)[2:-2]


def thumb_downup(notes: List[int], **kwargs) -> List[int]:
    """
    thumb down then up, without repeating lowest and highest notes
    """
    return thumb_down(notes, **kwargs) + thumb_up(notes, **kwargs)[2:-2]


def _get_middle_note(notes, **kwargs):
    """
    find the middle element of a list of notes
    """
    middle = float(len(notes)) / 2
    if middle % 2 != 0:
        return notes[int(middle - 0.5)]
    return (notes[int(middle)], notes[int(middle - 1)])


def _gen_middle(notes, middle_note, overlapping=False, **kwargs):
    """
    generate a "middle" pattern
    """
    ordered_notes = []
    for note in notes:
        if note == middle_note:
            if overlapping:
                ordered_notes.extend([middle_note, note])
        else:
            ordered_notes.extend([middle_note, note])
    return ordered_notes


def middle_up(notes: List[int], overlapping=False, **kwargs) -> List[int]:
    """
    alternate between the middle note and an ascending scale
    """
    middle_note = _get_middle_note(notes)
    return _gen_middle(sorted(notes), middle_note, overlapping, **kwargs)


def middle_down(notes: List[int], overlapping=False, **kwargs) -> List[int]:
    """
    alternate between the middle note and a descending scale
    """
    middle_note = _get_middle_note(notes)
    return _gen_middle(sorted(notes, reverse=True), middle_note, overlapping, **kwargs)


def middle_updown(notes: List[int], **kwargs) -> List[int]:
    """
    middle up then down, without repeating notes.
    """
    return middle_up(notes, **kwargs) + middle_down(notes, **kwargs)[2:-2]


def middle_downup(notes: List[int], **kwargs) -> List[int]:
    """
    middle down then up, without repeating notes
    """
    return middle_down(notes, **kwargs) + middle_up(notes, **kwargs)[2:-2]


def pinky_up(notes: List[int], **kwargs) -> List[int]:
    """
    alternate between the highest note and an ascending scale
    """
    sorted_notes = list(sorted(notes))
    ordered_notes = []
    for note in sorted_notes[:-1]:
        ordered_notes.extend([sorted_notes[-1], note])
    return ordered_notes


def pinky_down(notes: List[int], **kwargs) -> List[int]:
    """
    alternate between the highest note and a descending scale
    """
    sorted_notes = list(reversed(sorted(notes)))
    ordered_notes = []
    for note in sorted_notes[1:]:
        ordered_notes.extend([sorted_notes[-1], note])
    return ordered_notes


def pinky_updown(notes: List[int], **kwargs) -> List[int]:
    """
    pinky up then down, without repeating highest and lowest notes.
    """
    return pinky_up(notes, **kwargs) + pinky_down(notes, **kwargs)[2:-2]


def pinky_downup(notes: List[int], **kwargs) -> List[int]:
    """
    pinky down then up, without repeating lowest and highest notes
    """
    return pinky_down(notes, **kwargs) + pinky_up(notes, **kwargs)[2:-2]


def random_shuffle(notes: List[int], **kwargs) -> List[int]:
    """
    randomly shuffle notes
    """
    random.shuffle(notes)
    return notes


def random_octaves(
    notes: List[int], octaves: List[int] = [1], prob_octave: int = 33, **kwargs
) -> List[int]:
    """
    randomly apply octaves to a sequence
    """
    new_notes = []
    for note in notes:
        if _random_chance(prob_octave):
            octave = random.choice(octaves)
            note += octave * 12
        new_notes.append(note)
    return new_notes


def random_silence(notes, prob_silence: int = 33, **kwargs) -> List[int]:
    """
    randomly remove notes from a sequence
    """
    new_notes = []
    for note in notes:
        if _random_chance(prob_silence):
            note = 0
        new_notes.append(note)
    return new_notes


def three_two(notes, **kwargs) -> List[int]:
    """
    3 notes then 2 of silence
    """
    breaks = range(0, len(notes), 5)
    for b in breaks[1:]:
        notes[b - 2 : b] = [0, 0]
    return notes


def two_three(notes, **kwargs) -> List[int]:
    """
    2 notes then 3 of silence
    """
    breaks = range(0, len(notes), 5)
    for b in breaks[1:]:
        notes[b - 3 : b] = [0, 0, 0]
    return notes


def even_off(notes, prob_even_off: int = 33, **kwargs) -> List[int]:
    """
    turn even notes randomly off
    """
    new_notes = []
    for i, note in enumerate(notes, 1):
        if i % 2 == 0 and _random_chance(prob_even_off):
            note = 0
        new_notes.append(note)
    return new_notes


def odd_off(notes, prob_odd_off: int = 29, **kwargs) -> List[int]:
    """
    turn odd notes randomly off
    """
    new_notes = []
    for i, note in enumerate(notes, 1):
        if i % 2 != 0 and _random_chance(prob_odd_off):
            note = 0
        new_notes.append(note)
    return new_notes


def down(x, **kwargs):
    return sorted(x, reverse=True)


def up(x, **kwargs):
    return sorted(x, reverse=False)


def downup(x, **kwargs):
    return list(reversed(sorted(x))) + list(sorted(x))[1:-1]


def updown(x, **kwargs):
    return list(sorted(x)) + list(reversed(sorted(x)))[1:-1]


def repeat_start(x, **kwargs):
    repeat_start_range = kwargs.get("repeat_start__range", [0])
    n = kwargs.get("repeat_start__n", repeat_start_range)
    return (x[0] * n) + x[1:]


def repeat_end(x, **kwargs):
    repeat_end_range = kwargs.get("repeat_end_range", [0])
    n = kwargs.get("repeat_end_n", repeat_end_range)
    return (x[0] * n) + x[1:]


STYLES = {
    "down": down,
    "up": up,
    "downup": downup,
    "updown": updown,
    "oddeven": oddeven,
    "evenodd": evenodd,
    "repeat_start": repeat_start,
    "repeat_end": repeat_end,
    "shift_1": partial(_shift_n, n=1),
    "shift_2": partial(_shift_n, n=2),
    "shift_3": partial(_shift_n, n=3),
    "shift_4": partial(_shift_n, n=4),
    "shift_5": partial(_shift_n, n=5),
    "shift_6": partial(_shift_n, n=6),
    "shift_7": partial(_shift_n, n=7),
    "shift_8": partial(_shift_n, n=8),
    "middle_up": middle_up,
    "middle_down": middle_down,
    "middle_updown": middle_updown,
    "middle_downup": middle_downup,
    "thumb_up": thumb_up,
    "thumb_down": thumb_down,
    "thumb_updown": thumb_updown,
    "thumb_downup": thumb_downup,
    "pinky_up": pinky_up,
    "pinky_down": pinky_down,
    "pinky_updown": pinky_updown,
    "pinky_downup": pinky_downup,
    "random": random_shuffle,
    "random_shuffle": random_shuffle,
    "random_octaves": random_octaves,
    "random_silence": random_silence,
    "three_two": three_two,
    "two_three": two_three,
    "odd_off": odd_off,
    "even_off": even_off,
}


def apply_style(notes: List[int], style: str = "down", **kwargs) -> List[int]:
    """
    Apply a style to a list of notes
    """
    if style not in STYLES:
        raise ValueError(f'Style "{style}" is not valid. Choose from:\n\n{", ".join(STYLES.keys())}')
    return STYLES.get(style)(notes, **kwargs)


def apply_styles(x: List[int], styles: List[str], **kwargs):
    """
    Apply a list of styles to a list of notes in order from left to right
    """
    # apply multiple styles, in order
    for style in styles:
        notes = apply_style(x, style, **kwargs)
    return notes


def _check_duration(total_time: Union[int, float], duration: Optional[Union[int, float]] = None):
    if duration and total_time >= duration:
        return True
    return False


def _gen_silence(duration):
    return {
        "note": 0,
        "type": "silence",
        "duration": duration,
        "velocity": 0,
    }


def midi_arp(
    notes: List[int] = [],  # arbitrary list of notes to arpeggiate
    root: str = "A3",  # root note of chord
    chord: str = "min6_9",  # chord name,
    inversions: List[int] = [],  # inversions list
    stack: int = 0,  # stack a chord up or down
    styles: List[str] = ["down"],
    octaves: List[int] = [0],  # a list of octaves to add to the notes (eg: [-1, 2])
    velocities: List[int] = [100],
    # a list of velocities to apply across notes,
    # velocities are retrieved using a modulo so
    # this can be any duration and will be applied
    # in order
    beat_bpm: float = 131.0,  # bpm to use when determining beat length
    beat_count: Union[float, int, str] = "1/16",  # count of one beat of the arp
    beat_time_sig: str = "4/4",  # time signature of arp
    beat_duration: Optional[float] = None,  # the time of the note in ms
    note_bpm: float = 131.0,  # bpm to use when determining note duration
    note_count: Union[
        float, int, str
    ] = "3/64",  # count of note legth (should be less than or equat to beat count)
    note_time_sig: str = "4/4",  # time signature of arp
    note_duration: Optional[float] = None,  # arbitrary duration of note in ms
    start_bpm: float = 131.0,  # bpm to use when determining the start of the arp and adds silence at the beginning
    start_count: Union[float, int, str] = 0,  # the start beat count
    start_time_sig: str = "4/4",  # time signature to use when determining start
    start_duration: Optional[
        float
    ] = None,  # the amount of silence to add at the beginning in ms
    duration_bpm: float = 131.0,  # bpm to use when determining note duration
    duration_count: Union[float, int, str] = "16",  # the duration beat count
    duration_time_sig: str = "4/4",  # time signature to use when determining duration
    duration: Optional[Union[float, int]] = 1000.0,  # the total duration of the pattern in ms
    loops: Optional[int] = None,
    **kwargs,
):
    """
    Given a list of chord notes, a style name (eg: up, down), and a note count, generate an arpeggiated sequence of notes.
    """

    # generate notes
    if len(notes):
        chord_notes = [note_to_midi(n) for n in notes]
    else:
        chord_notes = midi_chord(root, chord, inversions, stack, **kwargs)

    # create list of notes including octaves
    chord_notes = list(
        set(chord_notes + [o * 12 + n for o in octaves for n in chord_notes])
    )
    # determine beat_duration
    if not beat_duration:
        beat_duration = bpm_to_time(beat_bpm, beat_count, beat_time_sig)

    # determine note_duration
    if not note_duration:
        note_duration = min(
            bpm_to_time(note_bpm, note_count, note_time_sig), beat_duration
        )
    else:
        note_duration = copy.copy(beat_duration)

    # clamp note_duration to beat_duration
    if note_duration > beat_duration:
        log.warning(
            f"WARNING: note_duration {note_duration} is greater than {beat_duration}, "
        )
        note_duration = copy.copy(beat_duration)

    # determine total duration
    if not duration:
        duration = bpm_to_time(duration_bpm, duration_count, duration_time_sig)

    # add silence
    if not start_duration:
        start_duration = bpm_to_time(start_bpm, start_count, start_time_sig)

    if start_duration and start_duration > 0:
        yield _gen_silence(start_duration)

    # keep track of time and loops
    total_time = 0.0
    n_loops = 0

    #
    while True:
        # apply the style /  order
        for i, note in enumerate(apply_styles(chord_notes, styles, **kwargs)):

            # determine the velocity
            velocity = velocities[i % len(velocities)]
            # TODO: randomize velocity

            # clamp max duration on last note.
            if not loops and duration and (total_time + beat_duration) > duration:
                beat_duration = duration - total_time
                note_duration = duration - total_time


            yield {
                "note": note,
                "type": "note" if note != 0 else "silence",
                "duration": note_duration,
                "velocity": velocity,
            }
            silence_duration = beat_duration - note_duration
            if silence_duration > 0:
                yield _gen_silence(silence_duration)

            # check for max duration after each beat if loops are not set.
            total_time += beat_duration
            if not loops and _check_duration(total_time, duration):
                break

        # check for max duration after breaking out of the notes loop if loops are not set
        if not loops and _check_duration(total_time, duration):
            break

        # check for loops if set
        n_loops += 1
        if loops and n_loops >= loops:
            break
