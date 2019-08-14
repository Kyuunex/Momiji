import sqlite3
from modules.connections import database_file as database_file


def mass_query(queries):
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    c.execute('BEGIN TRANSACTION')
    for query in queries:
        try:
            c.execute(query[0], query[1])
        except:
            pass
    conn.commit()
    conn.close()
    return []


def query(query):
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    if type(query) is str:
        result = tuple(c.execute(query))
    elif type(query) is list:
        result = tuple(c.execute(query[0], query[1]))
    elif type(query) is tuple:
        result = tuple(c.execute(query[0], query[1]))
    conn.commit()
    conn.close()
    return result
