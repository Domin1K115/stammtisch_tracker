# importieren aller Abhängigkeiten
import sqlite3
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px 

# globale Variablen definieren
Mitglieder = ['Leon', 'Zierer', 'Markus', 'Reiter',
 'Seppe', 'Christoph', 'Hoize']

Orte = ['Leon', 'Zierer', 'Markus', 'Reiter',
 'Seppe', 'Christoph', 'Hoize', 'Auswärts', 'Totalausfall']

Sidebarauswahl = ['Neuer Stammtisch', 'Kasse', 'Liste', 'Statistiken', 'Impressum']

datumsformat = 'DD.MM.YYYY'

datum_schon_vorhanden_error = 'Zu diesem Datum sind schon Daten vorhanden'

if st.session_state.löschen != type(bool):
    st.session_state.löschen = False

# format d bedeutet int für float in f wechseln optional .n für nachkommmastellen davor
kassenformat = st.column_config.NumberColumn(format= "%d €")

# Verbindung zu den SQLite-Datenbanken herstellen
conn = sqlite3.connect("app_data.db")
cursor = conn.cursor()

conn2 = sqlite3.connect("realle_daten.db")
cursor2 = conn2.cursor()

def tabellen_in_db_erstellen(): # Tabelle "stammtische" erstellen
    cursor.execute("""CREATE TABLE IF NOT EXISTS stammtische(
                        datum DATE PRIMARY KEY, 
                        anwesenheit TEXT, 
                        veranstalter TEXT, 
                        veranstalter2 TEXT)""")     

    # Tabelle "kasse" erstellen
    cursor.execute("""CREATE TABLE IF NOT EXISTS kasse(
                    mitglied TEXT PRIMARY KEY, 
                    offene_schulden INT, 
                    bezahlte_schulden INT)""")
    
    # Tabelle "altestammtische" erstellen

    cursor2.execute("DROP TABLE IF EXISTS altestammtische")

    cursor2.execute("""CREATE TABLE IF NOT EXISTS altestammtische(
                    datum DATE PRIMARY KEY,
                    anwesenheit TEXT,
                    veranstalter TEXT,
                    veranstalter2 TEXT)""")

tabellen_in_db_erstellen() # funktion wird direkt gecallt

def init_kasse():# Kasse initialisieren
    for mitglied in Mitglieder: # Hier wird geprüft, ob die namen aus Mitglieder schon in der db gelistet sind
        cursor.execute("SELECT COUNT(*) FROM kasse WHERE mitglied= ?", (mitglied,))
        count = cursor.fetchone()[0]
        if count != 0:
            continue
    # wenn nicht wird hier für jedes Mitlied die offenen und bezahlten Schulden auf 0 gesetzt
        cursor.execute("""INSERT INTO kasse 
                        (mitglied, offene_schulden, bezahlte_schulden) 
                        VALUES (?, ?, ?)""",
                        (mitglied, 0, 0))
        conn.commit()

init_kasse() # funktion wird direkt gecallt, damit die db bei jedem refresh initialisiert it



def testmodus(): # temporärer Testmodus
    with st.sidebar: # legt die zwei Knöpfe Datenbank leeren und Testdaten einfügen an
        löschen = st.button('Datenbanken leeren')
        testdaten = st.button('Testdaten einfügen')
    if löschen == True: # wenn der knopf gedrückt wird werden beide Db's geleert und neu erstellt
        cursor.execute("DROP TABLE IF EXISTS stammtische")
        cursor.execute("DROP TABLE IF EXISTS kasse")
        tabellen_in_db_erstellen()
        init_kasse()
    if testdaten == True: # hier werden einige Testdaten in die Datenbank gespeichert
        tabellen_in_db_erstellen()

        test_datum = ["11.07.2024", "24.10.2024", "18.07.2024", "18.04.2024"] # Hardcoded inputs
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
            try: # try except block um doppelte werte in der db abzufangen
                cursor.execute("""INSERT INTO stammtische 
                                (datum, anwesenheit, veranstalter, veranstalter2) 
                                VALUES (?, ?, ?, ?)""",
                                (dt, an, ve, ve2))
            except sqlite3.IntegrityError:
                st.error(f'{datum_schon_vorhanden_error}: {dt}')
                break
            conn.commit()
    


