import sqlite3
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px 
import os


Mitglieder = ['Leon', 'Zierer', 'Markus', 'Reiter',
 'Seppe', 'Christoph', 'Holzmann']

Orte = ['Leon', 'Zierer', 'Markus', 'Reiter',
 'Seppe', 'Christoph', 'Holzmann', 'Auswärts', 'Totalausfall']

Sidebarauswahl = ['Neuer Stammtisch', 'Kasse', 'Liste', 'Statistiken', 'Impressum']

datumsformat = 'DD.MM.YYYY'

# Verbindung zur SQLite-Datenbank herstellen
conn = sqlite3.connect("app_data.db")
cursor = conn.cursor()

# Tabelle "stammtische" erstellen
cursor.execute('''CREATE TABLE IF NOT EXISTS stammtische (
                    datum DATE, 
                    anwesenheit TEXT, 
                    veranstalter TEXT, 
                    veranstalter2 TEXT)''')

# Tabelle "kasse" erstellen
cursor.execute('''CREATE TABLE IF NOT EXISTS kasse (
                    mitglied TEXT PRIMARY KEY, 
                    offene_schulden INT, 
                    bezahlte_schulden INT)''')
# Initialisiere die Kasse
for mitglied in Mitglieder:
    cursor.execute("SELECT COUNT(*) FROM kasse WHERE mitglied= ?", (mitglied,))
    count = cursor.fetchone()[0]
    if count != 0:
        continue
    cursor.execute("INSERT INTO kasse (mitglied, offene_schulden, bezahlte_schulden) VALUES (?, ?, ?)",
    (mitglied, 0, 0))
    conn.commit()


def testmodus():
    with st.sidebar:
        löschen = st.button('Datenbank leeren')
        testdaten = st.button('Testdaten einfügen')
    if löschen == True:
        cursor.execute("DROP TABLE IF EXISTS stammtische")
        cursor.execute('''CREATE TABLE IF NOT EXISTS stammtische (
                    datum DATE, 
                    anwesenheit TEXT, 
                    veranstalter TEXT, 
                    veranstalter2 TEXT)''')
    if testdaten == True:
        cursor.execute('''CREATE TABLE IF NOT EXISTS stammtische (
                    datum DATE, 
                    anwesenheit TEXT, 
                    veranstalter TEXT, 
                    veranstalter2 TEXT)''')
        test_datum = ["2024-07-11", "2024-10-24", "2024-07-18", "2024-04-18"]
        test_anwesenheit = ["Leon, Zierer, Markus, Reiter, Seppe, Christoph, Holzmann", 
        "Leon, Zierer, Reiter, Seppe, Holzmann", 
        "Leon, Zierer, Reiter, Seppe, Holzmann, Christoph", 
        "Leon, Holzmann, Christoph"]
        test_veranstalter = ["Leon", "Leon", "Christoph", "Reiter"]
        test_veranstalter2 = ["Zierer", "Auswärts", "Markus", "Seppe"]
        for i in range(len(test_datum)):
            dt = test_datum[i]
            an = test_anwesenheit[i]
            ve = test_veranstalter[i]
            ve2 = test_veranstalter2[i]
            cursor.execute("INSERT INTO stammtische (datum, anwesenheit, veranstalter, veranstalter2) VALUES (DATE(?), ?, ?, ?)",
            (dt, an, ve, ve2))
            conn.commit()


def testmodus2():
    dat = datetime.date(2023, 3, 2)
    anw = 'Zierer, Markus, Leon, Reiter, Holzmann'
    veran = 'Reiter'
    veran2 = 'Leon'
    number = st.number_input('How many datasets', 0, 1000)
    for i in range(number):
        cursor.execute("INSERT INTO stammtische (datum, anwesenheit, veranstalter, veranstalter2) VALUES (DATE(?), ?, ?, ?)",
        (dat.isoformat(), anw, veran, veran2))
        dat = dat + datetime.timedelta(7)



