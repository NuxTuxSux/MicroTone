import itertools, abc
from abc import ABC, abstractmethod, abstractproperty

class Signal(ABC):
    # an abastract class wich describe a general signal
    # meglio definire active e next

    # @abstractproperty
    # def val(self):
        # present value of the signal
        # pass

    def __init__(self, control = None):
        self.active = True
    
    @abstractmethod
    def __next__(self):
        pass

    @property
    def control(self):
        pass

    # def __rshift__(self, other):
        # res = None

class Conj(Signal):
    def __init__(self, *signals):
        super().__init__()
        self.signals = signals
    
    def __next__(self):
        if self.signals:
            if self.signals[0].active:
                return next(self.signals[0])
            else:
                self.signals = self.signals[1:]
                return next(self)
        else:
            self.active = False
            return None
        

class Linear(Signal):
    def __init__(self, a, b, lenght):
        super().__init__()
        self.val = a
        self.length = lenght
        self.i = 0
        self.step = (b-a)/lenght
    
    def __next__(self):
        if self.active:
            if self.i >= self.length - 1:
                self.active = False
            v = self.val
            self.val += self.step
            self.i += 1
            return v
        else:
            return None

class Seq(Signal):
    def __init__(self, seq):
        super().__init__()
        self.seq = seq
    
    def __next__(self):
        # questo potrebbe essere il pattern generico di __next__, mi basta definire active e nextval e aggiungere anche il controllo
        if self.active:
            self.val = self.seq[0]
            self.seq = self.seq[1:]
            if not self.seq:
                self.active = False
            return self.val
        else:
            return None



# def ADSR(Signal):
    # def __init__(self, Alen, Dlen, Slev, Rlen):

x = Linear(10, 2, 8)
y = Linear(2, 4, 3)
z = Conj(x,Seq([1,2,3,4]),y)