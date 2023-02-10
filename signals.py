import itertools, abc
import numpy as np
from abc import ABC, abstractmethod, abstractproperty

class Signal(ABC):
    # an abastract class wich describe a general signal
    
    def control(args):
        # args is [controlValue, signalValue]
        return args[1]*args[0] if args[0] else None

    def __init__(self):
        self.initialized = False
        self.val = None

    def setVal(self, val):
        self.val = val

    def _initialize(self, **kwargs):
        pass

    def initialize(self, **kwargs):
        self._initialize(**kwargs)
        self.initialized = True

    def step(self):
        pass
    
    def __next__(self):
        self.step()
        return self.val
    

class Seq(Signal):
    # make a signal out of a sequence
    def __init__(self, seq, **kwargs):
        super().__init__(**kwargs)
        self.seq = seq

    def step(self):
        if self.seq:
            self.val = self.seq[0]
            self.seq = self.seq[1:]
        

class Incremental(Signal):
    
    def __init__(self, to, len, **kwargs):
        super().__init__(**kwargs)
        self.to = to
        self.len = len

    def _initialize(self, **kwargs):
        self.val = kwargs['val']
        self.delta = (self.to - self.val) / self.len

    def step(self):
        if self.len:
            self.val += self.delta
            self.len -= 1
        else:
            self.val = None
    

class Conj(Signal):
    def __init__(self, *signals, **kwargs):
        super().__init__(**kwargs)
        self.signals = signals
    
    def _initialize(self, **kwargs):
        # self.val = kwargs['val']
        self.signals[0].initialize(**kwargs)

    def step(self):                                 # it works but it's the hugliest piece of code I've ever written. Need to fix that
        if not self.signals:
            self.setVal(None)
        else:
            sig = self.signals[0]
            if not sig.initialized:
                sig.initialize(val = self.val)
            v = next(sig)
            if v == None:
                self.signals = self.signals[1:]
                self.step()
            else:
                self.setVal(v)
    

class Constant(Signal):
    # make a signal looping over a sequence
    def __init__(self, val0, **kwargs):
        super().__init__(**kwargs)
        self.setVal(val0)


class Loop(Signal):
    def __init__(self, signal, **kwargs):
        super().__init__(**kwargs)
        self.signal = signal
        self.sampled = []
        self.sampling = True
        self.i = -1
        self.N = -1

    def _initialize(self, **kwargs):
        self.signal.initialize(val = kwargs['val'])

    def step(self):
        if self.sampling:
            v = next(self.signal)
            if v:
                self.sampled.append(v)
                self.setVal(v)
            else:
                self.sampling = False
                self.N = len(self.sampled)
                self.setVal(self.sampled[0])
                self.i = 0
        else:
            self.i = (self.i + 1) % self.N
            self.setVal(self.sampled[self.i])

class Combine(Signal):
    # modificare in modo che elimini i segnali morti
    def __init__(self, *signals, by = np.sum, completeInput = True, **kwargs):
        super().__init__(**kwargs)
        self.signals = list(signals)                        # I needed to add `list` only implementing RemoteKeyboard. One of the worst bug I ever met. Don't know why now works.
        self.by = by
        self.completeInput = completeInput
            
    def _initialize(self, **kwargs):
        for sig in self.signals:
            sig.initialize(**kwargs)

    def add(self, signal):
        self.signals.append(signal)

    # def remove(self, key):
        # del self.signals[key]

    def step(self):                     # I don't like it
        vs = []
        ss = []
        for sig in self.signals:
            v = next(sig)
            if v != None:
                vs.append(v)
                ss.append(sig)
            else:
                if self.completeInput:
                    self.signals = []
                    self.setVal(None)
                    return


        self.signals = ss
        if len(vs):
            self.setVal(self.by(vs))
        else:
            self.setVal(0)

class ADSREnvelope(Signal):
    # NOTE: Optimize this
    def __init__(self, Alen, Dlen, Slev, Rlen, *, control, **kwargs):
        super().__init__(**kwargs)
        self.t = 0
        self.attack = Incremental(1, Alen)
        self.attack.initialize(val = 0)
        self.decay = Incremental(Slev, Dlen)
        self.release = Incremental(0, Rlen)
        self.Slev = Slev
        self.state = 'A'
        self.control = control
        self.val = 0

    
    def gorelease(self):
        self.state = 'R'
        self.release.initialize(val = self.val)
        return next(self.release)


    def step(self):
        if self.state == 'A':
            if next(self.control):
                v = next(self.attack)
                if v:
                    self.val = v
                else:
                    self.state = 'D'
                    self.decay.initialize(val = self.val)
                    self.val = next(self.decay)
            else:
                self.val = self.gorelease()
        elif self.state == 'D':
            if next(self.control):
                v = next(self.decay)
                if v:
                    self.val = v
                else:
                    self.state = 'S'
                    self.val = self.Slev
            else:
                self.val = self.gorelease()
        elif self.state == 'S':
            if next(self.control):
                self.val = self.Slev
            else:
                self.val = self.gorelease()
        else:
            self.val = next(self.release)

def ADSR(Alen, Dlen, Slev, Rlen, *, control):
    adsr = Conj(
        Combine(
            control,
            Incremental(1, Alen),
            by = Signal.control),
        Combine(
            control,
            Incremental(Slev, Dlen),
            by = Signal.control),
        Combine(
            control,
            Constant(Slev),
            by = Signal.control),
        Incremental(0, Rlen)
    )
    adsr.initialize(val = 0)
    return adsr

