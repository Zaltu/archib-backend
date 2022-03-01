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

VALID_PY_TYPES = [str, int, list, bool]

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
    """
    Basic check for SQL injection. Should be replaced by best practices.
    Data loop is a bit convoluted, but checks for any structure allowing:
    {
        "key":, "value",
        "key": ["Value1", "Value2", "Value3"]
    }
    Aborts with 405 if the structure is unintended.
    Aborts with 501 if special characters are found

    This should be recursive, but the intended structure is simple, so...

    :param dict data: data dict received from the wild
    """
    try:
        for key, value in data.items():
            assert(re.match(INJECT_REGEX, key))
            if type(value) not in VALID_PY_TYPES:
                raise TypeError()
            if isinstance(value, str):
                assert(re.match(INJECT_REGEX, value))
            try:
                for listentry in value:
                    if type(value not in VALID_PY_TYPES):
                        raise TypeError()
                    assert(re.match(INJECT_REGEX, listentry))
            except TypeError:
                pass  # Not iterable, no need to care.
    except AssertionError:  # String contains special characters
        abort(501)
    except TypeError:  # Value is not an expected type...
        abort(405)

def _callApi(data):
    db = archibackend.api.Archibase()
    table = data.pop("table")
    result = db.select(table, data, RETURNFIELD_CONFIG[table])
    db.close()
    lineitems = []
    for value in result:
        lineitems.append(dict(zip(RETURNFIELD_CONFIG[table], value)))
    return lineitems
