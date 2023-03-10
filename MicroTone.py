import os
import pygame


# :D
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


import pyaudio

from oscillators import *
from signals import Combine, Constant, ADSR, ADSREnvelope, Incremental, Signal
from events import EventGenerator, LocalKeyboard, Join

from keyboardserver.kbserver import RemoteKeyboard
# from filters import AverageWindow

import numpy as np

from itertools import count

import yaml


# open the window
WIDTH, HEIGHT = 800, 600
FULLSCREEN = False

AUDIO_BUFFER = 256 * 3
SAMPLE_RATE = Oscillator.SAMPLE_RATE



MAX_VOL = 0.8
OSCILLATOR_AMP = .2
SETTINGS = {}
CODES = {}
freqFromCode = None



def loadSettings(settingsfile):
    global SETTINGS, freqFromCode
    # load general settings
    with open(settingsfile, 'r') as f:
        SETTINGS = yaml.unsafe_load(f)
    
    
    # load function to get frequency from the keycode
    freqFromCode = eval(SETTINGS['FreqsSystem'])
    

def sphericalOscScope(t,v):
    R = 200
    T0 = SAMPLE_RATE/freqFromCode(60)    # sistemare
    ex = 400
    ey  = 300
    ez = -800

    x = R * np.cos(np.pi*2*v/HEIGHT)*np.cos(2*np.pi*t/T0)
    y = R * np.sin(np.pi*2*v/HEIGHT)
    z = R * np.cos(np.pi*2*v/HEIGHT)*np.sin(2*np.pi*t/T0)
    
    l = ez/(ez-z)
    xp = ex + (l * x - ex) + ex
    yp = ey + (l * y - ey) + ey
    return (xp, yp)

## test
def hsv_to_rgb(h, s, v):
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h >= 0 and h < 60:
        r, g, b = (c, x, 0)
    elif h >= 60 and h < 120:
        r, g, b = (x, c, 0)
    elif h >= 120 and h < 180:
        r, g, b = (0, c, x)
    elif h >= 180 and h < 240:
        r, g, b = (0, x, c)
    elif h >= 240 and h < 300:
        r, g, b = (x, 0, c)
    else:
        r, g, b = (c, 0, x)

    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)

    return (r, g, b)
## /test


def defaultKeySound(keySignal, frequency):
    return Combine(
            ADSREnvelope(SETTINGS['ALen'], SETTINGS['DLen'], SETTINGS['SLev'], SETTINGS['RLen'], control = keySignal),
            SawTooth(frequency),
            # Sine(4),
            # Triangle(10),
            # by = lambda sigs: Signal.control([sigs[0], sigs[1] * sigs[2]])
            by = Oscillator.control
        )

## just a beautiful sound. Temporally wrote down here
# Combine(
                        #     ADSREnvelope(SETTINGS['ALen'], SETTINGS['DLen'], SETTINGS['SLev'], SETTINGS['RLen'], control = kSign),
                        #     Square(freqFromCode(note)),
                        #     Triangle(freqFromCode(note)),
                        #     # Triangle(10),
                        #     by = lambda sigs: Signal.control([sigs[0], sigs[1] * sigs[2]])
                        #     # by = Oscillator.control
                        # )
##



if __name__ == "__main__":

    # Pygame initialization
    pygame.init()


    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN) if FULLSCREEN else pygame.display.set_mode((WIDTH, HEIGHT))

    # Pyaudio initialization
    st = pyaudio.PyAudio().open(SAMPLE_RATE, 1, pyaudio.paInt16, output = True, frames_per_buffer = AUDIO_BUFFER)


    loadSettings('settings.yaml')

    x = 0
    y0 = 0


    try:
        playback = Combine(completeInput = False, by = np.sum)
        
        keysignals = {}
        
        # main loop ending flag
        done = False
        frame = 0

        pyeventgen = LocalKeyboard(pygame)
        # pyeventgen = Join(LocalKeyboard(pygame), RemoteKeyboard())
        # pyeventgen = RemoteKeyboard()

        while not done:
            # event handling
            for event in pyeventgen.get():
                if event == EventGenerator.END:
                    done = True
                elif event[0] == 'KEY_DOWN':
                    
                    kSign = Constant(1)
                    keysignals[event[1]] = kSign
                    
                    playback.add(defaultKeySound(kSign, freqFromCode(event[1])))

                elif event[0] == 'KEY_UP':
                    # remove oscillator for released key
                    kSign = keysignals[event[1]]
                    kSign.setVal(None)
                
                # NOTE: one could take this off. keysignals don't grow much
                # keysignals = dict((k,v) for (k,v) in keysignals.items() if v.val)

            # write to audio out
            buffer = []
            for _ in range(AUDIO_BUFFER):
                
                v = next(playback) * OSCILLATOR_AMP

                buffer.append(v * 32767)
                
                if x == int(SAMPLE_RATE/freqFromCode(60)):#WIDTH:
                    x = 0
                    frame += 1
                
                x += 1
                
                if x % 6 == 0:
                    y = (v + .5) * HEIGHT
                    # pygame.draw.line(SCREEN, pygame.Color(20, 200, 30), (x-6,y0), (x,y))
                    
                    r, g, b = hsv_to_rgb(72*(y-y0), 1, 1)
                    
                    pygame.draw.line(SCREEN, pygame.Color(r, g, b), sphericalOscScope(x-6,y0), sphericalOscScope(x,y))
                    y0 = y

            st.write(np.int16(buffer).tobytes())
                
            if frame >= 10:
                frame = 0
                pygame.display.flip()
                SCREEN.fill(pygame.Color(0,0,0))
        
        # we're done
        pyeventgen.close()


    except KeyboardInterrupt as err:
        st.close()
        playback.close()

    # close pygame
    pygame.quit()
