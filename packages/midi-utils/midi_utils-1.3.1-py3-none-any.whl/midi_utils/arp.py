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
    """Check if a random event should occur based on probability.

    Args:
        prob: Integer percentage (0-100) chance of returning True.

    Returns:
        bool: True if random number is less than or equal to prob.
    """
    return random.randint(1, 100) <= prob


def _oddeven(notes, even_first=False, **kwargs):
    """Separate notes into odd and even indexed groups.

    Args:
        notes: List of MIDI note numbers.
        even_first: If True, return even-indexed notes first.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Notes reordered by odd/even index.
    """
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
    """Reorder notes with odd-indexed notes followed by even-indexed notes.

    Args:
        notes: List of MIDI note numbers to reorder.
        **kwargs: Additional arguments passed to _oddeven.

    Returns:
        List[int]: Notes reordered as [odd indices, even indices].
    """
    return _oddeven(notes)


def evenodd(notes: List[int], **kwargs) -> List[int]:
    """Reorder notes with even-indexed notes followed by odd-indexed notes.

    Args:
        notes: List of MIDI note numbers to reorder.
        **kwargs: Additional arguments passed to _oddeven.

    Returns:
        List[int]: Notes reordered as [even indices, odd indices].
    """
    return _oddeven(notes, even_first=True)


def _shift_n(notes: List[int], n: int = 1, **kwargs) -> List[int]:
    """Rotate notes by moving first n notes to the end.

    Args:
        notes: List of MIDI note numbers.
        n: Number of notes to shift from start to end.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Rotated list with first n notes moved to end.
    """
    n = min(n, len(notes))
    return notes[n:] + notes[:n]


def thumb_up(notes: List[int], **kwargs) -> List[int]:
    """Create pattern alternating between lowest note and ascending scale.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Pattern like [lowest, 2nd, lowest, 3rd, lowest, 4th, ...].
    """
    sorted_notes = list(sorted(notes))
    ordered_notes = []
    for note in sorted_notes[1:]:
        ordered_notes.extend([sorted_notes[0], note])
    return ordered_notes


def thumb_down(notes: List[int], **kwargs) -> List[int]:
    """Create pattern alternating between lowest note and descending scale.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Pattern like [lowest, highest, lowest, 2nd-highest, ...].
    """
    sorted_notes = list(reversed(sorted(notes)))
    ordered_notes = []
    for note in sorted_notes[:-1]:
        ordered_notes.extend([sorted_notes[-1], note])
    return ordered_notes


def thumb_updown(notes: List[int], **kwargs) -> List[int]:
    """Combine thumb_up and thumb_down patterns without repeating extremes.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments passed to thumb functions.

    Returns:
        List[int]: Combined pattern of thumb_up followed by thumb_down.
    """
    return thumb_up(notes, **kwargs) + thumb_down(notes, **kwargs)[2:-2]


def thumb_downup(notes: List[int], **kwargs) -> List[int]:
    """Combine thumb_down and thumb_up patterns without repeating extremes.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments passed to thumb functions.

    Returns:
        List[int]: Combined pattern of thumb_down followed by thumb_up.
    """
    return thumb_down(notes, **kwargs) + thumb_up(notes, **kwargs)[2:-2]


def _get_middle_note(notes, **kwargs):
    """Find the middle element(s) of a list of notes.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments (unused).

    Returns:
        int or tuple: Middle note if odd length, tuple of two middle notes if even.
    """
    middle = float(len(notes)) / 2
    if middle % 2 != 0:
        return notes[int(middle - 0.5)]
    return (notes[int(middle)], notes[int(middle - 1)])


