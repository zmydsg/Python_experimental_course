from Reversi import *
import random

corners = {(1,1), (1,8), (8,1), (8,8)}
x_squares = {(2,2), (2,7), (7,2), (7,7)}
c_squares = {(1,2), (2,1), (1,7), (2,8), (7,1), (8,2), (7,8), (8,7)}
edges = {(1,3), (1,4), (1,5), (1,6), (8,3), (8,4), (8,5), (8,6),
         (3,1), (4,1), (5,1), (6,1), (3,8), (4,8), (5,8), (6,8)}

POSITION_WEIGHTS = [
    [120, -20, 20, 5, 5, 20, -20, 120],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [120, -20, 20, 5, 5, 20, -20, 120]
]

def get_position_weight(x, y):
    return POSITION_WEIGHTS[y-1][x-1]

def count_pieces(board, color):
    count = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == color:
                count += 1
    return count

def evaluate_board(board, color):
    opponent = -color
    score = 0
    my_pieces = count_pieces(board, color)
    opp_pieces = count_pieces(board, opponent)
    piece_diff = my_pieces - opp_pieces
    
    my_corners = sum(1 for (x,y) in corners if board[x][y] == color)
    opp_corners = sum(1 for (x,y) in corners if board[x][y] == opponent)
    corner_diff = my_corners - opp_corners
    
    my_mobility = len(PossibleMove(color, board))
    opp_mobility = len(PossibleMove(opponent, board))
    mobility_diff = my_mobility - opp_mobility
    
    position_score = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == color:
                position_score += get_position_weight(x, y)
            elif board[x][y] == opponent:
                position_score -= get_position_weight(x, y)
    
    total_pieces = my_pieces + opp_pieces
    if total_pieces < 20:
        score = 100 * corner_diff + 20 * position_score + 10 * mobility_diff
    elif total_pieces < 50:
        score = 100 * corner_diff + 30 * position_score + 20 * mobility_diff + 5 * piece_diff
    else:
        score = 100 * corner_diff + 10 * position_score + 5 * mobility_diff + 20 * piece_diff
    
    return score

def player(Colour, Board):
    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0)
    
    opponent = -Colour
    best_move = None
    best_score = -float('inf')
    
    empty_count = sum(row.count(Empty) for row in Board)
    if empty_count <= 12:
        depth = 3
    else:
        depth = 1
    
    for move in possible_moves:
        x, y = move
        
        if (x, y) in corners:
            return move
        
        if (x, y) in x_squares and empty_count > 12:
            continue
        
        new_board = BoardCopy(Board)
        PlaceMove(Colour, new_board, x, y)
        
        if empty_count <= 12:
            score = minimax(new_board, Colour, depth, -float('inf'), float('inf'), False)
        else:
            score = evaluate_board(new_board, Colour)
        
        score += random.uniform(-0.1, 0.1)
        
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move if best_move else random.choice(possible_moves)

def minimax(board, color, depth, alpha, beta, maximizing_player):
    if depth == 0:
        return evaluate_board(board, color)
    
    opponent = -color
    possible_moves = PossibleMove(color if maximizing_player else opponent, board)
    
    if not possible_moves:
        if PossibleMove(opponent if maximizing_player else color, board):
            return minimax(board, color, depth-1, alpha, beta, not maximizing_player)
        else:
            return evaluate_board(board, color)
    
    if maximizing_player:
        max_eval = -float('inf')
        for move in possible_moves:
            new_board = BoardCopy(board)
            PlaceMove(color, new_board, move[0], move[1])
            eval = minimax(new_board, color, depth-1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in possible_moves:
            new_board = BoardCopy(board)
            PlaceMove(opponent, new_board, move[0], move[1])
            eval = minimax(new_board, color, depth-1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval