import asyncio
import sqlite3

dbfile = 'data/maindb.sqlite3'


async def massquery(query):
    if query:
        conn = sqlite3.connect(dbfile)
        c = conn.cursor()
        c.execute('BEGIN TRANSACTION')
        for s in query:
            try:
                c.execute(s[0], s[1])
            except:
                pass
        conn.commit()
        conn.close()
        return []


async def query(query):
    try:
        conn = sqlite3.connect(dbfile)
        c = conn.cursor()
        if type(query) is str:
            result = list(c.execute(query))
        elif type(query) is list:
            result = list(c.execute(query[0], query[1]))
        elif type(query) is tuple:
            result = list(c.execute(query[0], query[1]))
        conn.commit()
        conn.close()
        return result
    except Exception as result:
        return result
