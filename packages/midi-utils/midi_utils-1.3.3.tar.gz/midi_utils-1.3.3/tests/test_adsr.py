from midi_utils import ADSR


def test_adsr_iter():
    adsr = ADSR(
        attack=0.2,
        decay=0.2,
        sustain=0.7,
        release=0.3,
        samples=20,
        sig_digits=2,
        is_zero_indexed=True,
    )
    assert list(adsr) == [
        0.0,
        0.25,
        0.5,
        0.75,
        1.0,
        0.93,
        0.85,
        0.78,
        0.7,
        0.7,
        0.7,
        0.7,
        0.7,
        0.7,
        0.7,
        0.58,
        0.47,
        0.35,
        0.23,
        0.12,
    ]


def test_adsr_next():
    adsr = ADSR(
        attack=0.2,
        decay=0.2,
        sustain=0.7,
        release=0.3,
        samples=20,
        sig_digits=2,
        is_zero_indexed=True,
    )
    assert next(adsr) == 0.0
    assert next(adsr) == 0.25


def test_adsr_release_0():
    adsr = ADSR(
        attack=0.2,
        decay=0.2,
        sustain=0.7,
        release=0.0,
        samples=20,
        sig_digits=2,
        is_zero_indexed=True,
    )
    assert list(adsr) == [
        0.0,
        0.25,
        0.5,
        0.75,
        1.0,
        0.93,
        0.85,
        0.78,
        0.7,
        0.7,
        0.7,
        0.7,
        0.7,
        0.7,
        0.7,
        0.7,
        0.7,
        0.7,
        0.7,
        0.7,
    ]


def test_adsr_decay_0():
    adsr = ADSR(
        attack=0.2,
        decay=0.0,
        sustain=0.7,
        release=0.6,
        samples=20,
        sig_digits=2,
        is_zero_indexed=True,
    )
    assert list(adsr) == [
        0.0,
        0.25,
        0.5,
        0.75,
        1.0,
        0.7,
        0.7,
        0.7,
        0.7,
        0.64,
        0.58,
        0.52,
        0.47,
        0.41,
        0.35,
        0.29,
        0.23,
        0.17,
        0.12,
        0.06,
    ]


def test_adsr_attack_0():
    adsr = ADSR(
        attack=0.0,
        decay=0.2,
        sustain=0.7,
        release=0.6,
        samples=20,
        sig_digits=2,
        is_zero_indexed=True,
    )
    assert list(adsr) == [
        1,
        0.93,
        0.85,
        0.78,
        0.7,
        0.7,
        0.7,
        0.7,
        0.7,
        0.64,
        0.58,
        0.52,
        0.47,
        0.41,
        0.35,
        0.29,
        0.23,
        0.17,
        0.12,
        0.06,
    ]


def test_adsr_attack_min():
    adsr = ADSR(
        attack=0.2,
        decay=0.2,
        sustain=0.7,
        release=0.6,
        samples=20,
        attack_min_level=0.2,
        sig_digits=2,
        is_zero_indexed=True,
    )
    assert list(adsr) == [
        0.2,
        0.4,
        0.6,
        0.8,
        1.0,
        0.93,
        0.85,
        0.78,
        0.7,
        0.64,
        0.58,
        0.52,
        0.47,
        0.41,
        0.35,
        0.29,
        0.23,
        0.18,
        0.12,
        0.06,
    ]
