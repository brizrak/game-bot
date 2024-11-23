from random import shuffle
lobby_list = [(250,1000), (1000,5000),(5000,15000)]
money = 10000

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