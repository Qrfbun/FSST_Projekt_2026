"""
devs: Joel Walder, Johannes Kuen, Alexander Beck

Einfaches Blackjack-Spiel mit:
Tkinter GUI
SQLite Datenbank
Login / Registrierung
Blackjack Logik
"""

import tkinter as tk
from tkinter import messagebox

import blackjack as bj
import db_editor

#==============================================================================
# HAUPTFENSTER INITIALISIERUNG
#==============================================================================

root = tk.Tk()
root.title("Blackjack")
root.geometry("1000x850")
root.configure(bg="#0B3D2E")

# Fenstergröße fixieren, um Layout-Verschiebungen zu verhindern
root.resizable(False, False)


#==============================================================================
# GLOBALE VARIABLEN
#==============================================================================

current_user = None    # Speichert den aktuell eingeloggten Benutzernamen
deck = []              # Das aktuelle Kartendeck
player_hand = []       # Karten auf der Hand des Spielers
dealer_hand = []       # Karten auf der Hand des Dealers
bet = 0                # Aktueller Einsatz in der Runde
game_running = False   # Status, ob gerade eine aktive Runde läuft
current_frame = None   # Hält den aktuell sichtbaren Frame im Fokus


#==============================================================================
# FRAME-MANAGEMENT (SEITENWECHSEL)
#==============================================================================

# Definition aller Haupt-Container (Frames) für die verschiedenen Ansichten
login_frame = tk.Frame(root, bg="#0B3D2E")
game_frame = tk.Frame(root, bg="#0B3D2E")
change_pw_frame = tk.Frame(root, bg="#0B3D2E")
change_user_frame = tk.Frame(root, bg="#0B3D2E")
stats_frame = tk.Frame(root, bg="#0B3D2E")

def switch_frame(target_frame):
    """Versteckt den aktuell aktiven Frame und zeigt den gewünschten Ziel-Frame an."""
    global current_frame
    
    # Falls bereits ein Frame sichtbar ist, packen wir ihn weg
    if current_frame:
        current_frame.pack_forget()
        
    # Setzen des neuen Frames und füllen des gesamten Fensters
    current_frame = target_frame
    current_frame.pack(fill="both", expand=True)


#==============================================================================
# HILFSFUNKTIONEN & VALIDIERUNGEN
#==============================================================================

def update_info():
    """Holt die aktuellen Tokens aus der DB und aktualisiert die Anzeige."""
    tokens = db_editor.get_tokens(current_user)
    info_label.config(
        text=f"Benutzer: {current_user} | Tokens: {tokens}"
    )

def update_cards(hidden_dealer=True):
    """Aktualisiert die ASCII-Karten und die dazugehörigen Punktestände."""
    # Dealer-Karten (zweite Karte eventuell verdeckt)
    dealer_cards_label.config(
        text=bj.hand_to_ascii(dealer_hand, hide_second=hidden_dealer)
    )

    # Dealer-Punkte basierend auf Sichtbarkeit anzeigen
    if hidden_dealer:
        dealer_points_label.config(text="Punkte: ?")
    else:
        dealer_points_label.config(text=f"Punkte: {bj.hand_value(dealer_hand)}")

    # Spieler-Karten und Punkte immer offen anzeigen
    player_cards_label.config(text=bj.hand_to_ascii(player_hand))
    player_points_label.config(text=f"Punkte: {bj.hand_value(player_hand)}")

def set_game_buttons(state):
    """Aktiviert oder deaktiviert die Spiel-Buttons (Hit / Stand)."""
    hit_button.config(state=state)
    stand_button.config(state=state)

def open_game_screen():
    """Initialisiert das Spiel, mischt das Deck und wechselt zum Game-Screen."""
    global deck
    deck = bj.create_deck()
    bj.shuffle_deck(deck)
    update_info()
    switch_frame(game_frame)

def check_settings_allowed():
    """Verhindert den Wechsel in die Einstellungen, wenn eine Runde läuft."""
    if game_running:
        messagebox.showwarning("Fehler", "Bitte beende zuerst das aktuelle Spiel!")
        return False
    return True


#==============================================================================
# EINSTELLUNGEN-LOGIK (ZUGRIFF AUF DB_EDITOR)
#==============================================================================

