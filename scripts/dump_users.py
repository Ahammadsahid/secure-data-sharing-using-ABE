import sqlite3, os
p = r'c:\7th sem\CAPSTON PROJECT\code\secure-data-sharing\users.db'
print('DB exists:', os.path.exists(p))
con = sqlite3.connect(p)
cur = con.cursor()
try:
    cur.execute('SELECT id,username,password,role,department,clearance FROM users')
    rows = cur.fetchall()
    for r in rows:
        print(r)
except Exception as e:
    print('ERR', e)
finally:
    con.close()
