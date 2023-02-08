import sys
import os
 
from flask import Flask, request, render_template
# from multiprocessing import Process, Queue
from queue import Queue
from threading import Thread

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)

from events import EventGenerator

class RemoteKeyboard(EventGenerator):

    def startServer(queue):
        server = Flask(__name__)
        
        @server.route('/')
        def index():
            return render_template('index.html')
    
        @server.route('/submit', methods=['POST'])
        def submit():
            print(queue.get())
            data = request.get_data().decode('ascii')
            print(data.split(':'))
            return ""

        server.run(debug = True, host = '0.0.0.0', port = 80)



    def __init__(self):
        self.comm = Queue()
        self.comm.put(23)
        self.server = Thread(target = RemoteKeyboard.startServer, args = (self.comm,))
        self.server.start()

        
        
    
    def get(self):
        # print('cosa vuoi di già?')
        return []
