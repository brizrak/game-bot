from pydantic import BaseModel


class Stats(BaseModel):
    total_games: int
    wins: int
    loses: int
    draws: int


class UserData(BaseModel):
    id: int
    full_name: str
    score: int
    balance: int
    blackjack_stats: Stats
    seabattle_stats: Stats
    fool_stats: Stats
