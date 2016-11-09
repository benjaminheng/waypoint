#!/usr/bin/env python
"""Play a fixed frequency sound."""
from __future__ import division
import math
from threading import Thread

from pyaudio import PyAudio
from itertools import izip


def get_samples(frequency, volume, sample_rate, n_samples):
    samples = (
        int(
            # (volume * math.sin(2 * math.pi * frequency * t / sample_rate)) *
            (math.sin(2 * math.pi * frequency * t / sample_rate)) *
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
    samples = get_samples(frequency, volume, sample_rate, n_samples)
    for buf in izip(*[samples]*sample_rate):  # write several samples at a time
        stream.write(bytes(bytearray(buf)))
    # fill remainder of frameset with silence
    stream.write(b'\x80' * restframes)

    stream.stop_stream()
    stream.close()
    p.terminate()


class Tone(Thread):
    def __init__(self, frequency=440.0, volume=0.01, sample_rate=22050):
        super(Tone, self).__init__()
        self.frequency = frequency
        self.volume = volume
        self.sample_rate = sample_rate
        self.audio = PyAudio()
        self.stream = self.audio.open(
            format=self.audio.get_format_from_width(1),  # 8bit
            channels=1,  # mono
            rate=self.sample_rate,
            output=True
        )

    def run(self):
        n_samples = int(self.sample_rate * 3600)  # 1 hour length
        # restframes = n_samples % self.sample_rate
        samples = get_samples(
            self.frequency, self.volume, self.sample_rate, n_samples
        )
        idx = 0
        offset = self.sample_rate / 2   # 0.5sec
        while True:
            # write several samples at a time
            count = 0
            for buf in izip(*[samples]*self.sample_rate):
                self.stream.write(
                    bytes(bytearray([i*self.volume for i in buf]))
                )
                count += 1
                if count >= offset:
                    break
            idx += offset


if __name__ == '__main__':
    tone = Tone()
