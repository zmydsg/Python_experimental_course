from Reversi import *

def player(Colour, Board):
    """
    An enhanced Reversi player using Minimax with Alpha-Beta Pruning and advanced heuristic.
    Improvements:
    - Added stability evaluation (stable discs cannot be flipped).
    - Corner priority, edge management, and better mobility balancing.
    """

    BOARD_WEIGHTS = [
        [100, -40, 10, 5, 5, 10, -40, 100],
        [-40, -80, 1, 1, 1, 1, -80, -40],
        [10, 1, 5, 2, 2, 5, 1, 10],
        [5, 1, 2, 1, 1, 2, 1, 5],
        [5, 1, 2, 1, 1, 2, 1, 5],
        [10, 1, 5, 2, 2, 5, 1, 10],
        [-40, -80, 1, 1, 1, 1, -80, -40],
        [100, -40, 10, 5, 5, 10, -40, 100]
    ]

    CORNERS = {(1, 1), (1, 8), (8, 1), (8, 8)}

    def eval_board(board, ai_color):
        opponent_color = -ai_color
        score = 0
        my_count = 0
        opp_count = 0
        my_mob = len(PossibleMove(ai_color, board))
        opp_mob = len(PossibleMove(opponent_color, board))
        stability_bonus = 0

        for r in range(1, 9):
            for c in range(1, 9):
                if board[r][c] == ai_color:
                    score += BOARD_WEIGHTS[r-1][c-1]
                    my_count += 1
                    if (r, c) in CORNERS:
                        stability_bonus += 30
                elif board[r][c] == opponent_color:
                    score -= BOARD_WEIGHTS[r-1][c-1]
                    opp_count += 1
                    if (r, c) in CORNERS:
                        stability_bonus -= 30

        # Piece difference
        piece_diff = my_count - opp_count

        # Stage of the game
        empty = sum(board[r][c] == Empty for r in range(1, 9) for c in range(1, 9))
        if empty > 30:
            score += 10 * (my_mob - opp_mob)
            score += 1 * piece_diff
        elif empty > 10:
            score += 5 * (my_mob - opp_mob)
            score += 5 * piece_diff
        else:
            score += 2 * (my_mob - opp_mob)
            score += 20 * piece_diff

        score += stability_bonus
        return score

    def is_game_over(board):
        return not PossibleMove(Black, board) and not PossibleMove(White, board)

    def minimax(board, depth, maximizing, ai_color, alpha, beta):
        turn = ai_color if maximizing else -ai_color
        if depth == 0 or is_game_over(board):
            return eval_board(board, ai_color)

        moves = PossibleMove(turn, board)
        if not moves:
            if not PossibleMove(-turn, board):
                return eval_board(board, ai_color)
            return minimax(board, depth-1, not maximizing, ai_color, alpha, beta)

        if maximizing:
            max_eval = -float('inf')
            for move in moves:
                new_board = PlaceMove(turn, board, move[0], move[1])
                eval_value = minimax(new_board, depth-1, False, ai_color, alpha, beta)
                max_eval = max(max_eval, eval_value)
                alpha = max(alpha, eval_value)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                new_board = PlaceMove(turn, board, move[0], move[1])
                eval_value = minimax(new_board, depth-1, True, ai_color, alpha, beta)
                min_eval = min(min_eval, eval_value)
                beta = min(beta, eval_value)
                if beta <= alpha:
                    break
            return min_eval

    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0)

    best_score = -float('inf')
    best_move = None
    SEARCH_DEPTH = 2

    for move in possible_moves:
        # Shortcut: If corner available, take it
        if move in CORNERS:
            return move

        new_board = PlaceMove(Colour, Board, move[0], move[1])
        score = minimax(new_board, SEARCH_DEPTH - 1, False, Colour, -float('inf'), float('inf'))
        if score > best_score:
            best_score = score
            best_move = move

    return best_move