def testmodus2(): # temporärer testmodus
    dat = datetime.date(2023, 3, 2)
    anw = 'Zierer, Markus, Leon, Reiter, Holzmann'
    veran = 'Reiter'
    veran2 = 'Leon'
    number = st.number_input('How many datasets', 0, 1000) # zahlenfeldeingabe
    # fügt die Anzahl an ausgewählten werten ein und erhöht jedes mal den Tag um 7 
    # um doppelte werte zu vermeiden, deshalb kein try except block
    for i in range(number): 
        cursor.execute("INSERT INTO stammtische (datum, anwesenheit, veranstalter, veranstalter2) VALUES (DATE(?), ?, ?, ?)",
        (dat.isoformat(), anw, veran, veran2))
        dat = dat + datetime.timedelta(7)




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
                anwesenheit += ', '
            index += 1
            if index > 7:
                index = 1
        veranstalter = dic[datum][7]
        veranstalter2 = dic[datum][8]
        cursor2.execute("""INSERT INTO altestammtische(datum, anwesenheit, veranstalter, veranstalter2)
                    VALUES (?, ?, ?, ?)""", (datum, anwesenheit, veranstalter, veranstalter2))
    conn2.commit()
    return dic




def real_daten_importieren():
    jahr2024 = read_file('anwesenheit_2024.csv')
    jahr2025 = read_file('anwesenheit_2025.csv')
    datenbank_schreiben(jahr2024)
    datenbank_schreiben(jahr2025)



def reale_daten_lesen(): # fügt die aktuellsten Daten in die db ein, Stand 23.03.2025
    real_daten_importieren()
    cursor2.execute("SELECT * FROM altestammtische") # cursor2 ist immer die db realle_daten
    rows = cursor2.fetchall()
    for row in rows:
        datum = row[0]
        anwesenheit = row[1]
        if row[2] == 'Ausw�rts': # workaround weil beim excel export ä nicht ordentlich angezeigt wurde
            veranstalter = 'Auswärts'
        else:
            veranstalter = row[2]
        if row[3] == '':
            veranstalter2 = '-'
        elif row[3] == 'Ausw�rts':
            veranstalter2 = 'Auswärts'
        else:
            veranstalter2 = row[3]
        try: # try except block, um doppelte werte in der db abzufangen
            cursor.execute("""INSERT INTO stammtische (datum, 
                                anwesenheit, 
                                veranstalter, 
                                veranstalter2) Values 
                                (?, ?, ?, ?)""", 
                                (datum, anwesenheit, 
                                veranstalter, veranstalter2))
        except sqlite3.IntegrityError:
            st.error(f'{datum_schon_vorhanden_error}: {datum}')
            break
        conn.commit()



def neuen_stammtisch_eintragen(): # fügt einen neuen Eintrag zur db hinzu
    anwesenheit = st.multiselect('Anwesenheit:', Mitglieder, placeholder= 'Bitte Teilnehmer auswählen')

    spalte1, spalte2, spalte3 = st.columns(3)
    with spalte1:
        veranstalter = st.radio('Veranstalter:', Orte)
    with spalte2: # optionaler zweiter Veranstalter
        toggle = st.toggle('Zweiter Veranstaltungsort?')
    with spalte3:
        if toggle == True:
            veranstalter2 = st.radio('Veranstalter 2:', Orte)
            if veranstalter2 == veranstalter: # sicherstellen, dass derselbe nicht doppelt gewählt wird
                st.error('Bitte anderen Veranstaltungsort auswählen')
        else:
            veranstalter2 = '-'
