
import math
from Reversi import *
import time

Black, White, Empty = [1, -1, 0]


def player(Colour, Board, max_depth=80, time_limit=1.4):

    start_time = time.time()
    deadline = start_time + time_limit

    transposition_table = {}

    def board_hash(board, player, depth, maximizing):
        return ''.join(str(board[x][y]) for x in range(1, 9) for y in range(1, 9)) + f'_{player}_{depth}_{maximizing}'

    def evaluate(board, target_player):
        opponent = -target_player
        my_tiles = opp_tiles = 0
        my_mobility = len(PossibleMove(target_player, board))
        opp_mobility = len(PossibleMove(opponent, board))
        weights = [
            [100, -10, 10, 5, 5, 10, -10, 100],
            [-10, -20, -5, -5, -5, -5, -20, -10],
            [10, -5, 1, 1, 1, 1, -5, 10],
            [5, -5, 1, 0, 0, 1, -5, 5],
            [5, -5, 1, 0, 0, 1, -5, 5],
            [10, -5, 1, 1, 1, 1, -5, 10],
            [-10, -20, -5, -5, -5, -5, -20, -10],
            [100, -10, 10, 5, 5, 10, -10, 100]
        ]
        score = 0
        for x in range(1, 9):
            for y in range(1, 9):
                if board[x][y] == target_player:
                    score += weights[x - 1][y - 1]
                    my_tiles += 1
                elif board[x][y] == opponent:
                    score -= weights[x - 1][y - 1]
                    opp_tiles += 1
        score += 10 * (my_mobility - opp_mobility)
        score += 100 * (my_tiles - opp_tiles)
        return score

    def apply_move(board, player, x, y):
        flipped_discs = []
        opponent = -player
        board[x][y] = player
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1), (1, 0),  (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            flip = []
            while 1 <= nx <= 8 and 1 <= ny <= 8 and board[nx][ny] == opponent:
                flip.append((nx, ny))
                nx += dx
                ny += dy
            if 1 <= nx <= 8 and 1 <= ny <= 8 and board[nx][ny] == player:
                for fx, fy in flip:
                    board[fx][fy] = player
                flipped_discs.extend(flip)
        return flipped_discs

    def undo_move(board, player, x, y, flipped_discs):
        board[x][y] = Empty
        opponent = -player
        for fx, fy in flipped_discs:
            board[fx][fy] = opponent

    def sort_moves(moves, board, player):
        corner = {(1, 1), (1, 8), (8, 1), (8, 8)}
        def move_score(move):
            x, y = move
            score = 0
            if (x, y) in corner:
                score += 1000
            # Calculate approx disc flips
            directions = [(-1, -1), (-1, 0), (-1, 1),
                          (0, -1),          (0, 1),
                          (1, -1), (1, 0),  (1, 1)]
            opponent = -player
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                while 1 <= nx <= 8 and 1 <= ny <= 8 and board[nx][ny] == opponent:
                    score += 1
                    nx += dx
                    ny += dy
            return score
        return sorted(moves, key=move_score, reverse=True)

    def minimax(board, depth, alpha, beta, maximizing, player):
        if time.time() > deadline:
            raise TimeoutError
        
        key = board_hash(board, player, depth, maximizing)
        if key in transposition_table:
            return transposition_table[key]

        moves = PossibleMove(player, board)
        if depth == 0 or not moves:
            score = evaluate(board, Colour)
            transposition_table[key] = score
            return score

        best_value = -math.inf if maximizing else math.inf
        opponent = -player

        for x, y in sort_moves(moves, board, player):
            flipped = apply_move(board, player, x, y)
            try:
                value = minimax(board, depth - 1, alpha, beta, not maximizing, opponent)
            except TimeoutError:
                undo_move(board, player, x, y, flipped)
                raise
            undo_move(board, player, x, y, flipped)

            if maximizing:
                best_value = max(best_value, value)
                alpha = max(alpha, value)
            else:
                best_value = min(best_value, value)
                beta = min(beta, value)
            if beta <= alpha:
                break

        transposition_table[key] = best_value
        return best_value


    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0)


    for move in [(1, 1), (1, 8), (8, 1), (8, 8)]:
        if move in possible_moves:
            return move

    best_move = possible_moves[0]
    best_score = -math.inf

    try:
        for depth in range(2, max_depth + 1):
            current_best = best_move
            current_score = -math.inf
            for x, y in sort_moves(possible_moves, Board, Colour):
                flipped = apply_move(Board, Colour, x, y)
                try:
                    score = minimax(Board, depth - 1, -math.inf, math.inf, False, -Colour)
                except TimeoutError:
                    undo_move(Board, Colour, x, y, flipped)
                    raise
                undo_move(Board, Colour, x, y, flipped)
                if score > current_score:
                    current_score = score
                    current_best = (x, y)
            best_move = current_best
            best_score = current_score
    except TimeoutError:
        pass


    if best_move not in possible_moves:
        return possible_moves[0]
    return best_move