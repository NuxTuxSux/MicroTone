from signals import Signal, Incremental, Conj, Loop
import numpy as np



class Oscillator(Signal):
    SAMPLE_RATE = 44100

    # need to make all continuous' parameters pluggable by other signals
    def __init__(self, freq, fun, T, phase = 0, **kwargs):
        super().__init__(**kwargs)
        # self.freq = freq      # maybe this will be useful later on
        # self.T = T
        self.fun = fun
        self.phase = phase
        self.t = phase
        self.delta = T * freq / Oscillator.SAMPLE_RATE
    
    
    def step(self):
        self.t += self.delta
        self.val = self.fun(self.t)

def Sine(freq, **kwargs):
    hpi = 1.570795
    # def apprSin(t):
    #     t %= 6.283
    #     if t > hpi:
    #         t = 3.1415-t
    #     # return t-t*t*t/6+t*t*t*t*t/120-t*t*t*t*t*t*t/5040
    #     ts = t*t
    #     return t*(1-ts*(.166667-ts*(.008333-.000198*ts)))
    return Oscillator(freq, fun = np.sin, T = 2*np.pi, **kwargs)
    # return Oscillator(freq, fun = apprSin, T = 2*np.pi, **kwargs)

def SawTooth(freq, **kwargs):
    return Oscillator(freq, fun = lambda t: (t % 2) - 1, T = 1, **kwargs)


def Triangle(freq, **kwargs):
    def trf(x):
        x = x % 4
        if x < 2:
            return x - 1
        else:
            return 3 - x
    return Oscillator(freq, fun = trf, T = 4, **kwargs)


def Square(freq, **kwargs):
    return Oscillator(freq, fun = lambda t: 1 if t%1 < .5 else -1, T = 1, **kwargs)


# def Trapezoidal(freq, alpha, beta, **kwargs):
    # tr = Conj(
        # Incremental(1, alpha)
    # )
