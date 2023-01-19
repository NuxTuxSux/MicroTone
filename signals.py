import itertools, abc
import numpy as np
from abc import ABC, abstractmethod, abstractproperty

class Signal(ABC):
    # an abastract class wich describe a general signal
    
    def __init__(self, control = None, amplitude = .9):
        # set the control signal and the initial value
        # NOTE: a signal don't consume its control (useful for attaching a control to several signals)
        self.control = control
        self.amplitude = amplitude
        self.val = None

    @property
    def _controlValue(self):
        # returns the control value (or true if there's no control)
        return self.control == None or self.control.val
    
    @property
    def active(self):
        # Tells if the signal is active, based on its status or controls
        return self._controlValue and self.hasNext()

    def __next__(self):
        if self.active:
            self._step()
            return self.amplitude * self.val
        #     v = self.val
        #     self._step()
        # else:
        #     v = None
        # return v
    
    
    def setStart(self, _):
        pass

    @abstractmethod
    def _step(self):
        # update any eventual state and signal value
        # should be called only if signal is active
        pass
    
    @abstractmethod
    def hasNext(self):
        # tells if signal can output another value
        pass


class Seq(Signal):
    # make a signal out of a sequence
    def __init__(self, seq, **kwargs):
        super().__init__(**kwargs)
        self.seq = seq
#        if self.seq:
 #           self._step()

    def hasNext(self):
        return len(self.seq) > 0

    def _step(self):
        self.val = self.seq[0]
        self.seq = self.seq[1:]

class Incremental(Signal):
    
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.i = 0
        if len(args) == 2:
            self.stop = args[0]
            self.length = args[1]
            self.setStart(0)
        elif len(args) == 3:
            self.stop = args[1]
            self.length = args[2]
            self.setStart(args[0])
        
    def setStart(self, start):
        # not the best way I guess
        if start != None:
            self.delta = (self.stop - start) / self.length
            self.val = start - self.delta

    def _step(self):
        self.i += 1
        self.val += self.delta
    
    def hasNext(self):
        return self.i <= self.length

class Conj(Signal):
    def __init__(self, *signals, **kwargs):
        super().__init__(**kwargs)
        self.signals = signals
    
    def hasNext(self):
        return self.signals and self.signals[0].hasNext()

    def _step(self):
        if self.signals[0].active:
            self.val = next(self.signals[0])
        else: 
            self.signals = self.signals[1:]
            if self.signals:
                self.signals[0].setStart(self.val)
                self.val = next(self.signals[0])
            else:
                self.val = None

class Loop(Signal):
    # make a signal looping over a sequence
    def __init__(self, seq, **kwargs):
        super().__init__(**kwargs)
        self.seq = seq
        self.i = 0

    def hasNext(self):
        return True

    def _step(self):
        self.val = self.seq[self.i]
        self.i = (self.i + 1) % len(self.seq)


class Combine(Signal):
    # modificare in modo che elimini i segnali morti
    def __init__(self, signals = {}, by = np.sum, **kwargs):
        super().__init__(**kwargs)
        if signals:
            self.signals = signals
        else:
            self.signals = {}
        self.by = by
    
    def hasNext(self):
        return all(signal.hasNext() for _, signal in self.signals.items())
    
    def add(self, key, signal):
        self.signals[key] = signal

    def remove(self, key):
        del self.signals[key]

    def _step(self):
        self.val = self.by(list(filter(lambda x: x != None, [next(signal) for _, signal in self.signals.items()])))
    
    def flush(self):
        self.signals = dict([(k,v) for k,v in self.signals.items() if v.active])


def ADSR(Alen, Dlen, Slev, Rlen, *, control, **kwargs):
    return Conj(
        Incremental(1, Alen, control = control, **kwargs),
        Incremental(Slev, Dlen, control = control, **kwargs),
        Loop([Slev], control = control, **kwargs),
        Incremental(0, Rlen, **kwargs)
    )

def Silence(**kwargs):
    return Combine(**kwargs)


x = Incremental(10, 2, 8)
y = Incremental(2, 4, 3)
c = Seq([True, True, True, True, True, True, True, True, True, True, True, False, False])
z = Conj(x,Seq([1,2,3,4,5,6], control = c),y)

AL = 4
DL = 2
SL = 0.5
RL = 6

ctrl = Seq([True]*13 + [False] * 3)
a = Incremental(8, 2, control = ctrl)
b = Incremental(2,4, control = ctrl)
s = Conj(a,b)

c = Seq([True]*4+[False]*2)
i = Incremental(-1,4)
l = Loop([0,1],control = c)
x = Conj(l,i)
