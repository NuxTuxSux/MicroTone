from signals import Signal
import numpy as np

SAMPLE_RATE = 44100


class Oscillator(Signal):
    # need to make all continuous' parameters pluggable by other signals
    def __init__(self, freq, fun, T, phase = 0, **kwargs):
        super().__init__(**kwargs)
        # self.freq = freq      # maybe this will be useful later on
        # self.T = T
        self.fun = fun
        self.phase = phase
        self.t = phase
        self.delta = T * freq / SAMPLE_RATE
    
    
    def step(self):
        self.t += self.delta
        self.val = self.fun(self.t)

def Sine(freq, **kwargs):
    return Oscillator(freq, fun = np.sin, T = 2 * np.pi, **kwargs)

