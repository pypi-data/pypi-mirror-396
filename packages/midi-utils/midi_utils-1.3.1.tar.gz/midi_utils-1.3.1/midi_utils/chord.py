from typing import List, Union

from midi_utils.constants import CHORDS
from midi_utils.utils import note_to_midi


def lookup_chord(root: Union[str, int], chord: str, **kwargs) -> List[int]:
    """Look up chord notes given a root note and chord name.

    Args:
        root: Root note as string (e.g., 'C4', 'A3') or MIDI note number.
        chord: Chord name/type (e.g., 'MIN_6_9', 'MAJ7'). Case-insensitive.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: MIDI note numbers for the chord.

    Raises:
        ValueError: If chord name is not found in CHORDS dictionary.
    """
    midi_root = note_to_midi(root)
    base_notes = CHORDS.get(chord.upper().strip())
    if not base_notes:
        raise ValueError(
            f'Invalid chord name: {chord}. Choose from:{",".join(CHORDS.keys())}'
        )
    return [midi_root + note for note in base_notes]


def invert_chord(
    chord_notes: List[int], inversions: List[int] = [], **kwargs
) -> List[int]:
    """Apply inversions to chord notes by transposing each note by octaves.

    Args:
        chord_notes: List of MIDI note numbers in the chord.
        inversions: List of octave shifts (e.g., [0, 1, -1]) to apply cyclically to notes.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Inverted chord notes with octave transpositions applied.
                   Returns original chord_notes if inversions is empty.
    """
    if not len(inversions):
        return chord_notes

    inverted_chord = []
    for i, note in enumerate(chord_notes):
        inv = inversions[i % len(inversions)]
        note += inv * 12
        inverted_chord.append(note)
    return inverted_chord


def stack_chord(chord_notes: List[int], stack: int = 0, **kwargs) -> List[int]:
    """Stack a chord by adding octave-transposed copies and combining with original.

    Creates an additional copy of the chord transposed by the specified number of octaves,
    then combines with the original and returns sorted unique notes.

    Args:
        chord_notes: List of MIDI note numbers in the chord.
        stack: Number of octaves to transpose the stacked copy.
               Positive values stack up, negative values stack down.
        **kwargs: Additional arguments (unused).

    Returns:
        List[int]: Sorted list of unique MIDI notes from original and stacked chord.
    """
    stacked_chord = [(stack * 12) + note for note in chord_notes]
    return list(sorted(list(set(stacked_chord + chord_notes))))


def midi_chord(
    root: Union[str, int], chord="MIN_6_9", inversions=[], stack=0, **kwargs
) -> List[int]:
    """Generate MIDI chord notes with optional inversions and stacking.

    Combines chord lookup, inversion, and stacking operations to generate
    a complete chord with all transformations applied.

    Args:
        root: Root note as string (e.g., 'C4', 'A3') or MIDI note number.
        chord: Chord name/type (e.g., 'MIN_6_9', 'MAJ7'). Default 'MIN_6_9'.
        inversions: List of octave shifts to apply to each note cyclically.
        stack: Number of octaves to transpose additional chord copy.
        **kwargs: Additional arguments passed to lookup_chord, invert_chord, and stack_chord.

    Returns:
        List[int]: Sorted list of unique MIDI note numbers for the complete chord.

    Raises:
        ValueError: If chord name is not found in CHORDS dictionary.
    """
    chord_notes = lookup_chord(root, chord)
    return stack_chord(invert_chord(chord_notes, inversions), stack)
