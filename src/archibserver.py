from pprint import pprint as pp
from flask import Flask, request, jsonify
from flask_cors import CORS
from archibackend.interpreter import interpret

FLASK_PORT = 44361
FLASK_HOST = "0.0.0.0"

FLASK_APP = Flask(__name__)
CORS(FLASK_APP)


@FLASK_APP.route('/')
def base():
    return "Undefined endpoint"


@FLASK_APP.route('/search', methods=['POST'])
def search():
    pp(request.data)
    response = jsonify(interpret(request))
    return response


def launch():
    """
    Launch function as defined by AIGIS convention
    """
    FLASK_APP.run(port=FLASK_PORT, host=FLASK_HOST)


if __name__ == "__main__":  # For manual testing
    FLASK_APP.run(port=5077, host=FLASK_HOST)