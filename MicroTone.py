import pygame
from pygame import midi

import pyaudio

import numpy as np
from math import pi, sin

from itertools import count

import yaml
# inizializza Pygame
pygame.init()

# apre la finestra
screen = pygame.display.set_mode((400, 300))

# inizializza Pyaudio
st = pyaudio.PyAudio().open(44100, 1, pyaudio.paInt16, output = True, frames_per_buffer = 256)

# dizionario per memorizzare gli oscillatori
nd = {}

# dizionario per mappare i tasti della tastiera a delle note

VOLUME = 0.9
SETTINGS = {}
CODES = {}
freqFromCode = None

def loadSettings(settingsfile):
    global SETTINGS, CODES, freqFromCode
    # load general settings
    with open(settingsfile, 'r') as f:
        SETTINGS = yaml.unsafe_load(f)
    
    # print(SETTINGS)

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
    # ciclo principale
    done = False
    while not done:
        # gestisci gli eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                # verifica se il tasto Escape è stato premuto
                if event.key == pygame.K_ESCAPE:
                    done = True

                # verifica se il tasto premuto è presente nel dizionario
                if event.key in CODES:
                    # ottieni la nota corrispondente al tasto premuto
                    note = CODES[event.key]

                    # aggiungi un oscillatore per il tasto premuto
                    nd[event.key] = (
                        sin(c) * VOLUME / len(nd)
                        # ((c/pi/2)%2 - 1) * VOLUME / len(nd)
                        for c in count(0, (2 * pi * freqFromCode(note)) / 44100)
                    )
            if event.type == pygame.KEYUP:
                # verifica se il tasto premuto è stato rilasciato
                if event.key in CODES:
                    # rimuovi l'oscillatore per il tasto rilasciato
                    del nd[event.key]

        # scrivi i dati audio
        if nd:
            st.write(
                np.int16(
                    [
                        sum([int(next(osc) * 32767) for _, osc in nd.items()])
                        for _ in range(256)
                    ]
                ).tobytes()
            )

except KeyboardInterrupt as err:
    st.close()

# chiudi Pygame e Pyaudio
pygame.quit()
