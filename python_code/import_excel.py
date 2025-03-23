
import sqlite3


con = sqlite3.connect('realle_daten.db')
cur = con.cursor()

# cur.execute("DROP TABLE IF EXISTS altestammtische")

cur.execute("""CREATE TABLE IF NOT EXISTS altestammtische(
                datum DATE PRIMARY KEY,
                anwesenheit TEXT,
                veranstalter TEXT,
                veranstalter2 TEXT)""")





def read_file(filename: str) -> dict:
    dic = {}
    headers = []
    with open(filename, encoding= "utf-8") as file:
        for row in file:
            parts = row.split(';')
            if len(headers) == 0:
                for key in parts:
                    if key == '' or key == '\n':
                        continue
                    dic[key.strip()] = []
                    headers.append(key.strip())
            else:
                for i in range(len(dic)):
                    dic[headers[i]].append(parts[i])
    return dic


def stats(raw_data: dict) -> dict:
    dic = {}
    for person in raw_data:
        if person == 'Datum':
            raw_data[person] = 0
            continue
        result = 0
        for tag in raw_data[person]:
            if tag == 'Anwesend':
                result += 1
        dic[person] = result
    return dic


def datenbank_schreiben(raw_data: dict):
    dic = {}
    keys = list(raw_data.keys())
    for datum in raw_data['Datum']:
        dic[datum] = []
        index = raw_data['Datum'].index(datum)
        for key in keys:
            if key == 'Datum':
                continue
            dic[datum].append(raw_data[key][index])
    
    for datum in dic:
        anwesenheit = ''
        index = 1
        for status in dic[datum][:7]:
            if status == 'Anwesend':
                anwesenheit += keys[index]
                anwesenheit += ';'
            index += 1
            if index > 7:
                index = 1
        veranstalter = dic[datum][7]
        veranstalter2 = dic[datum][8]
        cur.execute("""INSERT INTO altestammtische(datum, anwesenheit, veranstalter, veranstalter2)
                    VALUES (?, ?, ?, ?)""", (datum, anwesenheit, veranstalter, veranstalter2))
    con.commit()
    return dic

def read_db():
    cur.execute("SELECT * FROM altestammtische")
    rows = cur.fetchall()
    for row in rows:
        # if row[2] == 'Auswärts':
        #     print('Heurecka')
        # else:
        #     print(row[2])
        print(row)
        print()

            

def main():
    # jahr2024 = read_file('Anwesenheit_2024.csv')
    # jahr2025 = read_file('Anwesenheit_2025.csv')
    # datenbank_schreiben(jahr2024)
    # datenbank_schreiben(jahr2025)

    read_db()
    # print(test['06.06.2024'])

main()

con.close()

# dic = {1: ['a', 'b', 'c'], 2: ['c', 'd', 'e']}

# for letter in dic[1]:
#     index = dic[1].index(letter)
#     print(dic[2][index])
