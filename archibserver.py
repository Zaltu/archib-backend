from pprint import pprint as pp
from flask import Flask, request
from archibackend.interpreter import interpret

FLASK_PORT = 5077
FLASK_HOST = "0.0.0.0"

FLASK_APP = Flask(__name__)


@FLASK_APP.route('/')
def base():
    return "Undefined endpoint"

@FLASK_APP.route('/search', methods=['POST'])
def search():
    pp(request.form)
    return interpret(request)


if __name__ == "__main__":
    FLASK_APP.run(port=FLASK_PORT, host=FLASK_HOST)