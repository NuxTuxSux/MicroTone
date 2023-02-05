from flask import Flask, request, render_template
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_data().decode('ascii')
    print(data.split(':'))
    return ""

if __name__ == '__main__':
    app.run(debug=True)
