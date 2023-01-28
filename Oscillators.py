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
    hpi = 3.14/2
    def apprSin(t):
        t %= 6.283
        if t > hpi:
            t = 3.14-t
        # return t-t*t*t/6+t*t*t*t*t/120-t*t*t*t*t*t*t/5040
        ts = t*t
        return t*(1-ts*(.166667-ts*(.008333-.000198*ts)))
    # return Oscillator(freq, fun = np.sin, T = np.pi, **kwargs)
    return Oscillator(freq, fun = apprSin, T = np.pi, **kwargs)

def SawTooth(freq, **kwargs):
    return Oscillator(freq, fun = lambda t: (t % 2) - 1, T = 1, **kwargs)

# def Trapezoidal(freq, alpha, beta, **kwargs):
    # tr = Conj(
        # Incremental(1, alpha)
    # )
