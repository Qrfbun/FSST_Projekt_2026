"""
devs: Joel Walder, Johannes Kuen, Alexander Beck

Einfaches Blackjack-Spiel mit:
- Tkinter GUI
- SQLite Datenbank
- Login / Registrierung
- Blackjack Logik
"""

import tkinter as tk
from tkinter import messagebox

import blackjack as bj
import db_editor


#========================
# HAUPTFENSTER
#========================

root = tk.Tk()

root.title("Blackjack")
root.geometry("1000x850")
root.configure(bg="#0B3D2E")

#Fenstergröße fixieren
root.resizable(False, False)


#========================
# GLOBALE VARIABLEN
#========================

current_user = None

deck = []

player_hand = []
dealer_hand = []

bet = 0

game_running = False


#========================
# HILFSFUNKTIONEN
#========================

#Spielerinformationen aktualisieren
def update_info():

    tokens = db_editor.get_tokens(current_user)

    info_label.config(
        text=f"Benutzer: {current_user} | Tokens: {tokens}"
    )


#Karten anzeigen
def update_cards(hidden_dealer=True):

    #Dealer Karten anzeigen
    dealer_cards_label.config(
        text=bj.hand_to_ascii(
            dealer_hand,
            hide_second=hidden_dealer
        )
    )

    #Dealer Punkte anzeigen
    if hidden_dealer:

        dealer_points_label.config(
            text="Punkte: ?"
        )

    else:

        dealer_points_label.config(
            text=f"Punkte: {bj.hand_value(dealer_hand)}"
        )

    #Player Karten anzeigen
    player_cards_label.config(
        text=bj.hand_to_ascii(player_hand)
    )

    #Player Punkte anzeigen
    player_points_label.config(
        text=f"Punkte: {bj.hand_value(player_hand)}"
    )


#Buttons aktivieren/deaktivieren
def set_game_buttons(state):

    hit_button.config(state=state)
    stand_button.config(state=state)


#Spielscreen öffnen
def open_game_screen():

    global deck

    #Login Widgets verstecken
    title_label.pack_forget()

    username_label.pack_forget()
    username_entry.pack_forget()

    password_label.pack_forget()
    password_entry.pack_forget()

    login_button.pack_forget()
    register_button.pack_forget()

    #Spiel Widgets anzeigen
    info_label.pack(pady=10)

    dealer_title.pack(pady=5)
    dealer_cards_label.pack()
    dealer_points_label.pack()

    separator.pack(pady=10)

    player_title.pack(pady=5)
    player_cards_label.pack()
    player_points_label.pack()

    result_label.pack(pady=10)

    bet_label.pack()
    bet_entry.pack(pady=5)

    button_frame.pack(pady=10)

    #Neues Deck erstellen
    deck = bj.create_deck()

    #Deck mischen
    bj.shuffle_deck(deck)

    update_info()


#========================
# LOGIN / REGISTER
#========================

#Login
def login():

    global current_user

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    #Leere Felder prüfen
    if username == "" or password == "":

        messagebox.showerror(
            "Fehler",
            "Bitte Benutzername und Passwort eingeben."
        )

        return

    #Username Länge prüfen
    if len(username) > 20:

        messagebox.showerror(
            "Fehler",
            "Username zu lang."
        )

        return

    #Login prüfen
    user = db_editor.login(
        username,
        password
    )

    #Fehlerhafter Login
    if user is None:

        messagebox.showerror(
            "Fehler",
            "Login fehlgeschlagen."
        )

        return

    current_user = username

    open_game_screen()


#Registrieren
def register():

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    #Leere Felder prüfen
    if username == "" or password == "":

        messagebox.showerror(
            "Fehler",
            "Bitte Benutzername und Passwort eingeben."
        )

        return

    #Username Länge prüfen
    if len(username) > 20:

        messagebox.showerror(
            "Fehler",
            "Username zu lang."
        )

        return

    #Passwort Länge prüfen
    if len(password) < 4:

        messagebox.showerror(
            "Fehler",
            "Passwort muss mindestens 4 Zeichen haben."
        )

        return

    #Spieler erstellen
    success = db_editor.create_player(
        username,
        password
    )

    #Username existiert bereits
    if not success:

        messagebox.showerror(
            "Fehler",
            "Username existiert bereits."
        )

        return

    messagebox.showinfo(
        "Erfolg",
        "Account erfolgreich erstellt."
    )


#========================
# SPIEL LOGIK
#========================

