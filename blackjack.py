"""
Autor: Joel Walder, Johannes Kuen, Alexander Beck
Dieses Skript enthält die gesamte Blackjack-Logik:
Kartendeck, Kartenwerte, Ass-Regel und ASCII-Anzeige.
"""

import random


#Alle Kartenwerte
CARD_VALUES = [
    "A", "2", "3", "4", "5",
    "6", "7", "8", "9", "10",
    "J", "Q", "K"
]

#Alle Kartenfarben
CARD_SUITS = ["♠", "♥", "♦", "♣"]


#Komplettes Kartendeck erstellen
def create_deck():
    deck = []

    for suit in CARD_SUITS:
        for value in CARD_VALUES:
            deck.append((value, suit))

    return deck


#Deck mischen
def shuffle_deck(deck):
    random.shuffle(deck)


#Eine Karte ziehen
def draw_card(deck):
    if len(deck) == 0:
        return None

    return deck.pop()


#Wert einer einzelnen Karte berechnen
def card_value(card_value_text):
    if card_value_text in ["J", "Q", "K"]:
        return 10

    if card_value_text == "A":
        return 11

    return int(card_value_text)


#Wert einer Hand berechnen
def hand_value(hand):
    value = 0
    aces = 0

    for card in hand:
        card_text = card[0]

        if card_text == "A":
            value += 11
            aces += 1
        elif card_text in ["J", "Q", "K"]:
            value += 10
        else:
            value += int(card_text)

    #Asse von 11 auf 1 reduzieren falls die Hand sonst über 21 ist
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1

    return value


#Prüfen ob der Dealer noch ziehen muss
def dealer_should_hit(hand):
    return hand_value(hand) < 17


#Prüfen wer gewonnen hat
def compare_hands(player_hand, dealer_hand):
    player_total = hand_value(player_hand)
    dealer_total = hand_value(dealer_hand)

    if player_total > 21:
        return "player_bust"

    if dealer_total > 21:
        return "dealer_bust"

    if player_total > dealer_total:
        return "player_win"

    if player_total < dealer_total:
        return "dealer_win"

    return "push"


#Eine einzelne Karte als ASCII darstellen
def card_to_ascii(card, hidden=False):
    if hidden:
        return [
            "┌─────┐",
            "│░░░░░│",
            "│░░░░░│",
            "│░░░░░│",
            "└─────┘"
        ]

    value = card[0]
    suit = card[1]

    left = f"{value:<2}"
    right = f"{value:>2}"

    return [
        "┌─────┐",
        f"│ {left}    │",
        f"│   {suit}   │",
        f"│    {right} │",
        "└─────┘"
    ]


#Eine Hand als ASCII-Bild zusammenbauen
def hand_to_ascii(hand, hidden_second_card=False):
    if len(hand) == 0:
        return "(keine Karten)"

    all_cards = []

    for index, card in enumerate(hand):
        if hidden_second_card and index == 1:
            all_cards.append(card_to_ascii(card, hidden=True))
        else:
            all_cards.append(card_to_ascii(card, hidden=False))

    lines = ["", "", "", "", ""]
    for card_lines in all_cards:
        for i in range(5):
            lines[i] += card_lines[i] + " "

    return "\n".join(lines)


#Hand mit Titel als Text zurückgeben
def hand_summary(title, hand, hidden_second_card=False):
    text = f"{title}:\n"
    text += hand_to_ascii(hand, hidden_second_card=hidden_second_card)

    if not hidden_second_card:
        text += f"\nPunkte: {hand_value(hand)}"

    return text


#Dealer-Zug ausführen
def dealer_play(deck, dealer_hand):
    while dealer_should_hit(dealer_hand):
        card = draw_card(deck)

        if card is None:
            break

        dealer_hand.append(card)

    return dealer_hand