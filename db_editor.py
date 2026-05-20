"""
Autor: Joel Walder, Johannes Kuen, Alexander Beck
Dieses Skript dient als Datenbank-Editor für die SQLite-Datenbank,
die von unserem Glücksspielprojekt verwendet wird.
"""

import sqlite3
import os

#Pfad zum aktuellen Skriptordner
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Datenbankdatei im selben Ordner
db_path = os.path.join(BASE_DIR, "db.sqlite3")


#Verbindung zur Datenbank herstellen
def connect():
    conn = sqlite3.connect(db_path)
    return conn


#Tabelle Spieler erstellen falls sie noch nicht existiert
def create_table():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Spieler (
        Username TEXT PRIMARY KEY,
        Password TEXT NOT NULL,
        Token INTEGER DEFAULT 1000,
        Profit INTEGER DEFAULT 0,
        Games_played INTEGER DEFAULT 0,
        Games_won INTEGER DEFAULT 0,
        Games_lost INTEGER DEFAULT 0
    );
    """)

    conn.commit()
    conn.close()


#Hilfsfunktion: Prüft ob ein Benutzername existiert
def player_exists(username):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 1 FROM Spieler
    WHERE Username = ?
    """, (username,))

    result = cursor.fetchone()
    conn.close()

    return result is not None


#Neuen Spieler erstellen
def create_player(username, password):
    username = username.strip()
    password = password.strip()

    if username == "" or password == "":
        return False

    conn = connect()
    cursor = conn.cursor()

    try:
        #Spieler in Datenbank einfügen
        cursor.execute("""
        INSERT INTO Spieler (Username, Password)
        VALUES (?, ?)
        """, (username, password))

        conn.commit()
        return True

    #Fehler falls Username bereits existiert
    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


#Login eines Spielers überprüfen
def login(username, password):
    username = username.strip()
    password = password.strip()

    if username == "" or password == "":
        return None

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT Username, Password, Token, Profit, Games_played, Games_won, Games_lost
    FROM Spieler
    WHERE Username = ? AND Password = ?
    """, (username, password))

    user = cursor.fetchone()
    conn.close()

    return user


#Spieler löschen
def delete_player(username, password):
    username = username.strip()
    password = password.strip()

    if username == "" or password == "":
        return False

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM Spieler
    WHERE Username = ? AND Password = ?
    """, (username, password))

    conn.commit()

    deleted = cursor.rowcount > 0
    conn.close()

    return deleted


#Aktuelle Tokens eines Spielers abrufen
def get_tokens(username):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT Token FROM Spieler
    WHERE Username = ?
    """, (username,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]

    return None


#Profit eines Spielers abrufen
def get_profit(username):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT Profit FROM Spieler
    WHERE Username = ?
    """, (username,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]

    return None


#Statistiken eines Spielers abrufen
def get_stats(username):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT Username, Token, Profit, Games_played, Games_won, Games_lost
    FROM Spieler
    WHERE Username = ?
    """, (username,))

    result = cursor.fetchone()
    conn.close()

    return result


#Tokens eines Spielers auf einen festen Wert setzen
def update_tokens(username, amount):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE Spieler
    SET Token = ?
    WHERE Username = ?
    """, (amount, username))

    conn.commit()
    conn.close()


#Tokens eines Spielers um einen Wert verändern
def change_tokens(username, delta):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE Spieler
    SET Token = Token + ?
    WHERE Username = ?
    """, (delta, username))

    conn.commit()
    conn.close()


#Anzahl gewonnener Spiele erhöhen
def add_win(username):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE Spieler
    SET Games_won = Games_won + 1,
        Games_played = Games_played + 1
    WHERE Username = ?
    """, (username,))

    conn.commit()
    conn.close()


#Anzahl verlorener Spiele erhöhen
def add_loss(username):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE Spieler
    SET Games_lost = Games_lost + 1,
        Games_played = Games_played + 1
    WHERE Username = ?
    """, (username,))

    conn.commit()
    conn.close()


#Einfach nur ein gespieltes Spiel zählen
def add_game(username):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE Spieler
    SET Games_played = Games_played + 1
    WHERE Username = ?
    """, (username,))

    conn.commit()
    conn.close()


#Profit eines Spielers aktualisieren
def update_profit(username, amount):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE Spieler
    SET Profit = Profit + ?
    WHERE Username = ?
    """, (amount, username))

    conn.commit()
    conn.close()


#Tabelle beim Import erstellen
create_table()