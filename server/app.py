from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import make_response
from utils import *

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
            

@app.route('/chat', methods=['POST'])
def chat():
    question = request.json['question']
    response_text = ask(question)
    response = make_response(jsonify({'response': response_text}), 200)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

@app.route('/hello', methods=['POST'])
def hello():
    response_text = 'hello saatva chatbot'
    response = make_response(jsonify({'response': response_text}), 200)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Credentials"] = "true"

    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    