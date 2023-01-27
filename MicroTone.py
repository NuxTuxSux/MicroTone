import pygame
from pygame import midi

import pyaudio

from oscillators import *
from signals import Combine, Constant, ADSR, Incremental, Signal
# from filters import AverageWindow

import numpy as np

from itertools import count

import yaml
# Pygame initialization
pygame.init()

# open the window
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
AUDIO_BUFFER = 256 * 4

# Pyaudio initialization
st = pyaudio.PyAudio().open(44100, 1, pyaudio.paInt16, output = True, frames_per_buffer = AUDIO_BUFFER)




MAX_VOL = .7
OSCILLATOR_AMP = .3
SETTINGS = {}
CODES = {}
freqFromCode = None




def loadSettings(settingsfile):
    global SETTINGS, CODES, freqFromCode
    # load general settings
    with open(settingsfile, 'r') as f:
        SETTINGS = yaml.unsafe_load(f)
    
    # load keycodes
    with open(SETTINGS['KeyCodes'], 'r') as f:
        kcds = yaml.safe_load(f)
        for keyname in kcds:
            CODES[getattr(pygame, 'K_' + str(keyname))] = kcds[keyname]
    
    # load function to get frequency from the keycode
    freqFromCode = eval(SETTINGS['FreqsSystem'])
    




loadSettings('settings.yaml')

x = 0
nframes = 0
# recording = []

try:
    playback = Combine(completeInput = False)
    # filteredPlayback = AverageWindow(playback)

    keysignals = {}
    # main loop
    done = False
    frame = 0
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
                            ADSR(SETTINGS['ALen'], SETTINGS['DLen'], SETTINGS['SLev'], SETTINGS['RLen'], control = kSign),
                            Sine(freqFromCode(note)),
                            by = Signal.control
                        )
                    )

            if event.type == pygame.KEYUP:
                if event.key in CODES:
                    # remove oscillator for released key
                    kSign = keysignals[event.key]
                    kSign.setVal(None)
            
            # NOTE: flush the key dict?

        # write to audio out
        buffer = []
        for fr in range(AUDIO_BUFFER):
            # NOTE: before here there was a check for next value not being None, now it should be useless
            # moreover I was converting the output to int via int() but I guess numpy was doing the job immediately after
            # v = max(-MAX_VOL, min(next(playback) * OSCILLATOR_AMP, MAX_VOL))

            v = next(playback) * OSCILLATOR_AMP

            buffer.append(v * 32767)
            # recording.append(v * 32767)

            if x == WIDTH-1:
                x = 0
                nframes += 1
                pygame.display.flip()
                SCREEN.fill(pygame.Color(0,0,0))
            else:
                x += 1
            
            y = int((v + 0.5) * HEIGHT)

            SCREEN.set_at((x, y), pygame.Color(20, 200, 30))

        st.write(np.int16(buffer).tobytes())




except KeyboardInterrupt as err:
    st.close()

# close pygame
pygame.quit()
