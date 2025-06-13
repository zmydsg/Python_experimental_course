# Module for Python course project V3.0 2025
# This module is an example of player function to be submitted
from Reversi import * 
import copy

def player(Colour, Board):
    opponent = -Colour
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)
    best_move = moves[0]
    min_opponent_moves = float('inf')
    for move in moves:

        new_board = copy.deepcopy(Board)
        new_board = PlaceMove(Colour, new_board, move[0], move[1])

        opponent_moves = len(PossibleMove(opponent, new_board))

        if opponent_moves < min_opponent_moves:
            min_opponent_moves = opponent_moves
            best_move = move

    return best_move


