import datetime
# import pandas as pd
import sqlite3 


con = sqlite3.connect("Test_db.db")

cur = con.cursor()

cur.execute("CREATE TABLE movie(title, year, score)")


cursor.execute("CREATE TABLE IF NOT EXISTS stammtische(datum DATE, anwesenheit TEXT, veranstalter TEXT, veranstalter2 TEXT)")



# dic = {}

# dic['t'] = 5

# df = pd.DataFrame(dic)

# print(df)
