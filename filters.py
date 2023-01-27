from signals import Signal
from queue import Queue

class AverageWindow(Signal):
    def __init__(self, signal, windowSize = 300):
        self.signal = signal
        self.window = Queue()
        self.windowSize = windowSize
        self.sum = 0
        for _ in range(windowSize):
            self.window.put(0)
    
    def step(self):
        nextSig = next(self.signal)
        self.window.put(nextSig)
        dropped = self.window.get()
        self.sum += nextSig - dropped
        self.val = self.sum / self.windowSize
        