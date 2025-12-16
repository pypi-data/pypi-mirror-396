from typing import Union

from .constants import (
    NOTE_TO_MIDI,
    ROOT_TO_MIDI,
    NOTE_EQUIVALENTS,
    MIDI_TO_FREQ,
    MIDI_TO_NOTE,
    NOTE_TO_FREQ,
)


def sharp_to_flat(note_name: str) -> str:
    """Translate a sharp note to its flat equivalent.

    Since the library uses flats internally, this converts sharp notes (e.g., 'C#')
    to their flat equivalents (e.g., 'Db').

    Args:
        note_name: A note name that may contain a sharp (e.g., 'C#4', 'F#').

    Returns:
        str: The equivalent flat note name, or the original if no sharp present.

    Raises:
        ValueError: If the note name contains an invalid sharp note.
    """
    if "#" in note_name:
        try:
            sharp_note = NOTE_EQUIVALENTS[note_name[:2]]
        except KeyError:
            raise ValueError(f"Invalid note: {note_name}")
        return sharp_note + note_name[2:]
    return note_name


def note_to_midi(note_name: Union[str, int]) -> int:
    """Convert a note name to its corresponding MIDI note number.

    If passed a valid MIDI note number or numeric string, returns it as an integer.
    Otherwise converts note name (e.g., 'C3') to MIDI number (e.g., 60).

    Args:
        note_name: A valid note name from `midi_utils.constants.NOTE_TO_MIDI`
                   (e.g., 'C3', 'Ab4') or an integer/string MIDI note (0-127).

    Returns:
        int: MIDI note number between 0 and 127.

    Raises:
        ValueError: If note name is invalid or MIDI note is outside 0-127 range.
    """
    if isinstance(note_name, str):
        try:
            midi_note = int(note_name)
        except ValueError:
            note_name = str(note_name).upper()
            note_name = sharp_to_flat(note_name)
            if note_name in NOTE_TO_MIDI:
                midi_note = NOTE_TO_MIDI[note_name]
            else:
                raise ValueError(f'"{note_name}" is not a valid note.')
    else:
        midi_note = int(note_name)
    if midi_note < 0 or midi_note > 127:
        raise ValueError(
            f'"{midi_note}" is not a valid midi note. Must be between 0 and 127'
        )
    return midi_note


def note_to_freq(note_name: str) -> float:
    """Convert a note name to its corresponding frequency in Hz.

    Args:
        note_name: A valid note name from `midi_utils.constants.NOTE_TO_MIDI`
                   (e.g., 'A4', 'C3').

    Returns:
        float: Frequency in Hertz (e.g., 440.0 for A4).

    Raises:
        ValueError: If note name is not found in NOTE_TO_FREQ.
    """
    try:
        return NOTE_TO_FREQ[note_name]
    except KeyError:
        raise ValueError(f"Invalid note name: {note_name}")


def midi_to_note(midi_note_num: int) -> str:
    """Convert a MIDI note number to its corresponding note name.

    Args:
        midi_note_num: A MIDI note number between 0 and 127 (e.g., 60, 69).

    Returns:
        str: Note name in scientific pitch notation (e.g., 'C3', 'A4').

    Raises:
        ValueError: If MIDI note number is not between 0 and 127.
    """
    try:
        return MIDI_TO_NOTE[midi_note_num]
    except KeyError:
        raise ValueError(f"Invalid midi note num: {midi_note_num}")


def midi_to_freq(midi_note_num: int) -> float:
    """Convert a MIDI note number to its corresponding frequency in Hz.

    Args:
        midi_note_num: A MIDI note number between 0 and 127 (e.g., 69 for A4).

    Returns:
        float: Frequency in Hertz (e.g., 440.0 for MIDI note 69).

    Raises:
        ValueError: If MIDI note number is not between 0 and 127.
    """
    try:
        return MIDI_TO_FREQ[midi_note_num]
    except KeyError:
        raise ValueError(f"Invalid midi note num: {midi_note_num}")


def midi_to_octave(midi_note_num: int, octave: int) -> int:
    """Transpose a MIDI note by one or more octaves.

    Args:
        midi_note_num: A valid MIDI note between 0 and 127.
        octave: Number of octaves to transpose. Positive values transpose up,
                negative values transpose down (e.g., 1, -1, 2).

    Returns:
        int: Transposed MIDI note number.

    Raises:
        ValueError: If resulting MIDI note is outside 0-127 range.
    """
    midi_note_num += octave * 12
    if midi_note_num < 0 or midi_note_num > 127:
        raise ValueError(f"midi note num {midi_note_num} out of valid range.")
    return midi_note_num


def root_to_midi(root: Union[str, int]) -> int:
    """Convert a root name to its corresponding MIDI note number (0-11).

    If passed a valid MIDI note value (0-11), returns it unchanged.

    Args:
        root: A valid root name from `midi_utils.constants.ROOT_TO_MIDI`
              (e.g., 'C', 'Db', 'F#') or a MIDI note between 0 and 11.

    Returns:
        int: MIDI note number between 0 and 11 representing the root.

    Raises:
        ValueError: If root name or number is invalid.
    """
    if isinstance(root, str):
        root = root.upper()
        if root in ROOT_TO_MIDI:
            return ROOT_TO_MIDI[root]
        raise ValueError(
            f'"{root}" is not a valid root name. Choose from: {", ".join(ROOT_TO_MIDI.keys())}'
        )
    if root not in ROOT_TO_MIDI.values():
        raise ValueError(
            f'"{root}" is not a valid midi root. Choose from: {", ".join(ROOT_TO_MIDI.values())}'
        )
    return root


def freq_to_octave(freq: float, octave: int) -> float:
    """Transpose a frequency up or down by octaves.

    Each octave up doubles the frequency, each octave down halves it.

    Args:
        freq: Frequency in Hertz (e.g., 440.0).
        octave: Number of octaves to transpose. Positive values transpose up,
                negative values transpose down.

    Returns:
        float: Transposed frequency in Hertz.
    """
    if octave < 0:
        return freq * (1.0 / (abs(octave) * 2.0))
    return freq * (octave * 2.0)


def bpm_to_time(
    bpm: float = 120.00, count: Union[str, int, float] = 1, time_sig: str = "4/4"
) -> float:
    """Convert BPM, beat count, and time signature to duration in milliseconds.

    Args:
        bpm: Beats per minute (e.g., 120.0).
        count: Number of beats as float, int, or string fraction (e.g., 1, 0.5, '1/4').
        time_sig: Time signature as string (e.g., '4/4', '3/4').

    Returns:
        float: Duration in milliseconds.
    """
    if isinstance(count, str):
        if "/" in count:
            numerator, denominator = count.split("/")
            count = float(numerator) / float(denominator)
    time_segs = time_sig.split("/")
    return (60.00 / float(bpm)) * float(time_segs[0]) * float(count) * 1000.0


def rescale(x, range_x, range_y, sig_digits=3):
    """Rescale a value from one range to another.

    Linearly maps a value from an input range to an output range.

    Args:
        x: Value to rescale.
        range_x: Input range as [min, max] list.
        range_y: Output range as [min, max] list.
        sig_digits: Number of decimal places to round result. Default 3.

    Returns:
        float: Rescaled value rounded to sig_digits decimal places.
    """

    # Figure out how 'wide' each range is
    x_span = max(range_x) - min(range_x)
    y_span = max(range_y) - min(range_y)

    # Compute the scale factor between left and right values
    scale_factor = float(y_span) / float(x_span)

    return round(min(range_y) + (x - min(range_x)) * scale_factor, sig_digits)