def _gen_middle(notes, middle_note, overlapping=False, **kwargs):
    """Generate pattern alternating between middle note and other notes.

    Args:
        notes: List of MIDI note numbers.
        middle_note: The middle note to alternate with.
        overlapping: If True, repeat middle note when encountered.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Pattern alternating middle note with each other note.
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
    """Create pattern alternating between middle note and ascending scale.

    Args:
        notes: List of MIDI note numbers.
        overlapping: If True, repeat middle note when encountered.
        **kwargs: Additional arguments passed to _gen_middle.

    Returns:
        List[int]: Pattern like [middle, lowest, middle, 2nd, middle, 3rd, ...].
    """
    middle_note = _get_middle_note(notes)
    return _gen_middle(sorted(notes), middle_note, overlapping, **kwargs)


def middle_down(notes: List[int], overlapping=False, **kwargs) -> List[int]:
    """Create pattern alternating between middle note and descending scale.

    Args:
        notes: List of MIDI note numbers.
        overlapping: If True, repeat middle note when encountered.
        **kwargs: Additional arguments passed to _gen_middle.

    Returns:
        List[int]: Pattern like [middle, highest, middle, 2nd-highest, ...].
    """
    middle_note = _get_middle_note(notes)
    return _gen_middle(sorted(notes, reverse=True), middle_note, overlapping, **kwargs)


def middle_updown(notes: List[int], **kwargs) -> List[int]:
    """Combine middle_up and middle_down patterns without repeating notes.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments passed to middle functions.

    Returns:
        List[int]: Combined pattern of middle_up followed by middle_down.
    """
    return middle_up(notes, **kwargs) + middle_down(notes, **kwargs)[2:-2]


def middle_downup(notes: List[int], **kwargs) -> List[int]:
    """Combine middle_down and middle_up patterns without repeating notes.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments passed to middle functions.

    Returns:
        List[int]: Combined pattern of middle_down followed by middle_up.
    """
    return middle_down(notes, **kwargs) + middle_up(notes, **kwargs)[2:-2]


def pinky_up(notes: List[int], **kwargs) -> List[int]:
    """Create pattern alternating between highest note and ascending scale.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Pattern like [highest, lowest, highest, 2nd, highest, 3rd, ...].
    """
    sorted_notes = list(sorted(notes))
    ordered_notes = []
    for note in sorted_notes[:-1]:
        ordered_notes.extend([sorted_notes[-1], note])
    return ordered_notes


def pinky_down(notes: List[int], **kwargs) -> List[int]:
    """Create pattern alternating between highest note and descending scale.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Pattern like [highest, highest, highest, 2nd-highest, ...].
    """
    sorted_notes = list(reversed(sorted(notes)))
    ordered_notes = []
    for note in sorted_notes[1:]:
        ordered_notes.extend([sorted_notes[-1], note])
    return ordered_notes


def pinky_updown(notes: List[int], **kwargs) -> List[int]:
    """Combine pinky_up and pinky_down patterns without repeating extremes.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments passed to pinky functions.

    Returns:
        List[int]: Combined pattern of pinky_up followed by pinky_down.
    """
    return pinky_up(notes, **kwargs) + pinky_down(notes, **kwargs)[2:-2]


def pinky_downup(notes: List[int], **kwargs) -> List[int]:
    """Combine pinky_down and pinky_up patterns without repeating extremes.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments passed to pinky functions.

    Returns:
        List[int]: Combined pattern of pinky_down followed by pinky_up.
    """
    return pinky_down(notes, **kwargs) + pinky_up(notes, **kwargs)[2:-2]


def random_shuffle(notes: List[int], **kwargs) -> List[int]:
    """Randomly shuffle the order of notes.

    Args:
        notes: List of MIDI note numbers to shuffle.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Notes in random order.
    """
    random.shuffle(notes)
    return notes


def random_octaves(
    notes: List[int], octaves: List[int] = [1], prob_octave: int = 33, **kwargs
) -> List[int]:
    """Randomly transpose notes by octaves based on probability.

    Args:
        notes: List of MIDI note numbers.
        octaves: List of octave shifts to choose from (e.g., [-1, 1, 2]).
        prob_octave: Percentage chance (0-100) each note gets transposed.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Notes with random octave transpositions applied.
    """
    new_notes = []
    for note in notes:
        if _random_chance(prob_octave):
            octave = random.choice(octaves)
            note += octave * 12
        new_notes.append(note)
    return new_notes


def random_silence(notes, prob_silence: int = 33, **kwargs) -> List[int]:
    """Randomly replace notes with silence based on probability.

    Args:
        notes: List of MIDI note numbers.
        prob_silence: Percentage chance (0-100) each note becomes silent (0).
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Notes with random silences (0 values) inserted.
    """
    new_notes = []
    for note in notes:
        if _random_chance(prob_silence):
            note = 0
        new_notes.append(note)
    return new_notes


def three_two(notes, **kwargs) -> List[int]:
    """Create pattern with 3 notes followed by 2 silences, repeating.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Pattern with every 4th and 5th position replaced by silence (0).
    """
    breaks = range(0, len(notes), 5)
    for b in breaks[1:]:
        notes[b - 2 : b] = [0, 0]
    return notes


def two_three(notes, **kwargs) -> List[int]:
    """Create pattern with 2 notes followed by 3 silences, repeating.

    Args:
        notes: List of MIDI note numbers.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Pattern with every 3rd, 4th, and 5th position replaced by silence (0).
    """
    breaks = range(0, len(notes), 5)
    for b in breaks[1:]:
        notes[b - 3 : b] = [0, 0, 0]
    return notes


def even_off(notes, prob_even_off: int = 33, **kwargs) -> List[int]:
    """Randomly silence even-indexed notes based on probability.

    Args:
        notes: List of MIDI note numbers.
        prob_even_off: Percentage chance (0-100) each even-indexed note becomes silent.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Notes with even-indexed positions randomly silenced.
    """
    new_notes = []
    for i, note in enumerate(notes, 1):
        if i % 2 == 0 and _random_chance(prob_even_off):
            note = 0
        new_notes.append(note)
    return new_notes


def odd_off(notes, prob_odd_off: int = 29, **kwargs) -> List[int]:
    """Randomly silence odd-indexed notes based on probability.

    Args:
        notes: List of MIDI note numbers.
        prob_odd_off: Percentage chance (0-100) each odd-indexed note becomes silent.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Notes with odd-indexed positions randomly silenced.
    """
    new_notes = []
    for i, note in enumerate(notes, 1):
        if i % 2 != 0 and _random_chance(prob_odd_off):
            note = 0
        new_notes.append(note)
    return new_notes


def down(x, **kwargs):
    """Sort notes in descending order (highest to lowest).

    Args:
        x: List of MIDI note numbers.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Notes sorted from highest to lowest.
    """
    return sorted(x, reverse=True)


def up(x, **kwargs):
    """Sort notes in ascending order (lowest to highest).

    Args:
        x: List of MIDI note numbers.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Notes sorted from lowest to highest.
    """
    return sorted(x, reverse=False)


def downup(x, **kwargs):
    """Sort notes descending then ascending without repeating extremes.

    Args:
        x: List of MIDI note numbers.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Pattern starting high, going low, then back high.
    """
    return list(reversed(sorted(x))) + list(sorted(x))[1:-1]


def updown(x, **kwargs):
    """Sort notes ascending then descending without repeating extremes.

    Args:
        x: List of MIDI note numbers.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Pattern starting low, going high, then back low.
    """
    return list(sorted(x)) + list(reversed(sorted(x)))[1:-1]


def repeat_start(x, **kwargs):
    """Repeat the first note n times before the rest of the sequence.

    Args:
        x: List of MIDI note numbers.
        **kwargs: May contain 'repeat_start__n' for number of repetitions.

    Returns:
        List[int]: Notes with first note repeated n times at start.
    """
    repeat_start_range = kwargs.get("repeat_start__range", [0])
    n = kwargs.get("repeat_start__n", repeat_start_range)
    return (x[0] * n) + x[1:]


def repeat_end(x, **kwargs):
    """Repeat the last note n times after the rest of the sequence.

    Args:
        x: List of MIDI note numbers.
        **kwargs: May contain 'repeat_end_n' for number of repetitions.

    Returns:
        List[int]: Notes with last note repeated n times at end.
    """
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
    """Apply an arpeggio style transformation to a list of notes.

    Args:
        notes: List of MIDI note numbers to transform.
        style: Name of style to apply (e.g., 'up', 'down', 'updown', 'thumb_up').
        **kwargs: Additional arguments passed to the style function.

    Returns:
        List[int]: Transformed notes according to the specified style.

    Raises:
        ValueError: If style name is not recognized.
    """
    if style not in STYLES:
        raise ValueError(
            f'Style "{style}" is not valid. Choose from:\n\n{", ".join(STYLES.keys())}'
        )
    return STYLES.get(style)(notes, **kwargs)


def apply_styles(x: List[int], styles: List[str], **kwargs):
    """Apply multiple style transformations sequentially to notes.

    Args:
        x: List of MIDI note numbers to transform.
        styles: List of style names to apply in order.
        **kwargs: Additional arguments passed to each style function.

    Returns:
        List[int]: Notes after all style transformations are applied.
    """
    # apply multiple styles, in order
    for style in styles:
        notes = apply_style(x, style, **kwargs)
    return notes


def _check_duration(
    total_time: Union[int, float], duration: Optional[Union[int, float]] = None
):
    """Check if total time has reached or exceeded target duration.

    Args:
        total_time: Current accumulated time in milliseconds.
        duration: Target duration in milliseconds, or None for no limit.

    Returns:
        bool: True if duration is set and total_time >= duration.
    """
    if duration and total_time >= duration:
        return True
    return False


def _gen_silence(duration):
    """Generate a silence event dictionary.

    Args:
        duration: Length of silence in milliseconds.

    Returns:
        dict: Silence event with note=0, type='silence', and velocity=0.
    """
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
    ] = "3/64",  # count of note length (should be less than or equal to beat count)
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
    duration: Optional[
        Union[float, int]
    ] = 1000.0,  # the total duration of the pattern in ms
    loops: Optional[int] = None,
    **kwargs,
):
    """Generate an arpeggiated sequence of MIDI note events.

    Creates an arpeggio pattern from a chord or list of notes, applying style
    transformations and timing parameters. Yields note event dictionaries with
    note numbers, durations, and velocities.

    Args:
        notes: Explicit list of MIDI note numbers to arpeggiate (overrides chord).
        root: Root note for chord generation (e.g., 'A3', 'C4').
        chord: Chord type name (e.g., 'min6_9', 'maj7').
        inversions: List of inversion degrees to apply to chord.
        stack: Number of octaves to stack the chord up (positive) or down (negative).
        styles: List of style names to apply (e.g., ['down', 'random_octaves']).
        octaves: Octave shifts to include (e.g., [0, 1] includes original and +1 octave).
        velocities: MIDI velocities (0-127) to cycle through for notes.
        beat_bpm: BPM for calculating beat duration.
        beat_count: Beat count as string (e.g., '1/16') or number for each note step.
        beat_time_sig: Time signature for beat calculations.
        beat_duration: Override beat duration in milliseconds.
        note_bpm: BPM for calculating note duration.
        note_count: Note length as string (e.g., '3/64') or number.
        note_time_sig: Time signature for note duration calculations.
        note_duration: Override note duration in milliseconds.
        start_bpm: BPM for calculating start silence.
        start_count: Beat count for initial silence.
        start_time_sig: Time signature for start calculation.
        start_duration: Override start silence duration in milliseconds.
        duration_bpm: BPM for calculating total duration.
        duration_count: Beat count for total duration.
        duration_time_sig: Time signature for duration calculation.
        duration: Total pattern duration in milliseconds.
        loops: Number of times to loop the pattern (None for duration-based).
        **kwargs: Additional arguments passed to style functions.

    Yields:
        dict: Note events with keys 'note' (MIDI number or 0 for silence),
              'type' ('note' or 'silence'), 'duration' (ms), 'velocity' (0-127).
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
