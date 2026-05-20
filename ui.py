import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit,
    QTextEdit, QStackedWidget,
    QMessageBox, QSpinBox
)

import db_editor
import blackjack as bj


#========================
# LOGIN SCREEN
#========================
class LoginScreen(QWidget):

    def __init__(self, switch_to_game):
        super().__init__()

        self.switch_to_game = switch_to_game

        layout = QVBoxLayout()

        #Titel
        self.title = QLabel("BLACKJACK LOGIN")
        layout.addWidget(self.title)

        #Inputs
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.username)
        layout.addWidget(self.password)

        #Buttons
        self.login_btn = QPushButton("Login")
        self.register_btn = QPushButton("Registrieren")

        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)

        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    #Login Logik
    def login(self):

        u = self.username.text().strip()
        p = self.password.text().strip()

        user = db_editor.login(u, p)

        if user is None:
            QMessageBox.warning(self, "Fehler", "Login fehlgeschlagen")
            return

        self.switch_to_game(u)

    #Register Logik
    def register(self):

        u = self.username.text().strip()
        p = self.password.text().strip()

        if db_editor.create_player(u, p):
            QMessageBox.information(self, "OK", "Account erstellt")
        else:
            QMessageBox.warning(self, "Fehler", "Username existiert bereits")


#========================
# GAME SCREEN
#========================
class GameScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.username = None
        self.deck = []
        self.player = []
        self.dealer = []
        self.bet = 0
        self.active = False

        layout = QVBoxLayout()

        #Info
        self.info = QLabel("Nicht eingeloggt")
        layout.addWidget(self.info)

        #Output
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        #Einsatz
        bet_layout = QHBoxLayout()

        self.bet_box = QSpinBox()
        self.bet_box.setMinimum(1)
        self.bet_box.setMaximum(100000)

        self.start_btn = QPushButton("Neue Runde")
        self.hit_btn = QPushButton("Hit")
        self.stand_btn = QPushButton("Stand")

        self.start_btn.clicked.connect(self.start_game)
        self.hit_btn.clicked.connect(self.hit)
        self.stand_btn.clicked.connect(self.stand)

        bet_layout.addWidget(self.bet_box)
        bet_layout.addWidget(self.start_btn)
        bet_layout.addWidget(self.hit_btn)
        bet_layout.addWidget(self.stand_btn)

        layout.addLayout(bet_layout)

        self.setLayout(layout)

        self.set_buttons(False)

    #Buttons aktivieren/deaktivieren
    def set_buttons(self, running):

        self.hit_btn.setEnabled(running)
        self.stand_btn.setEnabled(running)

    #User setzen
    def set_user(self, username):
        self.username = username
        self.update_info()

    #Info updaten
    def update_info(self):

        tokens = db_editor.get_tokens(self.username)

        self.info.setText(
            f"User: {self.username} | Tokens: {tokens}"
        )

    #Spiel starten
    def start_game(self):

        self.deck = bj.create_deck()
        bj.shuffle_deck(self.deck)

        self.player = [bj.draw_card(self.deck), bj.draw_card(self.deck)]
        self.dealer = [bj.draw_card(self.deck), bj.draw_card(self.deck)]

        self.bet = self.bet_box.value()
        self.active = True

        self.set_buttons(True)

        self.show_game(hidden=True)

    #Hit
    def hit(self):

        self.player.append(bj.draw_card(self.deck))

        if bj.hand_value(self.player) > 21:
            self.end_game()

        self.show_game(hidden=True)

    #Stand
    def stand(self):
        self.end_game()

    #Spiel beenden
    def end_game(self):

        self.dealer = bj.dealer_play(self.deck, self.dealer)

        result = bj.compare_hands(self.player, self.dealer)

        if result == "player_win":
            db_editor.change_tokens(self.username, self.bet)
            msg = "Du gewinnst!"

        elif result == "dealer_win":
            db_editor.change_tokens(self.username, -self.bet)
            msg = "Dealer gewinnt!"

        elif result == "dealer_bust":
            db_editor.change_tokens(self.username, self.bet)
            msg = "Dealer Bust!"

        elif result == "player_bust":
            db_editor.change_tokens(self.username, -self.bet)
            msg = "Player Bust!"

        else:
            msg = "Unentschieden"

        self.active = False
        self.set_buttons(False)

        self.show_game(hidden=False, result=msg)
        self.update_info()

    #Spiel anzeigen
    def show_game(self, hidden=False, result=None):

        text = "\nBLACKJACK\n\n"

        text += bj.hand_summary("Dealer", self.dealer, hidden_second_card=hidden)
        text += "\n\n"
        text += bj.hand_summary("Player", self.player)

        if result:
            text += "\n\nERGEBNIS: " + result

        self.output.setText(text)


#========================
# MAIN WINDOW
#========================
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Blackjack")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        #Screens erstellen
        self.game_screen = GameScreen()
        self.login_screen = LoginScreen(self.login_success)

        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.game_screen)

    #Login erfolgreich -> Screen wechseln
    def login_success(self, username):

        self.game_screen.set_user(username)
        self.stack.setCurrentWidget(self.game_screen)


#App starten
def run_app():

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())