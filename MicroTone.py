import pygame
from pygame import midi

import math

import colorsys

import pyaudio

from oscillators import *
from signals import Combine, Constant, ADSR, ADSREnvelope, Incremental, Signal
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
SAMPLE_RATE = Oscillator.SAMPLE_RATE

# Pyaudio initialization
st = pyaudio.PyAudio().open(SAMPLE_RATE, 1, pyaudio.paInt16, output = True, frames_per_buffer = AUDIO_BUFFER)

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


MAX_VOL = .9
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




loadSettings('settings.yaml')

x = 0
y0 = 0

# recording = []

def mymean(args):
    if len(args):
        return np.mean(args)
    else:
        return 0

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
                            ADSREnvelope(SETTINGS['ALen'], SETTINGS['DLen'], SETTINGS['SLev'], SETTINGS['RLen'], control = kSign),
                            Square(freqFromCode(note)),
                            # SawTooth(freqFromCode(note)),
                            # Triangle(10),
                            # by = lambda sigs: Signal.control([sigs[0], sigs[1] * sigs[2]])
                            # by = Oscillator.control
                        )
                    )

            if event.type == pygame.KEYUP:
                if event.key in CODES:
                    # remove oscillator for released key
                    kSign = keysignals[event.key]
                    kSign.setVal(None)
            
            # NOTE: maybe one can take this off. keysignals don't grow much
            # keysignals = dict((k,v) for (k,v) in keysignals.items() if v.val)

        # write to audio out
        buffer = []
        for _ in range(AUDIO_BUFFER):
            # NOTE: before here there was a check for next value not being None, now it should be useless
            # moreover I was converting the output to int via int() but I guess numpy was doing the job immediately after
            # v = max(-MAX_VOL, min(next(playback) * OSCILLATOR_AMP, MAX_VOL))

            v = next(playback) * OSCILLATOR_AMP

            buffer.append(v * 32767)
            # recording.append(v * 32767)

            if x == int(SAMPLE_RATE/freqFromCode(60)):#WIDTH:
                x = 0
                frame += 1
                # print(frame)

            x += 1
            
            
            if x % 6 == 0:
                # y = int((v + .5) * HEIGHT)
                y = (v + .5) * HEIGHT
                # pygame.draw.line(SCREEN, pygame.Color(20, 200, 30), (x-6,y0), (x,y))
                
                r, g, b = hsv_to_rgb(72*(y-y0), 1, 1)
                colore = pygame.Color(r, g, b)

                # if y-y0:
                    # print(y-y0)                
                pygame.draw.line(SCREEN, colore, sphericalOscScope(x-6,y0), sphericalOscScope(x,y))
                # pygame.draw.line(SCREEN, pygame.Color(20, 200, 30), sphericalOscScope(x-6,y0), sphericalOscScope(x,y))
                y0 = y
            # SCREEN.set_at((x, y), pygame.Color(20, 200, 30))
            
            

        st.write(np.int16(buffer).tobytes())

            
        if frame >= 4:
            frame = 0
            pygame.display.flip()
            SCREEN.fill(pygame.Color(0,0,0))



except KeyboardInterrupt as err:
    st.close()

# close pygame
pygame.quit()
