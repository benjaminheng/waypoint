#!/usr/bin/env python
"""Play a fixed frequency sound."""
from __future__ import division
import math
import numpy as np
from threading import Thread

from pyaudio import PyAudio
from itertools import izip, count


def get_samples(frequency, volume, sample_rate, n_samples):
    samples = (
        int(
            (volume * math.sin(2 * math.pi * frequency * t / sample_rate)) *
            0x7f + 0x80
            # math.sin(2 * math.pi * frequency * t / sample_rate)
        )
        for t in xrange(n_samples)  # NOQA
    )
    return samples


def normalize(sample, volume):
    return int(sample * volume * 0x7f + 0x80)


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

    def sine_wave(self, frequency=440.0, framerate=44100, amplitude=0.5):
        if amplitude > 1.0:
            amplitude = 1.0
        if amplitude < 0.0:
            amplitude = 0.0
        return (
            # float(amplitude) *
            math.sin(2.0*math.pi*float(frequency)*(float(i)/float(framerate)))
            for i in count(0)
        )

    def run(self):
        n_samples = int(self.sample_rate * 3600)  # 1 hour length
        # restframes = n_samples % self.sample_rate
        samples = get_samples(
            self.frequency, self.volume, self.sample_rate, n_samples
        )
        while True:
            # write several samples at a time
            fs = 44100       # sampling rate, Hz, must be integer
            duration = 1.0   # in seconds, may be float
            f = 440.0        # sine frequency, Hz, may be float

            # generate samples, note conversion to float32 array
            # samples = (
            #     (np.sin(2*np.pi*np.arange(fs*duration)*f/fs))
            #     .astype(np.float32)
            # )
            self.stream.write(self.volume*samples)


if __name__ == '__main__':
    tone = Tone()
    tone.start()
    while True:
        pass
