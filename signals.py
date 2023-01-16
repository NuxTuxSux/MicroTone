import itertools, abc
import numpy as np
from abc import ABC, abstractmethod, abstractproperty

class Signal(ABC):
    # an abastract class wich describe a general signal
    
    def __init__(self, control = None):
        # set the control signal and the initial value
        # NOTE: a signal don't consume its control (useful for attaching a control to several signals)
        self.control = control
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
        if self.active and self._controlValue:
            self._step()
            return self.val
        else:
            return None
    
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

    def hasNext(self):
        return len(self.seq) > 0

    def _step(self):
        # questo potrebbe essere il pattern generico di __next__, mi basta definire active e nextval e aggiungere anche il controllo
        self.val = self.seq[0]
        self.seq = self.seq[1:]

class Linear(Signal):
    # def __init__(self, a, b, length, **kwargs):
    #     super().__init__(**kwargs)
    #     self.length = length
    #     self.i = 0
    #     self.delta = (b-a)/length
    #     self.val = a - self.delta
    
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.i = 0
        if len(args) == 2:
            self.stop = args[0]
            self.length = args[1]
            self.startingFrom(0)
        elif len(args) == 3:
            self.stop = args[1]
            self.length = args[2]
            self.startingFrom(args[0])
        
    def startingFrom(self, start):
        self.delta = (self.stop - start) / self.length
        self.val = start - self.delta
        return self

    def _step(self):
        self.i += 1
        self.val += self.delta
    
    def hasNext(self):
        return self.i < self.length

class Conj(Signal):
    def __init__(self, *signals, **kwargs):
        super().__init__(**kwargs)
        self.signals = signals
    
    def hasNext(self):
        return self.signals and self.signals[0].hasNext()

    def _step(self):
        self.val = next(self.signals[0])
        if not self.signals[0].active:
            self.signals = self.signals[1:]

class Combine(Signal):
    def __init__(self, *signals, by = np.sum, **kwargs):
        super().__init__(**kwargs)
        self.signals = signals
        self.by = by
    
    def hasNext(self):
        return all(signal.hasNext() for signal in self.signals)
    
    def _step(self):
        self.val = self.by([next(signal) for signal in self.signals])


# # def ADSR(Signal):
#     # def __init__(self, Alen, Dlen, Slev, Rlen):




x = Linear(10, 2, 8)
y = Linear(2, 4, 3)
c = Seq([True, True, True, True, True, True, True, True, True, True, True, False, False])
z = Conj(x,Seq([1,2,3,4,5,6], control = c),y)