#Neue Runde starten
def start_game():

    global deck
    global player_hand
    global dealer_hand
    global bet
    global game_running

    #Prüfen ob bereits ein Spiel läuft
    if game_running:

        messagebox.showwarning(
            "Fehler",
            "Das aktuelle Spiel läuft noch."
        )

        return

    #Tokens laden
    tokens = db_editor.get_tokens(current_user)

    #Einsatz prüfen
    try:

        bet = int(bet_entry.get())

    except ValueError:

        messagebox.showerror(
            "Fehler",
            "Bitte gültigen Einsatz eingeben."
        )

        return

    #Ungültiger Einsatz
    if bet <= 0:

        messagebox.showerror(
            "Fehler",
            "Einsatz muss größer als 0 sein."
        )

        return

    #Zu wenig Tokens
    if bet > tokens:

        messagebox.showerror(
            "Fehler",
            "Nicht genug Tokens."
        )

        return

    #Startkarten ziehen
    player_hand = [
        bj.draw_card(deck),
        bj.draw_card(deck)
    ]

    dealer_hand = [
        bj.draw_card(deck),
        bj.draw_card(deck)
    ]

    game_running = True

    #Einsatzfeld sperren
    bet_entry.config(state="disabled")

    set_game_buttons("normal")

    result_label.config(text="")

    update_cards(hidden_dealer=True)

    #Blackjack prüfen
    player_value = bj.hand_value(player_hand)
    dealer_value = bj.hand_value(dealer_hand)

    #Spieler Blackjack
    if player_value == 21 and dealer_value != 21:

        db_editor.change_tokens(
            current_user,
            bet * 1.5
        )

        db_editor.add_win(current_user)

        db_editor.update_profit(
            current_user,
            bet * 1.5
        )

        result_label.config(
            text="BLACKJACK! Du gewinnst!"
        )

        game_running = False

        set_game_buttons("disabled")

        bet_entry.config(state="normal")

        update_cards(hidden_dealer=False)

        update_info()

        return

    #Dealer Blackjack
    if dealer_value == 21 and player_value != 21:

        db_editor.change_tokens(
            current_user,
            -bet
        )

        db_editor.add_loss(current_user)

        db_editor.update_profit(
            current_user,
            -bet
        )

        result_label.config(
            text="Dealer hat Blackjack!"
        )

        game_running = False

        set_game_buttons("disabled")

        bet_entry.config(state="normal")

        update_cards(hidden_dealer=False)

        update_info()

        return

    #Beide Blackjack
    if dealer_value == 21 and player_value == 21:

        db_editor.add_game(current_user)

        result_label.config(
            text="Beide haben Blackjack! Unentschieden!"
        )

        game_running = False

        set_game_buttons("disabled")

        bet_entry.config(state="normal")

        update_cards(hidden_dealer=False)

        update_info()

        return


#Spieler zieht Karte
def hit():

    global game_running

    #Prüfen ob Spiel läuft
    if not game_running:
        return

    #Neue Karte ziehen
    player_hand.append(
        bj.draw_card(deck)
    )

    update_cards(hidden_dealer=True)

    #Bust prüfen
    if bj.hand_value(player_hand) > 21:

        db_editor.change_tokens(
            current_user,
            -bet
        )

        db_editor.add_loss(current_user)

        db_editor.update_profit(
            current_user,
            -bet
        )

        result_label.config(
            text="Bust! Du verlierst!"
        )

        game_running = False

        set_game_buttons("disabled")

        #Einsatzfeld wieder freigeben
        bet_entry.config(state="normal")

        #Dealer zieht keine Karten mehr
        update_cards(hidden_dealer=False)

        update_info()


#Spieler bleibt stehen
def stand():

    global game_running

    #Prüfen ob Spiel läuft
    if not game_running:
        return

    #Dealer spielt
    bj.dealer_play(
        deck,
        dealer_hand
    )

    #Gewinner berechnen
    result = bj.compare_hands(
        player_hand,
        dealer_hand
    )

    #Spieler gewinnt
    if result == "player_win":

        db_editor.change_tokens(
            current_user,
            bet
        )

        db_editor.add_win(current_user)

        db_editor.update_profit(
            current_user,
            bet
        )

        result_label.config(
            text="Du gewinnst!"
        )

    #Dealer gewinnt
    elif result == "dealer_win":

        db_editor.change_tokens(
            current_user,
            -bet
        )

        db_editor.add_loss(current_user)

        db_editor.update_profit(
            current_user,
            -bet
        )

        result_label.config(
            text="Dealer gewinnt!"
        )

    #Dealer Bust
    elif result == "dealer_bust":

        db_editor.change_tokens(
            current_user,
            bet
        )

        db_editor.add_win(current_user)

        db_editor.update_profit(
            current_user,
            bet
        )

        result_label.config(
            text="Dealer Bust! Du gewinnst!"
        )

    #Unentschieden
    else:

        db_editor.add_game(current_user)

        result_label.config(
            text="Unentschieden!"
        )

    game_running = False

    set_game_buttons("disabled")

    #Einsatzfeld wieder freigeben
    bet_entry.config(state="normal")

    update_cards(hidden_dealer=False)

    update_info()


