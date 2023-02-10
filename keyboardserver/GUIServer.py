from flask import Flask, request, render_template
import socket

SYNTH_PORT = 50000
PACKET_SIZE = 8


if __name__ == "__main__":
    server = Flask(__name__)
    toSynthServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'Connecting to synth on port {SYNTH_PORT}')
    toSynthServer.connect(('0.0.0.0', SYNTH_PORT))
    
    @server.route('/')
    def index():
        return render_template('index.html')
    
    @server.route('/submit', methods=['POST'])
    def submit():
        data = request.get_data().decode('ascii').ljust(PACKET_SIZE,' ')
        toSynthServer.sendall(data.encode())
        return ""

    server.run(debug = False, host = '0.0.0.0', port = 80, use_reloader = False)
