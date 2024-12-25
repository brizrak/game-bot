from random import shuffle

lobby_list = [(250, 1000), (1000, 5000), (5000, 15000)]


def create_deck():
    mast_list = ["cherv", "boob", "chip", "cross"]

    type_list = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "валет", "дама", "король", "туз"]
    deck = []
    # deck = [("cherv", "2"), ("boob", "2"), ("chip", "2"), ("cross", "2"), ("chip", "2"), ("boob", "2"), ("cherv", "2"), ("cherv", "2"), ("cherv", "2"), ("cherv", "2"), ("cherv", "2")]
    for el in mast_list:
        for elel in type_list:
            deck.append((el, elel))
    shuffle(deck)
    shuffle(deck)
    shuffle(deck)
    return deck


def stavkas():
    bet_list = []
    for bet0, bet1 in lobby_list:
        x = int(bet1) / int(bet0) + 1
        for i in range(1, int(x)):
            bet_list.append(int(bet0) * i)
    return bet_list


all_stavkas = stavkas()
