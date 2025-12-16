# ADSR generator
from platform import release
from typing import Generator

from .utils import rescale


class ADSR:
    """ADSR (Attack, Decay, Sustain, Release) envelope generator.

    Generates amplitude envelope values over time according to the classic ADSR model:
    - Attack: Time to reach peak amplitude from start
    - Decay: Time to descend from peak to sustain level
    - Sustain: Level maintained during note hold
    - Release: Time to fade to zero after note release

    The envelope can be iterated to get amplitude values for each sample.
    """

    def __init__(
        self,
        attack: float = 0.2,
        decay: float = 0.2,
        sustain: float = 0.7,
        release: float = 0.3,
        samples: int = 20,
        attack_min_level: float = 0.0,
        attack_max_level: float = 1.0,
        sig_digits: int = 2,
        is_zero_indexed: bool = True,
    ):
        """Initialize ADSR envelope generator.

        Args:
            attack: Percentage of samples (0.0-1.0) to reach peak amplitude.
            decay: Percentage of samples (0.0-1.0) to descend to sustain level.
            sustain: Amplitude level (0.0-1.0) maintained during sustain phase.
            release: Percentage of samples (0.0-1.0) to fade from sustain to zero.
            samples: Total number of samples in the envelope.
            attack_min_level: Starting amplitude level for attack phase.
            attack_max_level: Peak amplitude level at end of attack phase.
            sig_digits: Number of decimal places to round envelope values.
            is_zero_indexed: If True, sample indexing starts at 0; if False, starts at 1.

        Raises:
            ValueError: If attack + decay + release > 1.0.
        """
        self.attack = attack
        self.decay = decay
        self.sustain_level = sustain
        self.release = release
        self.sustain = 1.0 - (self.attack + self.decay + self.release)

        if self.sustain < 0:
            raise ValueError(
                "The sum of attack, decay, and release percentages are greater than 1"
            )

        self.samples = samples
        self.attack_min_level = attack_min_level
        self.attack_max_level = attack_max_level
        self.sig_digits = sig_digits
        self.is_zero_indexed = is_zero_indexed
        self.idx = -1

    def get_value(self, sample: int):
        """Get envelope amplitude value at a specific sample position.

        Args:
            sample: Sample index position in the envelope.

        Returns:
            float: Amplitude value (0.0-1.0) at the given sample, rounded to sig_digits.
        """
        if not self.is_zero_indexed:
            sample += 1

        sample_per = float(sample) / float(self.samples)
        val = 0.0

        if sample_per <= self.attack:
            if self.attack == 0:
                val = 1
            else:
                val = rescale(
                    sample_per / self.attack,
                    range_x=[0, 1],
                    range_y=[self.attack_min_level, self.attack_max_level],
                )

        elif (sample_per - self.attack) < self.decay:
            if self.decay > 0:
                decay_ratio = (sample_per - self.attack) / self.decay
            else:
                decay_ratio = 0
            val = 1 - (decay_ratio * (1 - self.sustain_level))

        elif (sample_per - self.attack - self.decay) < self.sustain:
            val = self.sustain_level

        else:
            if self.release > 0:
                release_ratio = (
                    sample_per - self.attack - self.decay - self.sustain
                ) / self.release
            else:
                release_ratio = 0
            val = (1 - release_ratio) * self.sustain_level

        return max(0.0, round(val, self.sig_digits))

    def __iter__(self) -> Generator[float, None, None]:
        """Iterate through all envelope amplitude values.

        Yields:
            float: Amplitude value for each sample from 0 to samples-1.
        """
        for i in range(0, self.samples):
            yield self.get_value(i)

    def __next__(self):
        """Get next envelope value in iteration.

        Returns:
            float: Amplitude value at current index position.

        Raises:
            StopIteration: When all samples have been exhausted.
        """
        self.idx += 1
        if self.idx > self.samples:
            raise StopIteration
        return self.get_value(self.idx)