def neuen_stammtisch_eintragen():
    anwesenheit = st.multiselect('Anwesenheit:', Mitglieder, placeholder= 'Bitte Teilnehmer auswählen')

    spalte1, spalte2, spalte3 = st.columns(3)
    with spalte1:
        veranstalter = st.radio('Veranstalter:', Orte)
    with spalte2:
        toggle = st.toggle('Zweiter Veranstaltungsort?')
    with spalte3:
        if toggle == True:
            veranstalter2 = st.radio('Veranstalter 2:', Orte)
            if veranstalter2 == veranstalter:
                st.error('Bitte anderen Veranstaltungsort auswählen')

    datum = st.date_input('Datum:', format= datumsformat)
    cursor.execute("SELECT COUNT(*) FROM stammtische WHERE datum = ?", (datum,))
    datum_in_db = cursor.fetchone()[0]

    if datetime.date.weekday(datum) != 3:
        st.error('Donnerstog is Stammtisch!!')
        don_check = False
    elif datum_in_db > 0:
        st.error('Zu diesem Datum gibt es schon einen Eintrag!')
        don_check = False
    else:
        don_check = True

    if st.button("Stammtisch eintragen?") and don_check == True:
        anwesenheit_str = ', '.join(anwesenheit)
        datum_str = datum.isoformat()
        cursor.execute("INSERT INTO stammtische (datum, anwesenheit, veranstalter, veranstalter2) Values (DATE(?), ?, ?, ?)", 
        (datum_str, anwesenheit_str, veranstalter, veranstalter2))
        conn.commit()
        st.success("Stammtisch gespeichert!")


def kasse():
    cursor.execute("SELECT * FROM kasse")
    moneten = cursor.fetchall()
    schulden = {}
    for kollege in moneten:
        schulden[kollege[0]] = kollege[1:]
    cursor.execute("SELECT * FROM stammtische")
    rows = cursor.fetchall()
    for row in rows:
        for mitglied in Mitglieder:
            if mitglied not in row[1]:
                schulden[mitglied] = schulden[mitglied][0] + 5, schulden[mitglied][1]
    df = pd.DataFrame(schulden, index= ['Offen', 'Bezahlt'])
    st.subheader('Offene Schulden')
    st.dataframe(df, use_container_width= True, hide_index= False)


def liste_anzeigen(veranstalter, modus):
    st.write(veranstalter)
    ver1_empty = len(veranstalter[0]) == 0
    ver2_empty = len(veranstalter[1]) == 0
    cursor.execute("SELECT * FROM stammtische")
    rows = cursor.fetchall()
    rows.sort()
    rows_filtered = []
    if modus == False:
        for row in rows:
            if (row[2] in veranstalter[0] or ver1_empty) and (row[3] in veranstalter[1] or ver2_empty):
                rows_filtered.append(row)
            else:
                continue
    else:
        for row in rows:
            if row[2] in veranstalter[0] or row[3] in veranstalter[1]:
                rows_filtered.append(row)
            elif ver1_empty and ver2_empty:
                rows_filtered.append(row)
            else:
                continue

    df = pd.DataFrame(rows_filtered, columns=['Datum ', 'Teilnehmer ', 'Veranstalter ', 'Zweiter Veranstalter'])
    st.dataframe(df, use_container_width = True, hide_index = True)



def veranstalter_filter():
    cursor.execute("SELECT veranstalter, veranstalter2 FROM stammtische")
    rows = cursor.fetchall()
    ver1 = []
    ver2 = []
    for row in rows:
        if row[0] not in ver1:
            ver1.append(row[0])
        if row[1] not in ver2:
            ver2.append(row[1])
        else:
            continue
    spalte1, spalte2 = st.columns(2)
    with spalte1:
        filter1 = st.selectbox('Filter Veranstalter', ver1, 
        index= None, placeholder= 'Bitte auswählen')
        if type(filter1) == type(None):
            filter1 = []
    with spalte2:
        filter2 = st.selectbox('Filter zweiter Veranstalter', 
        ver2, index= None, placeholder= 'Bitte auswählen')
        if type(filter2) == type(None):
            filter2 = []
    return filter1, filter2
    


