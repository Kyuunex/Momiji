import asyncio
import sqlite3

dbfile = 'db.db'

async def query(query):
	try:
		conn = sqlite3.connect(dbfile)
		c = conn.cursor()
		result = list(c.execute(query))
		conn.commit()
		conn.close()
		return result
	except Exception as result:
		return result

async def update(tn, setkey, setvalue, wherekey, wherevalue):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	result = list(c.execute("UPDATE "+tn+" SET "+setkey+" = ? WHERE "+wherekey+" = ?;", (setvalue, wherevalue)))
	conn.commit()
	conn.close()
	return result

async def select(tn, selectkey, wheres):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	if wheres != None:
		wherestring = "WHERE "
		wherevalues = []
		for onewhere in wheres:
			wherestring += str(onewhere[0])
			wherestring += " = "
			wherestring += "?"
			wherevalues.append(onewhere[1])
			if onewhere != wheres[-1]:
				wherestring += " AND "
		result = list(c.execute("SELECT "+selectkey+" FROM "+tn+" "+wherestring+";", tuple(wherevalues)))
	else:
		result = list(c.execute("SELECT "+selectkey+" FROM "+tn+";"))
	conn.commit()
	conn.close()
	return result

async def delete(tn, wheres):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	if wheres != None:
		wherestring = "WHERE "
		wherevalues = []
		for onewhere in wheres:
			wherestring += str(onewhere[0])
			wherestring += " = "
			wherestring += "?"
			wherevalues.append(onewhere[1])
			if onewhere != wheres[-1]:
				wherestring += " AND "
		result = list(c.execute("DELETE FROM "+tn+" "+wherestring+";", tuple(wherevalues)))
	else:
		result = list(c.execute("DELETE FROM "+tn+";"))
	conn.commit()
	conn.close()
	return result

async def insert(tn, values):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	formatstring = ("?," * len(values)).rstrip(",")
	print("INSERT INTO "+tn+" VALUES ("+formatstring+")", values)
	result = list(c.execute("INSERT INTO "+tn+" VALUES ("+formatstring+")", values))
	conn.commit()
	conn.close()
	return result
