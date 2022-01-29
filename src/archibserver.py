from pprint import pprint as pp
from flask import Flask, request, jsonify
from flask_cors import CORS
from archibackend.interpreter import interpret

FLASK_PORT = 5077
FLASK_HOST = "0.0.0.0"

FLASK_APP = Flask(__name__)
CORS(FLASK_APP)

@FLASK_APP.route('/')
def base():
    return "Undefined endpoint"

@FLASK_APP.route('/search', methods=['POST'])
def search():
    pp(request.data)
    print("Test")
    response = jsonify(interpret(request))
    return response


if __name__ == "__main__":
    FLASK_APP.run(port=FLASK_PORT, host=FLASK_HOST)