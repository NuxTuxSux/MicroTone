import pygame
from pygame import midi

import pyaudio

from oscillators import Sine, Oscillator
from signals import Combine, Constant, ADSR, Incremental, Signal

import numpy as np

from itertools import count

import yaml
# Pygame initialization
pygame.init()

# open the window
screen = pygame.display.set_mode((400, 300))

# Pyaudio initialization
st = pyaudio.PyAudio().open(44100, 1, pyaudio.paInt16, output = True, frames_per_buffer = 256)




MAX_VOL = .9
OSCILLATOR_AMP = .3
SETTINGS = {}
CODES = {}
freqFromCode = None


# test constants
ALen = 100
DLen = 1200
SLev = 0.4
RLen = 3000
#



def loadSettings(settingsfile):
    global SETTINGS, CODES, freqFromCode
    # load general settings
    with open(settingsfile, 'r') as f:
        SETTINGS = yaml.unsafe_load(f)
    
    # load keycodes
    with open(SETTINGS['KeyCodes'], 'r') as f:
        kcds = yaml.safe_load(f)
        # print(kcds)
        for keyname in kcds:
            CODES[getattr(pygame, 'K_' + str(keyname))] = kcds[keyname]
    
    # load function to get frequency from the keycode
    freqFromCode = eval(SETTINGS['FreqsSystem'])
    




loadSettings('settings.yaml')
try:
    playback = Combine(completeInput = False)
    keysignals = {}
    # main loop
    done = False
    while not done:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                # check for ESC keypress
                if event.key == pygame.K_ESCAPE:
                    done = True

                # check if the pressed key is in our keyboard dict
                if event.key in CODES:
                    # get the note corresponding to pressed key
                    note = CODES[event.key]

                    # NOTE: DEFINE THE KEYSIGNALS AND USE THEM TO CONTROL THE OSCILLATORS
                    kSign = Constant(1)
                    keysignals[event.key] = kSign
                    
                    playback.add(
                        Combine(
                            ADSR(ALen, DLen, SLev, RLen, control = kSign),
                            Sine(freqFromCode(note)),
                            by = Signal.control
                        )

                    )

            if event.type == pygame.KEYUP:
                # print([keysignals[k].seq for k in keysignals])
                if event.key in CODES:
                    # remove oscillator for released key
                    # playback.remove(event.key)
                    kSign = keysignals[event.key]
                    kSign.setVal(None)
            
            # NOTE: flush the key dict?

        # write to audio out
        buffer = []
        for _ in range(256):
            v = next(playback)
            buffer.append(int((v if v != None else 0) * 32767) * OSCILLATOR_AMP)
        # if any(buffer):
            # print(buffer)
        st.write(np.int16(buffer).tobytes())
        # st.write(
        #     np.int16(
        #         [
        #             # write 256-values buffer, after having it converted to 16bit int
        #             int(next(playback) * 32767)
        #             for _ in range(256)
        #         ]
        #     ).tobytes()
        # )

except KeyboardInterrupt as err:
    st.close()

# close pygame
pygame.quit()