def submit_change_password():
    """Übergibt Altes und Neues Passwort an die DB und prüft das Resultat."""
    old_pw = old_pw_entry.get().strip()
    new_pw = new_pw_entry.get().strip()
    
    # Eingabeprüfung auf leere Felder
    if not old_pw or not new_pw:
        messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen.")
        return
        
    # Sicherheitsprüfung für das neue Passwort
    if len(new_pw) < 4:
        messagebox.showerror("Fehler", "Das neue Passwort muss mindestens 4 Zeichen haben.")
        return

    # Aufruf der DB-Funktion. Gibt True zurück, wenn das alte PW stimmte und geändert wurde
    success = db_editor.change_password(current_user, new_pw, old_pw)
    if success:
        messagebox.showinfo("Erfolg", "Passwort erfolgreich geändert.")
        old_pw_entry.delete(0, tk.END)
        new_pw_entry.delete(0, tk.END)
        switch_frame(game_frame)
    else:
        # Fehlermeldung, falls das alte Passwort in der DB nicht übereinstimmte
        messagebox.showerror("Fehler", "Altes Passwort ist nicht korrekt!")

def submit_change_username():
    """Übergibt den neuen Usernamen an die DB und validiert das Ergebnis."""
    global current_user
    new_user = new_user_entry.get().strip()
    
    # Eingabeprüfung auf leeren String
    if not new_user:
        messagebox.showerror("Fehler", "Bitte einen Benutzernamen eingeben.")
        return
        
    # Längenbegrenzung einhalten
    if len(new_user) > 20:
        messagebox.showerror("Fehler", "Username zu lang (max. 20 Zeichen).")
        return

    # Aufruf der DB-Funktion. Gibt True zurück, wenn der Name frei war und geändert wurde
    success = db_editor.change_username(current_user, new_user)
    if success:
        messagebox.showinfo("Erfolg", f"Benutzername erfolgreich geändert in: {new_user}")
        current_user = new_user
        update_info()
        new_user_entry.delete(0, tk.END)
        switch_frame(game_frame)
    else:
        # Fehlermeldung, falls der Username bereits vergeben ist
        messagebox.showerror("Fehler", "Username existiert bereits oder Änderung fehlgeschlagen.")

def open_stats_screen():
    """Liest die Statistiken aus der DB und bereitet sie für das Label auf."""
    if not check_settings_allowed():
        return
        
    # Statistiken abrufen
    stats = db_editor.get_stats(current_user)
    
    # DB liefert (Username, Token, Profit, Games_played, Games_won, Games_lost)
    if len(stats) == 6:
        stats_text = (f"Username: {stats[0]}\n\n"
                      f"Tokens: {stats[1]}\n\n"
                      f"Profit: {stats[2]}\n\n"
                      f"Games played: {stats[3]}\n\n"
                      f"Games won: {stats[4]}\n\n"
                      f"Games lost: {stats[5]}")
  
    else:
        # Fallback, falls das Format unerwartet ist
        stats_text = f"Statistiken konnten nicht korrekt geladen werden.\nRohdaten: {stats}"
        
    # Text im Stats-Frame setzen und dorthin wechseln
    stats_display_label.config(text=stats_text)
    switch_frame(stats_frame)

def logout():
    """Loggt den aktuellen Benutzer aus und setzt die Session zurück."""
    global current_user, game_running
    
    # Ausloggen mitten im Spiel unterbinden
    if game_running:
        messagebox.showwarning("Fehler", "Beende zuerst das aktuelle Spiel!")
        return
        
    # Session-Variablen zurücksetzen
    current_user = None
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    
    # Zurück zum Login-Bildschirm
    switch_frame(login_frame)


#==============================================================================
# AUTHENTIFIZIERUNG (LOGIN & REGISTRIERUNG)
#==============================================================================

def login():
    global current_user
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if username == "" or password == "":
        messagebox.showerror("Fehler", "Bitte Benutzername und Passwort eingeben.")
        return

    if len(username) > 20:
        messagebox.showerror("Fehler", "Username zu lang.")
        return

    user = db_editor.login(username, password)
    if user is None:
        messagebox.showerror("Fehler", "Login fehlgeschlagen.")
        return

    current_user = username
    open_game_screen()