# Hier wird das gewünschte Datum abgefragt, hier wird noch in der Datenbank geprüft, ob das 
# Datum schonmal vorhanden ist, das wird in Zukunft wsl auch über einen try except
# Block gelöst
    datum = st.date_input('Datum:', format= datumsformat)
    cursor.execute("SELECT COUNT(*) FROM stammtische WHERE datum = ?", (datum,))
    datum_in_db = cursor.fetchone()[0]

    if datetime.date.weekday(datum) != 3: # hier wird geprüft, ob der gewählte Tag ein Donnerstag ist
        st.error('Donnerstog is Stammtisch!!')
        don_check = False
    elif datum_in_db > 0:
        st.error(datum_schon_vorhanden_error)
        don_check = False
    else:
        don_check = True

# Hier werden die gewählten Daten in die Datenbank gespeichert
    if st.button("Stammtisch eintragen?") and don_check == True:
        anwesenheit_str = ', '.join(anwesenheit)
        datum_str = datum.isoformat()
        cursor.execute("""INSERT INTO stammtische 
                        (datum, anwesenheit, veranstalter, veranstalter2) 
                        Values (DATE(?), ?, ?, ?)""", 
                        (datum_str, anwesenheit_str, veranstalter, veranstalter2))
        conn.commit()
        st.success("Stammtisch gespeichert!")


def kasse(): # Zeigt den aktuellen Kassenstand an (aktuell nur Schulden)
    cursor.execute("SELECT * FROM kasse")
    moneten = cursor.fetchall()
    schulden = {} # dict im Format mitglied: [offene Schulden, geschlossene Schulden]
    formatierung = {} # dict im Format mitglied : Kassenformat
# Hier werden die aktuellen Werte aus der db gelesen (aktuell immer leer, weil nichts
# in Kasse gespeichert wird
    for kollege in moneten:
        schulden[kollege[0]] = kollege[1:]
# Hier wird ausgewertet an welchem tag welche person anwesend war oder nicht
    cursor.execute("SELECT * FROM stammtische")
    rows = cursor.fetchall()
    for row in rows:
        for mitglied in Mitglieder:
            if mitglied not in row[1]:
                schulden[mitglied] = schulden[mitglied][0] + 5, schulden[mitglied][1]
            formatierung[mitglied] = kassenformat

    df = pd.DataFrame(schulden, index= ['Offen', 'Bezahlt'], dtype= float)

    st.subheader('Offene Schulden')
    st.dataframe(df, column_config= formatierung, 
                use_container_width= True, hide_index= False)


# Das ist das Overlay, das die Meldung zum löschen anzeigt
@st.dialog('Wirklich löschen?')
def eintrag_löschen(menge: int) -> bool:
    if menge == 1:
        st.write(f'{menge} Eintrag löschen?')
    else:
        st.write(f'{menge} Einträge löschen?')
    if st.button('Ja') == True:
        st.session_state.löschen = True
        st.rerun()


# zeigt eine Tabelle mit allen stammtischen in der db an, nimmt als input die selectionen aus 
# veranstalter_filter() und den Filtermodus aus dem oder toggle aus main()
def liste_anzeigen(veranstalter: tuple[list, list], filtermodus: bool): 
    st.write(veranstalter)
    löschen = st.button('Ausgewählte Daten löschen?')
    ver1_empty = len(veranstalter[0]) == 0
    ver2_empty = len(veranstalter[1]) == 0
    cursor.execute("SELECT * FROM stammtische")
    rows = cursor.fetchall()
# soll nach datum sortieren, funktioniert noch nicht, weil die aktuell als str gespeichert sind
    rows.sort() 
    rows_filtered = []
# wenn der filtermodus aus ist, heißt das Und filter modus, also was in veranstalter und
# veranstalter 2 ausgewählt ist
    if filtermodus == False: 
        for row in rows:
            if (row[2] in veranstalter[0] or ver1_empty) and (row[3] in veranstalter[1] or ver2_empty):
                rows_filtered.append(row)
            else:
                continue
