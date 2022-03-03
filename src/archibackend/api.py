import os
from pprint import pprint as pp
import toml
import json
import psycopg2 as PSQL

SECRETS = toml.load(os.path.join(os.path.dirname(__file__), "config", "secrets.toml"))["general"]
CONFIG = toml.load(os.path.join(os.path.dirname(__file__), "config", "config.toml"))["general"]

with open(os.path.join(os.path.dirname(__file__), "config", "dbmap.json")) as infile:
    ARCHIVE_CONFIG = json.load(infile)

class Database:
    """
    Base class for managing the DB connection. Shouldn't be called directly by user applications, but be
    wrapped by a back-end tailored to the use case.
    """
    def __init__(self):
        self.conn = PSQL.connect(
            database=CONFIG["database"],
            user=SECRETS["user"]
        )
    
    def getVersion(self):
        COMMAND = 'SELECT version()'
        return self._run_command(COMMAND)
    
    
    def close(self):
        self.conn.close()
        print("Exited cleanly")
    

    def _run_command(self, command, params=None):
        try:
            cur = self.conn.cursor()
            #print(cur.mogrify(command, params))
            cur.execute(command, params)
            value = cur.fetchall()
            cur.close()
        except Exception as e:
            print(e)

        return value


class Archibase(Database):
    def select(self, table, fields, returnfields="*"):
        """
        Prep the SELECT command on a given table for a certain set of provided filters.
        """
        realtable = self._get_real_table(table)
        # if no table, we have a problem
        if not realtable:
            raise TableNotFoundException(f"No table {table} found...")
        realfields, fieldtypes, skipped = self._map_field_requests(realtable, fields)
        realcommand = self._build_select_command(
            realtable,
            realfields,
            fieldtypes,
            ','.join(returnfields) if returnfields else '*'
        )
        return self._run_command(realcommand, realfields)



    def _get_real_table(self, table):
        return ARCHIVE_CONFIG["tables"].get(table, None)

    def _map_field_requests(self, table, fields):
        newdict = {}
        fieldtypes = {}
        skipped = []
        for key, value in fields.items():
            newkey = ARCHIVE_CONFIG[table].get(key, {}).get("field", None)
            if not newkey:
                skipped.append(key)
                continue
            newdict[newkey] = value
            fieldtypes[newkey] = ARCHIVE_CONFIG[table][key]["type"]
        return newdict, fieldtypes, skipped
    
    def _build_select_command(self, table, fields, searchtypes, returnfields):
        base = f"SELECT {returnfields} FROM {table}"
        if fields:
            base += " WHERE "
            extras = []
            for key, value in fields.items():
                extras.append(ARCHIVE_CONFIG["querysyntax"][searchtypes[key]].format(key=key))
            base += " AND ".join(extras)
        base += ";"

        # Handle "contains" logic. Due to python string formatting
        # shenanigans, we need to add the PSQL "%" regex characters to the vars
        # and not the query directly...
        for key in fields.keys():
            if searchtypes[key] == "contains":
                fields[key] = "%"+fields[key]+"%"
        return base




class TableNotFoundException(Exception):
    """
    The requested DB table does not match anything on record.
    """

if __name__ == "__main__":
    db = Archibase()
    result = db.select("games", {"genres": ["Pixel"]})
    db.close()
    pp(result)