def register():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if username == "" or password == "":
        messagebox.showerror("Fehler", "Bitte Benutzername und Passwort eingeben.")
        return

    if len(username) > 20:
        messagebox.showerror("Fehler", "Username zu lang.")
        return

    if len(password) < 4:
        messagebox.showerror("Fehler", "Passwort muss mindestens 4 Zeichen haben.")
        return

    success = db_editor.create_player(username, password)
    if not success:
        messagebox.showerror("Fehler", "Username existiert bereits.")
        return

    messagebox.showinfo("Erfolg", "Account erfolgreich erstellt.")


#==============================================================================
# IN-GAME BLACKJACK LOGIK
#==============================================================================

def start_game():
    global deck, player_hand, dealer_hand, bet, game_running

    if game_running:
        messagebox.showwarning("Fehler", "Das aktuelle Spiel läuft noch.")
        return

    tokens = db_editor.get_tokens(current_user)

    try:
        bet = int(bet_entry.get())
    except ValueError:
        messagebox.showerror("Fehler", "Bitte gültigen Einsatz eingeben.")
        return

    if bet <= 0:
        messagebox.showerror("Fehler", "Einsatz muss größer als 0 sein.")
        return

    if bet > tokens:
        messagebox.showerror("Fehler", "Nicht genug Tokens.")
        return

    # Startkarten für beide Parteien ziehen
    player_hand = [bj.draw_card(deck), bj.draw_card(deck)]
    dealer_hand = [bj.draw_card(deck), bj.draw_card(deck)]
    game_running = True

    # GUI-Zustände während der Runde anpassen
    bet_entry.config(state="disabled")
    set_game_buttons("normal")
    result_label.config(text="")
    update_cards(hidden_dealer=True)

    player_value = bj.hand_value(player_hand)
    dealer_value = bj.hand_value(dealer_hand)

    # Sofortige Blackjack-Überprüfung beim Austeilen
    if player_value == 21 and dealer_value != 21:
        db_editor.change_tokens(current_user, bet * 1.5)
        db_editor.add_win(current_user)
        db_editor.update_profit(current_user, bet * 1.5)
        result_label.config(text="BLACKJACK! Du gewinnst!")
        end_round()

    elif dealer_value == 21 and player_value != 21:
        db_editor.change_tokens(current_user, -bet)
        db_editor.add_loss(current_user)
        db_editor.update_profit(current_user, -bet)
        result_label.config(text="Dealer hat Blackjack!")
        end_round()

    elif dealer_value == 21 and player_value == 21:
        db_editor.add_game(current_user)
        result_label.config(text="Beide haben Blackjack! Unentschieden!")
        end_round()

def hit():
    global game_running
    if not game_running:
        return

    player_hand.append(bj.draw_card(deck))
    update_cards(hidden_dealer=True)

    # Überkauft-Prüfung (Bust)
    if bj.hand_value(player_hand) > 21:
        db_editor.change_tokens(current_user, -bet)
        db_editor.add_loss(current_user)
        db_editor.update_profit(current_user, -bet)
        result_label.config(text="Bust! Du verlierst!")
        end_round()

def stand():
    global game_running
    if not game_running:
        return

    # Dealer zieht nach seinen Regeln
    bj.dealer_play(deck, dealer_hand)
    result = bj.compare_hands(player_hand, dealer_hand)

    # Auswertung des Ergebnisses und DB-Aktualisierung
    if result == "player_win":
        db_editor.change_tokens(current_user, bet)
        db_editor.add_win(current_user)
        db_editor.update_profit(current_user, bet)
        result_label.config(text="Du gewinnst!")

    elif result == "dealer_win":
        db_editor.change_tokens(current_user, -bet)
        db_editor.add_loss(current_user)
        db_editor.update_profit(current_user, -bet)
        result_label.config(text="Dealer gewinnt!")

    elif result == "dealer_bust":
        db_editor.change_tokens(current_user, bet)
        db_editor.add_win(current_user)
        db_editor.update_profit(current_user, bet)
        result_label.config(text="Dealer Bust! Du gewinnst!")

    else:
        db_editor.add_game(current_user)
        result_label.config(text="Unentschieden!")

    end_round()

