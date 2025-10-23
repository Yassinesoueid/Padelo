from typing import List, Tuple

def determine_winner_and_clean(set_scores: List[Tuple[int,int]]):
    sets_a = sum(1 for a,b in set_scores if a > b)
    sets_b = sum(1 for a,b in set_scores if b > a)
    winner = "A" if sets_a > sets_b else "B"
    clean = 1 if (sets_a==2 and sets_b==0) or (sets_b==2 and sets_a==0) else 0
    return winner, clean

def count_bagels(set_scores: List[Tuple[int,int]]):
    bagels_a = sum(1 for a,b in set_scores if a == 6 and b == 0)
    bagels_b = sum(1 for a,b in set_scores if b == 6 and a == 0)
    return bagels_a, bagels_b