# wenn der toggle an ist, wird im modus oder gefiltert
    else:
        for row in rows:
            if row[2] in veranstalter[0] or row[3] in veranstalter[1]:
                rows_filtered.append(row)
            elif ver1_empty and ver2_empty:
                rows_filtered.append(row)
            else:
                continue


# wenn alles gefiltert wurde, wird alles in einem dataframe objekt angezeigt
    df = pd.DataFrame(rows_filtered, columns=['Datum ', 'Teilnehmer ', 
                        'Veranstalter ', 'Zweiter Veranstalter'])
    output = st.dataframe(df, use_container_width = True, hide_index = True, on_select= "rerun",
    selection_mode= 'multi-row')


    if löschen == True:
        eintrag_löschen(len(output['selection']['rows']))
    if st.session_state.löschen == True:
        for row in output['selection']['rows']:
            datum = df.iat[row,0]
            cursor.execute("""DELETE FROM stammtische WHERE datum = ?""", (datum,))
            conn.commit()
        st.session_state.löschen = False
        st.rerun()


    



def veranstalter_filter() -> tuple[list, list]: # Hier werden die Veranstaltungen gefiltert
    cursor.execute("SELECT veranstalter, veranstalter2 FROM stammtische")
    rows = cursor.fetchall()
    ver1 = []
    ver2 = []
# Hier werden erstmal alle veranstaltungsorte aus der Datenbank gelesen, sodass nur die zum
# filtern angezeigt werden, die auch möglich sind
    for row in rows:
        if row[0] not in ver1:
            ver1.append(row[0])
        if row[1] not in ver2:
            ver2.append(row[1])
        else:
            continue
    spalte1, spalte2 = st.columns(2)
    with spalte1: # Hier wird die erste Selection abgefragt
        filter1 = st.selectbox('Filter Veranstalter', ver1, 
        index= None, placeholder= 'Bitte auswählen')
        if type(filter1) == type(None):
            filter1 = []
    with spalte2: # Hier die zweite
        filter2 = st.selectbox('Filter zweiter Veranstalter', 
        ver2, index= None, placeholder= 'Bitte auswählen')
        if type(filter2) == type(None):
            filter2 = []
    return filter1, filter2 # returned ein tuple beider listen
    


def datums_filter(): # aktuell nicht in gebrauch
    cursor.execute("SELECT datum FROM stammtische")
    vorhandene_datums = cursor.fetchall()
    vorhandene_datums.sort()
    try:
        st.date_input('Datumsfilter', min_value= vorhandene_datums[0][0], 
        max_value= vorhandene_datums[-1][0], format= datumsformat)
    except IndexError:
        st.error('Fehler mit dem Datensatz!')


# Hier wird gezählt wie viele stammtische jedes Mitglied anwesend war und wie oft an welchem
# Ort er stattgefunden hat
def stammtische_zählen() -> dict[str:list]: 
    cursor.execute("SELECT * FROM stammtische")
    rows = cursor.fetchall()
    stats = {}
    for ort in Orte: # Hier werden alle Orte als Keys initialisiert
        if ort not in stats:
            if ort in Mitglieder:
                stats[ort] = [0, 0]
            else:
                stats[ort] = [0]
    for row in rows: # Dann wird für jede Zeile in der db der Wert gelesen
        for mitglied in Mitglieder:
            if mitglied in row[1]:
                stats[mitglied][1] += 1
        for ort in Orte:
            if ort in row[2] or ort in row[3]:
                stats[ort][0] += 1
    return stats
    

# Hier wird der erste Tab der Statistik Seite angezeigt
def stats_tab1(): 
    dic = stammtische_zählen() # erst werden die stammtische gezählt 
    labels1 = list(dic.keys()) # die labels werden definiert um sie später im dataframe zu nutzen
    labels2 = labels1[0:7]
    anwesenheiten = []
    veranstaltungen = []
# Hier werden die Zahlen wie oft jeder anwesend war und wie oft an jedem Ort war 
# in seperate Listen übergeben
    for location in dic: 
        veranstaltungen.append(dic[location][0])
        try:
            anwesenheiten.append(dic[location][1])