def end_round():
    """Setzt den Rundenstatus zurück und reaktiviert die Eingaben."""

    tokens = db_editor.get_tokens(current_user)
    if tokens <= 0:
        messagebox.showinfo("Game Over", "Du hast keine Tokens mehr! Hie bekommst du 100 Tokens als Trostpreis.")
        db_editor.update_tokens(current_user, 100)
        update_info()
        
    global game_running
    game_running = False
    set_game_buttons("disabled")
    bet_entry.config(state="normal")
    update_cards(hidden_dealer=False)
    update_info()


#==============================================================================
# UI AUFBAU: LOGIN FRAME
#==============================================================================

title_label = tk.Label(login_frame, text="BLACKJACK", font=("Arial", 28, "bold"), bg="#0B3D2E", fg="white")
title_label.pack(pady=30)

username_label = tk.Label(login_frame, text="Benutzername", font=("Arial", 14), bg="#0B3D2E", fg="white")
username_label.pack()
username_entry = tk.Entry(login_frame, font=("Arial", 14), width=25)
username_entry.pack(pady=10)

password_label = tk.Label(login_frame, text="Passwort", font=("Arial", 14), bg="#0B3D2E", fg="white")
password_label.pack()
password_entry = tk.Entry(login_frame, font=("Arial", 14), width=25, show="*")
password_entry.pack(pady=10)

login_button = tk.Button(login_frame, text="Login", font=("Arial", 14), width=20, command=login)
login_button.pack(pady=10)

register_button = tk.Button(login_frame, text="Registrieren", font=("Arial", 14), width=20, command=register)
register_button.pack(pady=10)


#==============================================================================
# UI AUFBAU: GAME FRAME
#==============================================================================

info_label = tk.Label(game_frame, text="", font=("Arial", 14), bg="#0B3D2E", fg="white")
info_label.pack(pady=10)

dealer_title = tk.Label(game_frame, text="DEALER", font=("Arial", 20, "bold"), bg="#0B3D2E", fg="white")
dealer_title.pack(pady=5)
dealer_cards_label = tk.Label(game_frame, text="", font=("Courier New", 14), bg="#0B3D2E", fg="white", justify="left")
dealer_cards_label.pack()
dealer_points_label = tk.Label(game_frame, text="", font=("Arial", 14), bg="#0B3D2E", fg="white")
dealer_points_label.pack()

separator = tk.Label(game_frame, text="----------------------------------------", font=("Arial", 16), bg="#0B3D2E", fg="white")
separator.pack(pady=10)

player_title = tk.Label(game_frame, text="PLAYER", font=("Arial", 20, "bold"), bg="#0B3D2E", fg="white")
player_title.pack(pady=5)
player_cards_label = tk.Label(game_frame, text="", font=("Courier New", 14), bg="#0B3D2E", fg="white", justify="left")
player_cards_label.pack()
player_points_label = tk.Label(game_frame, text="", font=("Arial", 14), bg="#0B3D2E", fg="white")
player_points_label.pack()

result_label = tk.Label(game_frame, text="", font=("Arial", 18, "bold"), bg="#0B3D2E", fg="gold")
result_label.pack(pady=10)

bet_label = tk.Label(game_frame, text="Einsatz", font=("Arial", 14), bg="#0B3D2E", fg="white")
bet_label.pack()
bet_entry = tk.Entry(game_frame, font=("Arial", 14), width=15)
bet_entry.pack(pady=5)
bet_entry.insert(0, "10")

# Spielfluss Steuerungs-Buttons (Runde, Hit, Stand)
button_frame = tk.Frame(game_frame, bg="#0B3D2E")
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Neue Runde", font=("Arial", 14), width=15, command=start_game)
start_button.grid(row=0, column=0, padx=10)
hit_button = tk.Button(button_frame, text="Hit", font=("Arial", 14), width=15, command=hit, state="disabled")
hit_button.grid(row=0, column=1, padx=10)
stand_button = tk.Button(button_frame, text="Stand", font=("Arial", 14), width=15, command=stand, state="disabled")
stand_button.grid(row=0, column=2, padx=10)

