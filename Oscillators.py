class Wave:
    
    def __init__(self, attack_len, decay_len, sustain_level, release_len, oscillator, amplitude) -> None:
        self.attack_len = attack_len
        self.decay_len = decay_len
        self.sustain_level = sustain_level
        self.release_len = release_len
        self.oscillator = oscillator
        self.amplitude = amplitude
        self.state = 'ATTACK'
        self.i = 0
        self.value = 0
    
    def release(self):
        self.state = True
    
    def __next__(self):
        if self.state == 'ATTACK':
            self.value = self.i * self.oscillator(self.i) / self.attack_len
        elif self.state == 'DECAY':
            self.value = 1 - (self.i - self.attack_len) * 

        
        



class Oscillators:
    def __init__(self) -> None:
        self.waves = []
    def addWave(self, key, wave):
        self.waves[key] = wave
    def release(self, key):
        self.waves[key].release()