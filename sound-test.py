#!/usr/bin/env python
"""Play a fixed frequency sound."""
from __future__ import division
import math

from pyaudio import PyAudio
from itertools import izip


def get_samples(frequency, volume, sample_rate):
    samples = (
        int(
            (volume * math.sin(2 * math.pi * frequency * t / sample_rate)) *
            0x7f +
            0x80
        )
        for t in xrange(n_samples)  # NOQA
    )
    return samples


def sine_tone(frequency, duration, volume=1, sample_rate=22050):
    n_samples = int(sample_rate * duration)
    restframes = n_samples % sample_rate

    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(1),  # 8bit
                    channels=1,  # mono
                    rate=sample_rate,
                    output=True)
    samples = get_samples(frequency, volume, sample_rate)
    for buf in izip(*[samples]*sample_rate):  # write several samples at a time
        stream.write(bytes(bytearray(buf)))
    # fill remainder of frameset with silence
    stream.write(b'\x80' * restframes)

    stream.stop_stream()
    stream.close()
    p.terminate()
