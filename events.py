from abc import ABC, abstractmethod, abstractproperty
import pygame
import yaml

from flask import Flask, request, render_template


SETTINGSFILE = 'settings.yaml'

    

class EventGenerator(ABC):

    # I use couple-events
    END = ('END', None)

    def keyDown(self, code):
        return ('KEY_DOWN', code)
    
    def keyUp(self, code):
        return ('KEY_UP', code)
            
    @abstractmethod
    def get(self):
        pass
        

class Join(EventGenerator):
    def __init__(self, EG1, EG2):
        self.EG1 = EG1
        self.EG2 = EG2
    
    def get(self):
        return self.EG1.get() + self.EG2.get()

class LocalKeyboard(EventGenerator):
    def __init__(self, pyG):
        # load keycodes
        self.CODES = {}
        self.pygame = pyG
        with open(SETTINGSFILE, 'r') as f:
            SETTINGS = yaml.unsafe_load(f)
            with open(SETTINGS['KeyCodes'], 'r') as f:
                kcds = yaml.safe_load(f)
                for keyname in kcds:
                    self.CODES[getattr(pygame, 'K_' + str(keyname))] = kcds[keyname]

    def _parseEvent(self, event):
        if event.type == self.pygame.QUIT:
            return EventGenerator.END
        elif event.type == self.pygame.KEYDOWN:
            if event.key == self.pygame.K_ESCAPE:
                return EventGenerator.END
            if event.key in self.CODES:
                return ('KEY_DOWN', self.CODES[event.key])
        elif event.type == self.pygame.KEYUP:
            if event.key in self.CODES:
                return ('KEY_UP', self.CODES[event.key])
        else:
            # just to be more explicit
            return None
    
    def get(self):
        return list(filter(lambda x: x != None, map(self._parseEvent, self.pygame.event.get())))

# class RemoteKeyboard(EventGenerator):
    
#     def __init__(self):
#         self.server = Flask(__name__)

#         @self.server.route('/')
#         def index():
#             return render_template('index.html')

#         @self.server.route('/submit', methods=['POST'])
#         def submit():
#             data = request.get_data().decode('ascii')
#             print(data.split(':'))
#             return ""

#         self.server.run(debug = True, host = '0.0.0.0', port = 80)
    
#     def get(self):
#         print('cosa vuoi di già?')
#         return []



        