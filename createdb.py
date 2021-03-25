import sqlite3
con = sqlite3.connect('./db/searches.db')
cur = con.cursor()

cur.execute("CREATE TABLE searches (id text, query text, matches text, date text)")

con.commit()
con.close()