#========================
# LOGIN SCREEN
#========================

#Titel
title_label = tk.Label(
    root,
    text="BLACKJACK",
    font=("Arial", 28, "bold"),
    bg="#0B3D2E",
    fg="white"
)

title_label.pack(pady=30)


#Benutzername Label
username_label = tk.Label(
    root,
    text="Benutzername",
    font=("Arial", 14),
    bg="#0B3D2E",
    fg="white"
)

username_label.pack()


#Benutzername Eingabe
username_entry = tk.Entry(
    root,
    font=("Arial", 14),
    width=25
)

username_entry.pack(pady=10)


#Passwort Label
password_label = tk.Label(
    root,
    text="Passwort",
    font=("Arial", 14),
    bg="#0B3D2E",
    fg="white"
)

password_label.pack()


#Passwort Eingabe
password_entry = tk.Entry(
    root,
    font=("Arial", 14),
    width=25,
    show="*"
)

password_entry.pack(pady=10)


#Login Button
login_button = tk.Button(
    root,
    text="Login",
    font=("Arial", 14),
    width=20,
    command=login
)

login_button.pack(pady=10)


#Register Button
register_button = tk.Button(
    root,
    text="Registrieren",
    font=("Arial", 14),
    width=20,
    command=register
)

register_button.pack(pady=10)


#Enter Taste für Login
root.bind(
    "<Return>",
    lambda event: login()
)


#========================
# SPIEL SCREEN
#========================

#Spielerinformationen
info_label = tk.Label(
    root,
    text="",
    font=("Arial", 14),
    bg="#0B3D2E",
    fg="white"
)


#Dealer Titel
dealer_title = tk.Label(
    root,
    text="DEALER",
    font=("Arial", 20, "bold"),
    bg="#0B3D2E",
    fg="white"
)


#Dealer Karten
dealer_cards_label = tk.Label(
    root,
    text="",
    font=("Courier New", 14),
    bg="#0B3D2E",
    fg="white",
    justify="left"
)


#Dealer Punkte
dealer_points_label = tk.Label(
    root,
    text="",
    font=("Arial", 14),
    bg="#0B3D2E",
    fg="white"
)


#Trennlinie
separator = tk.Label(
    root,
    text="----------------------------------------",
    font=("Arial", 16),
    bg="#0B3D2E",
    fg="white"
)


#Player Titel
player_title = tk.Label(
    root,
    text="PLAYER",
    font=("Arial", 20, "bold"),
    bg="#0B3D2E",
    fg="white"
)


#Player Karten
player_cards_label = tk.Label(
    root,
    text="",
    font=("Courier New", 14),
    bg="#0B3D2E",
    fg="white",
    justify="left"
)


#Player Punkte
player_points_label = tk.Label(
    root,
    text="",
    font=("Arial", 14),
    bg="#0B3D2E",
    fg="white"
)


#Ergebnis Label
result_label = tk.Label(
    root,
    text="",
    font=("Arial", 18, "bold"),
    bg="#0B3D2E",
    fg="gold"
)


#Einsatz Label
bet_label = tk.Label(
    root,
    text="Einsatz",
    font=("Arial", 14),
    bg="#0B3D2E",
    fg="white"
)


#Einsatz Eingabe
bet_entry = tk.Entry(
    root,
    font=("Arial", 14),
    width=15
)

bet_entry.insert(0, "10")


#========================
# BUTTONS
#========================

#Button Frame
button_frame = tk.Frame(
    root,
    bg="#0B3D2E"
)


#Neue Runde Button
start_button = tk.Button(
    button_frame,
    text="Neue Runde",
    font=("Arial", 14),
    width=15,
    command=start_game
)

start_button.grid(row=0, column=0, padx=10)


#Hit Button
hit_button = tk.Button(
    button_frame,
    text="Hit",
    font=("Arial", 14),
    width=15,
    command=hit,
    state="disabled"
)

hit_button.grid(row=0, column=1, padx=10)


#Stand Button
stand_button = tk.Button(
    button_frame,
    text="Stand",
    font=("Arial", 14),
    width=15,
    command=stand,
    state="disabled"
)

stand_button.grid(row=0, column=2, padx=10)


#========================
# PROGRAMM STARTEN
#========================

root.mainloop()