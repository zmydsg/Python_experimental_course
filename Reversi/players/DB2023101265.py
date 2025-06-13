from Reversi import *
import random

def player(Colour, Board):
    opponent = -Colour
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)


    WEIGHTS = [
        [100, -20, 10,  5,  5, 10, -20, 100],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [10,   -2,  0,   0,  0,   0,  -2,  10],
        [5,    -2,  0,   0,  0,   0,  -2,   5],
        [5,    -2,  0,   0,  0,   0,  -2,   5],
        [10,   -2,  0,   0,  0,   0,  -2,  10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [100, -20, 10,  5,  5, 10, -20, 100],
    ]

    best_score = float('-inf')

    candidates = []

    for x, y in moves:

        temp = BoardCopy(Board)
        PlaceMove(Colour, temp, x, y)


        weighted_score = 0
        for i in range(1, 9):
            for j in range(1, 9):
                c = temp[i][j]
                w = WEIGHTS[j-1][i-1]
                if c == Colour:
                    weighted_score += w
                elif c == opponent:
                    weighted_score -= w

        if weighted_score > best_score:
            best_score = weighted_score
            candidates = [ (x, y, temp) ]
        elif weighted_score == best_score:
            candidates.append( (x, y, temp) )

    min_opp_moves = float('inf')
    final_moves = []
    for x, y, board_after in candidates:
        opp_moves = len(PossibleMove(opponent, board_after))
        if opp_moves < min_opp_moves:
            min_opp_moves = opp_moves
            final_moves = [(x, y)]
        elif opp_moves == min_opp_moves:
            final_moves.append((x, y))

    return random.choice(final_moves)