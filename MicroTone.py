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
st = pyaudio.PyAudio().open(44100, 1, pyaudio.paInt16, output=True, frames_per_buffer=256)

# dizionario per memorizzare gli oscillatori
nd = {}

# dizionario per mappare i tasti della tastiera a delle note
key_to_note = {
    pygame.K_a: 60,  # nota C
    pygame.K_w: 61,  # nota C#
    pygame.K_s: 62,  # nota D
    pygame.K_e: 63,  # nota D#
    pygame.K_d: 64,  # nota E
    pygame.K_f: 65,  # nota F
    pygame.K_t: 66,  # nota F#
    pygame.K_g: 67,  # nota G
    pygame.K_y: 68,  # nota G#
    pygame.K_h: 69,  # nota A
    pygame.K_u: 70,  # nota A#
    pygame.K_j: 71,  # nota B
    pygame.K_k: 72,  # nota C (ottava successiva)
}



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
                if event.key in key_to_note:
                    # ottieni la nota corrispondente al tasto premuto
                    note = key_to_note[event.key]

                    # aggiungi un oscillatore per il tasto premuto
                    nd[event.key] = (
                        sin(c) * 0.1
                        for c in count(0, (2 * pi * midi.midi_to_frequency(note)) / 44100)
                    )
            if event.type == pygame.KEYUP:
                # verifica se il tasto premuto è stato rilasciato
                if event.key in key_to_note:
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
