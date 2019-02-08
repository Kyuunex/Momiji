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


async def update(tn, setkey, setvalue, wherekey, wherevalue):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    result = list(c.execute("UPDATE %s SET %s = ? WHERE %s = ?;" %
                            (tn, setkey, wherekey), (setvalue, wherevalue)))
    conn.commit()
    conn.close()
    return result


async def select(tn, selectkey, wheres):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    if wheres:
        wherestring = "WHERE "
        wherevalues = []
        for onewhere in wheres:
            wherestring += str(onewhere[0])
            wherestring += " = "
            wherestring += "?"
            wherevalues.append(onewhere[1])
            if onewhere != wheres[-1]:
                wherestring += " AND "
        result = list(c.execute("SELECT %s FROM %s %s;" %
                                (selectkey, tn, wherestring), tuple(wherevalues)))
    else:
        result = list(c.execute("SELECT %s FROM %s;" % (selectkey, tn)))
    conn.commit()
    conn.close()
    return result


async def delete(tn, wheres):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    if wheres:
        wherestring = "WHERE "
        wherevalues = []
        for onewhere in wheres:
            wherestring += str(onewhere[0])
            wherestring += " = "
            wherestring += "?"
            wherevalues.append(onewhere[1])
            if onewhere != wheres[-1]:
                wherestring += " AND "
        result = list(c.execute("DELETE FROM %s %s;" %
                                (tn, wherestring), tuple(wherevalues)))
    else:
        result = list(c.execute("DELETE FROM %s;" % (tn)))
    conn.commit()
    conn.close()
    return result


async def insert(tn, values):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    formatstring = ("?," * len(values)).rstrip(",")
    result = list(c.execute("INSERT INTO %s VALUES (%s)" %
                            (tn, formatstring), values))
    conn.commit()
    conn.close()
    return result