def datums_filter():
    cursor.execute("SELECT datum FROM stammtische")
    vorhandene_datums = cursor.fetchall()
    vorhandene_datums.sort()
    try:
        st.date_input('Datumsfilter', min_value= vorhandene_datums[0][0], 
        max_value= vorhandene_datums[-1][0], format= datumsformat)
    except IndexError:
        st.error('Fehler mit dem Datensatz!')



def stammtische_zählen():
    cursor.execute("SELECT * FROM stammtische")
    rows = cursor.fetchall()
    stats = {}
    for mitglied in Mitglieder:
        if mitglied not in stats:
            stats[mitglied] = [0, 0]
    for row in rows:
        for mitglied in Mitglieder:
            if mitglied in row[1]:
                stats[mitglied][0] += 1
            if mitglied in row[2] or mitglied in row[3]:
                stats[mitglied][1] += 1
    return stats
    


def stats_tab1():
    dic = stammtische_zählen()
    labels = list(dic.keys())
    anwesenheiten = []
    veranstaltungen = []
    for kollege in dic:
        anwesenheiten.append(dic[kollege][0])
        veranstaltungen.append(dic[kollege][1])

    spalte1, spalte2 = st.columns(2)
    with spalte1:
        kuchen_anwesenheiten = px.pie(names= labels, values= anwesenheiten)
        kuchen_anwesenheiten.update_traces(textposition='inside', textinfo='label+percent+value')
        st.subheader('Anwesenheit')
        st.plotly_chart(kuchen_anwesenheiten)
    with spalte2:
        kuchen_veranstaltungen = px.pie(names= labels, values= veranstaltungen)
        kuchen_veranstaltungen.update_traces(textposition='inside', textinfo= 'label+percent+value')
        st.subheader('Veranstaltungen')
        st.plotly_chart(kuchen_veranstaltungen)


def stats_tab2():
    dic = stammtische_zählen()



def impressum():
    st.write(os.getenv)
    if os.getenv("STREAMLIT_SERVER_MODE") == 'true':
        st.write('True')
    else:
        st.write('False')
    # if __name__ == __main__:
    #     st.video('Rick Astley - Never Gonna Give You Up (Official Music Video).mp4',
    # autoplay= True, loop= True)
    # else:
    #     st.video('python_code/Rick Astley - Never Gonna Give You Up (Official Music Video).mp4',
    #     autoplay= True, loop= True)

    

def test():
    # tab1, tab2 = st.tabs(["Tab 1", "Tab2"])
    # tab1.write("this is tab 1")
    # tab2.write("this is tab 2")
    cursor.execute("SELECT * FROM stammtische")
    rows = cursor.fetchall()
    st.write(rows)




# Main

def main():
    with st.sidebar:
        st.header('Stammtisch Tracker:')
        auswahl = st.selectbox('Funktion: ', Sidebarauswahl)
        test_auswahl = st.toggle('Testmodus')
        if auswahl == Sidebarauswahl[2]:
            oder = st.toggle('Oder Filterung?')
        testmodus2()
    if  test_auswahl == True:
        testmodus()
    if auswahl == Sidebarauswahl[0]: # Neuer Stammtisch
        st.header(Sidebarauswahl[0], )
        neuen_stammtisch_eintragen()
    elif auswahl == Sidebarauswahl[1]: # Kasse 
        st.header(Sidebarauswahl[1])
        kasse()
    elif auswahl == Sidebarauswahl[2]: # Liste
        st.header(Sidebarauswahl[2])
        filterkriterium = veranstalter_filter()
        liste_anzeigen(filterkriterium, oder)
        # datums_filter()
    elif auswahl == Sidebarauswahl[3]: # Statistiken
        st.header(Sidebarauswahl[3])
        tab1, tab2 = st.tabs(['Kuchen', 'Pokal'])
        with tab1:
            stats_tab1()
        with tab2:
            stats_tab2()        
    elif auswahl == Sidebarauswahl[4]: # Impressum
        st.header(Sidebarauswahl[4])
        impressum()


    

main()




# Verbindung schließen, wenn die App stoppt
conn.close()
