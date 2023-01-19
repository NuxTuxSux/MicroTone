import pygame
from pygame import midi

import pyaudio

from oscillators import Sine, Oscillator
from signals import Silence, Combine, ADSR, Loop

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
OSCILLATOR_AMP = .2
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
        # print(kcds)
        for keyname in kcds:
            CODES[getattr(pygame, 'K_' + str(keyname))] = kcds[keyname]
    
    # load function to get frequency from the keycode
    freqFromCode = eval(SETTINGS['FreqsSystem'])
    




loadSettings('settings.yaml')
try:
    playback = Silence(amplitude = MAX_VOL)
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
                    kSign = Loop([1])
                    keysignals[event.key] = kSign
                    next(kSign)
                    
                    playback.add(event.key,
                        Combine({
                            # 'env': ADSR(10, 10, 0.9, 40, amplitude = 1.),
                            'osc': Sine(freqFromCode(note), amplitude = OSCILLATOR_AMP, control = kSign)
                            },
                            by = np.prod
                        )
                        # Sine(freqFromCode(note), amplitude = OSCILLATOR_AMP, control = kSign)

                    )

            if event.type == pygame.KEYUP:
                print([keysignals[k].seq for k in keysignals])
                if event.key in CODES:
                    # remove oscillator for released key
                    # playback.remove(event.key)
                    kSign = keysignals[event.key]
                    kSign.seq = [0]
            
            print(keysignals)
            playback.flush()

        # write to audio out
        buffer = []
        for _ in range(256):
            for k in keysignals:
                next(keysignals[k])
            v = next(playback)
            print(v)
            buffer.append(int((v if v else 0) * 32767))

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
