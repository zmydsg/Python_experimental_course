import random
import math

# Define constants
NUM_DECKS = 6
RESHUFFLE_THRESHOLD = 10  # reshuffle when fewer than 10 cards remain
NUM_GAMES = 10000

# Card values and Hi-Lo count values
CARD_VALUES = {
    **{str(i): i for i in range(2, 10)},
    '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
}
HI_LO_COUNT = {
    **{str(i): 1 for i in range(2, 7)},
    **{str(i): 0 for i in range(7, 10)},
    '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
}

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        self.cards = []
        for _ in range(NUM_DECKS):
            for card in CARD_VALUES:
                self.cards += [card] * 4
        random.shuffle(self.cards)
        self.running_count = 0

    def draw(self):
        if len(self.cards) < RESHUFFLE_THRESHOLD:
            self.reset()
        card = self.cards.pop()
        self.running_count += HI_LO_COUNT[card]
        return card

    def true_count(self):
        # remaining decks
        decks_remaining = max(len(self.cards) / 52, 1)
        return self.running_count / decks_remaining

def hand_value(hand):
    # calculate best blackjack hand value with aces
    values = [CARD_VALUES[c] for c in hand]
    total = sum(values)
    # adjust aces from 11 to 1 as needed
    aces = hand.count('A')
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def play_bank(deck):
    hand = [deck.draw(), deck.draw()]
    while hand_value(hand) < 17:
        hand.append(deck.draw())
    return hand_value(hand)

def play_player(deck):
    hand = [deck.draw(), deck.draw()]
    while True:
        tc = deck.true_count()
        # dynamic threshold: 12 + int(true_count), capped [12, 20]
        threshold = min(max(12, 14 + int(tc)), 15)
        if hand_value(hand) >= threshold:
            break
        hand.append(deck.draw())
        if hand_value(hand) > 21:
            break
    return hand_value(hand)

# Simulation
deck = Deck()
total_score = 0

for _ in range(NUM_GAMES):
    bet = 1
    tc = deck.true_count()
    if tc > 1:
        bet = min(int(tc), 10)
    player_total = play_player(deck)
    bank_total = play_bank(deck)

    # Determine outcome
    if player_total > 21 or (bank_total <= 21 and bank_total > player_total):
        total_score -= bet
    elif bank_total > 21 or player_total > bank_total:
        total_score += bet
    # push is 0

print(f"After {NUM_GAMES} games, total score: {total_score}")
