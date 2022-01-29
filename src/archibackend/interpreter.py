"""
The purpose of this file is to validate, clean, and process the request received through the flask framework.
It should only really expose one function, which will raise errors as appropriate, or return the results.
"""
import re
import os
import json

from flask import abort

import archibackend.api

INJECT_REGEX = "^[a-zA-Z0-9 ]+$"

with open(os.path.join(os.path.dirname(__file__), "config", "returnvalues.json")) as infile:
    RETURNFIELD_CONFIG = json.load(infile)

def interpret(data):
    try:
        data = _structure(data)
        _inchect(data)
        return _callApi(data)
    except Exception as e:
        print("ERROR")
        print(e)
        raise



def _structure(data):
    # no application/json header...
    # or DB table not specified
    # or DB table has no returnfields configured.
    if not data.is_json\
       or not "table" in data.json\
       or not data.json["table"] in RETURNFIELD_CONFIG:
        abort(400)
    return data.json

def _inchect(data):
    try:
        for key, value in data.items():
            assert(re.match(INJECT_REGEX, key))
            assert(re.match(INJECT_REGEX, value))
    except AssertionError:  # String contains special characters
        abort(400)
    except TypeError:
        abort(400)  # value is not a string...

def _callApi(data):
    db = archibackend.api.Archibase()
    table = data.pop("table")
    result = db.select(table, data, RETURNFIELD_CONFIG[table])
    db.close()
    print(result)
    lineitems = []
    for value in result:
        lineitems.append(dict(zip(RETURNFIELD_CONFIG[table], value)))
    return lineitems