# Trennlinie zum Einstellungs-Bereich
settings_separator = tk.Label(game_frame, text="========================================", font=("Arial", 12), bg="#0B3D2E", fg="#1E6B52")
settings_separator.pack(pady=15)

# Die untere Leiste für Account-Einstellungen & Logout
settings_bar = tk.Frame(game_frame, bg="#0B3D2E")
settings_bar.pack(pady=5)

pw_change_btn = tk.Button(settings_bar, text="Passwort ändern", font=("Arial", 11), width=16, 
                          command=lambda: switch_frame(change_pw_frame) if check_settings_allowed() else None)
pw_change_btn.grid(row=0, column=0, padx=5)

user_change_btn = tk.Button(settings_bar, text="Username ändern", font=("Arial", 11), width=16, 
                            command=lambda: switch_frame(change_user_frame) if check_settings_allowed() else None)
user_change_btn.grid(row=0, column=1, padx=5)

stats_btn = tk.Button(settings_bar, text="Statistiken", font=("Arial", 11), width=16, command=open_stats_screen)
stats_btn.grid(row=0, column=2, padx=5)

logout_btn = tk.Button(settings_bar, text="Abmelden", font=("Arial", 11), width=16, bg="#7A1E1E", fg="white", command=logout)
logout_btn.grid(row=0, column=3, padx=5)


#==============================================================================
# UI AUFBAU: PASSWORD CHANGE FRAME
#==============================================================================

tk.Label(change_pw_frame, text="Passwort ändern", font=("Arial", 24, "bold"), bg="#0B3D2E", fg="white").pack(pady=30)

tk.Label(change_pw_frame, text="Altes Passwort", font=("Arial", 14), bg="#0B3D2E", fg="white").pack(pady=5)
old_pw_entry = tk.Entry(change_pw_frame, font=("Arial", 14), width=25, show="*")
old_pw_entry.pack(pady=5)

tk.Label(change_pw_frame, text="Neues Passwort", font=("Arial", 14), bg="#0B3D2E", fg="white").pack(pady=5)
new_pw_entry = tk.Entry(change_pw_frame, font=("Arial", 14), width=25, show="*")
new_pw_entry.pack(pady=5)

tk.Button(change_pw_frame, text="Bestätigen", font=("Arial", 14), width=20, command=submit_change_password).pack(pady=20)
tk.Button(change_pw_frame, text="Zurück", font=("Arial", 12), width=15, command=lambda: switch_frame(game_frame)).pack(pady=5)


#==============================================================================
# UI AUFBAU: USERNAME CHANGE FRAME
#==============================================================================

tk.Label(change_user_frame, text="Benutzername ändern", font=("Arial", 24, "bold"), bg="#0B3D2E", fg="white").pack(pady=30)

tk.Label(change_user_frame, text="Neuer Benutzername", font=("Arial", 14), bg="#0B3D2E", fg="white").pack(pady=5)
new_user_entry = tk.Entry(change_user_frame, font=("Arial", 14), width=25)
new_user_entry.pack(pady=5)

tk.Button(change_user_frame, text="Bestätigen", font=("Arial", 14), width=20, command=submit_change_username).pack(pady=20)
tk.Button(change_user_frame, text="Zurück", font=("Arial", 12), width=15, command=lambda: switch_frame(game_frame)).pack(pady=5)


#==============================================================================
# UI AUFBAU: STATS FRAME
#==============================================================================

tk.Label(stats_frame, text="Deine Statistiken", font=("Arial", 24, "bold"), bg="#0B3D2E", fg="gold").pack(pady=30)

# Dieses Label wird dynamisch durch open_stats_screen befüllt
stats_display_label = tk.Label(stats_frame, text="", font=("Arial", 16), bg="#0B3D2E", fg="white", justify="center")
stats_display_label.pack(pady=20)

tk.Button(stats_frame, text="Zurück zum Spiel", font=("Arial", 14), width=20, command=lambda: switch_frame(game_frame)).pack(pady=20)


#==============================================================================
# ANWENDUNGSSTART
#==============================================================================

# Enter-Taste führt den Login nur aus, solange der User im Login-Fenster ist
root.bind("<Return>", lambda event: login() if current_frame == login_frame else None)

# Setzen des initialen Frames beim Programmstart
switch_frame(login_frame)

root.mainloop()