# der indexerror, der auftritt wenn versucht wird bei den zwei Orten Auswärts und Totalausfall 
# einen Wert der Anwesenheit abzufragenn, wird übersprungen
        except IndexError: 
            continue
# Anschließend werden die beiden Listen als Kuchendiagramm dargestellt
    spalte1, spalte2 = st.columns(2)
    with spalte1:
        kuchen_anwesenheiten = px.pie(names= labels2, values= anwesenheiten)
        kuchen_anwesenheiten.update_traces(textposition='inside', textinfo='label+percent+value')
        st.subheader('Anwesenheit')
        st.plotly_chart(kuchen_anwesenheiten)
    with spalte2:
        kuchen_veranstaltungen = px.pie(names= labels1, values= veranstaltungen)
        kuchen_veranstaltungen.update_traces(textposition='inside', textinfo= 'label+percent+value')
        st.subheader('Veranstaltungen')
        st.plotly_chart(kuchen_veranstaltungen)


def stats_tab2(): # noch nicht definiert
    dic = stammtische_zählen()



def impressum(): # Never gonna give you up!!
    try: # try except block um zwischen local und Server zu unterscheiden
        st.video('python_code/Rick Astley - Never Gonna Give You Up (Official Music Video).mp4',
        autoplay= True, loop= True)
    except st.streamlit.runtime.media_file_storage.MediaFileStorageError:
        st.video('Rick Astley - Never Gonna Give You Up (Official Music Video).mp4',
        autoplay= True, loop= True)
    

    

def test(): # wird aktuell nicht benutzt
    cursor.execute("SELECT * FROM stammtische")
    rows = cursor.fetchall()
    st.write(rows)
     


# Hier die Main function, sie gibt alles an was in der Sidebar angezeigt wird und führt die 
# jeweiligen Funktionen aus, wenn sie benötigt werden

def main():
    with st.sidebar:
        st.header('Stammtisch Tracker:') # Header
        auswahl = st.selectbox('Funktion: ', Sidebarauswahl) # Auswahlfeld welche Function genutzt wird



# Hier die Abfrage des oder toggles, die für die Filterung der Liste genutzt wird 
        if auswahl == Sidebarauswahl[2]: 
            oder = st.toggle('Oder Filterung?')
        

        test_auswahl = st.toggle('Testmodus') # Temporärer Testmodus
        if  test_auswahl == True:
            testmodus()
            testmodus2()

# Hier der Knopf um die tatsächlich aktuellen Daten einzugüfen, aktuell noch hier zum testen
# auf Dauer wird das automatisiert laufen
        if st.button('Reale Daten einfügen') == True: 
            reale_daten_lesen()

        st.html("https://stammtischtracker.streamlit.app") # Url der WebApp
    
    if auswahl == Sidebarauswahl[0]: # Neuer Stammtisch function wird gecallt
        st.header(Sidebarauswahl[0], )
        neuen_stammtisch_eintragen()
    elif auswahl == Sidebarauswahl[1]: # Kasse function wird gecallt
        st.header(Sidebarauswahl[1])
        kasse()
    elif auswahl == Sidebarauswahl[2]: # Listen function wird gecallt
        st.header(Sidebarauswahl[2])
        filterkriterium = veranstalter_filter()
        liste_anzeigen(filterkriterium, oder)
        # datums_filter()
    elif auswahl == Sidebarauswahl[3]: # Statistiken function wird gecallt
        st.header(Sidebarauswahl[3])
        tab1, tab2 = st.tabs(['Kuchen', 'Pokal']) # zwei tabs zur anzeige verschiedener stats
        with tab1:
            stats_tab1()
        with tab2:
            stats_tab2()        
    elif auswahl == Sidebarauswahl[4]: # Impressum function wird gecallt
        st.header(Sidebarauswahl[4])
        impressum()


    

main()




# Verbindung schließen, wenn die App stoppt
conn.close()
