# Module for Python course project V4.0 2025
# Reversi AI with Alpha-Beta pruning and improved evaluation

from Reversi import *

ring1 = {(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
         (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8),
         (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (2, 8), (3, 8),
         (4, 8), (5, 8), (6, 8), (7, 8)}
coner1 = {(1,1), (1,8), (8,1), (8,8)}
ring2 = {(2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (7, 2), (7, 3),
         (7, 4), (7, 5), (7, 6), (7, 7), (3, 2), (4, 2), (5, 2), (6, 2),
         (3, 7), (4, 7), (5, 7), (6, 7)}
coner2 = {(2,2), (2,7), (7,2), (7,7)}
ring3 = {(3, 3), (3, 4), (3, 5), (3, 6), (6, 3), (6, 4), (6, 5), (6, 6),
         (4, 3), (5, 3), (4, 6), (5, 6)}
coner3 = {(3,3), (3,6), (6,3), (6,6)}
weight = {0: coner1, 1: ring1, 2: coner3, 3: ring3, 4: ring2-coner2, 5: coner2}
weight2 = {0: ring1, 1: ring3, 2: ring2}

def player(Colour, Board):
    """高级翻转棋AI策略，整合分阶段策略及Alpha-Beta搜索"""
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)

    empty_count = sum(row.count(Empty) for row in Board)

    if empty_count > 44:
        return opening_strategy(Colour, Board, moves)
    elif empty_count > 12:
        return midgame_strategy(Colour, Board, moves)
    else:
        # 终局阶段提高搜索深度
        return endgame_strategy(Colour, Board, moves, depth=4)


def opening_strategy(Colour, Board, moves):
    position_weights = [
        [120, -20, 20, 5, 5, 20, -20, 120],
        [-20, -40, -5, -5, -5, -5, -40, -20],
        [20, -5, 15, 3, 3, 15, -5, 20],
        [5, -5, 3, 3, 3, 3, -5, 5],
        [5, -5, 3, 3, 3, 3, -5, 5],
        [20, -5, 15, 3, 3, 15, -5, 20],
        [-20, -40, -5, -5, -5, -5, -40, -20],
        [120, -20, 20, 5, 5, 20, -20, 120]
    ]

    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for move in moves:
        if move in corners:
            return move

    best_move = moves[0]
    best_score = -float('inf')
    for (x, y) in moves:
        score = position_weights[x - 1][y - 1]
        if not gives_opponent_corner(Colour, Board, (x, y)):
            score += 20
        if score > best_score:
            best_score = score
            best_move = (x, y)
    return best_move


def midgame_strategy(Colour, Board, moves):
    opponent = -Colour
    best_move = moves[0]
    best_score = -float('inf')

    for (x, y) in moves:
        new_board = PlaceMove(Colour, BoardCopy(Board), x, y)
        position_score = evaluate_position(Colour, new_board)
        my_mobility = len(PossibleMove(Colour, new_board))
        opponent_mobility = len(PossibleMove(opponent, new_board))
        score = position_score + 20 * (my_mobility - opponent_mobility)
        if gives_opponent_corner(Colour, Board, (x, y)):
            score -= 100
        if score > best_score:
            best_score = score
            best_move = (x, y)

    return best_move


def endgame_strategy(Colour, Board, moves, depth):
    opponent = -Colour
    best_move = moves[0]
    best_score = -float('inf')
    alpha = -float('inf')
    beta = float('inf')

    for (x, y) in moves:
        new_board = PlaceMove(Colour, BoardCopy(Board), x, y)
        score = alphabeta(opponent, new_board, depth - 1, alpha, beta, False, Colour)
        if score > best_score:
            best_score = score
            best_move = (x, y)
        alpha = max(alpha, best_score)

    return best_move


def alphabeta(player, board, depth, alpha, beta, is_maximizing, Colour):
    moves = PossibleMove(player, board)
    opponent = -player

    if depth == 0 or not moves:
        return evaluate_position(Colour, board)

    if is_maximizing:
        value = -float('inf')
        for (x, y) in moves:
            new_board = PlaceMove(player, BoardCopy(board), x, y)
            value = max(value, alphabeta(opponent, new_board, depth - 1, alpha, beta, False, Colour))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = float('inf')
        for (x, y) in moves:
            new_board = PlaceMove(player, BoardCopy(board), x, y)
            value = min(value, alphabeta(opponent, new_board, depth - 1, alpha, beta, True, Colour))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value


def evaluate_position(Colour, board):
    opponent = -Colour
    my_score = 0
    opp_score = 0

    # 棋子数
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == Colour:
                my_score += 1
            elif board[x][y] == opponent:
                opp_score += 1

    position_weights = [
        [120, -20, 20, 5, 5, 20, -20, 120],
        [-20, -40, -5, -5, -5, -5, -40, -20],
        [20, -5, 15, 3, 3, 15, -5, 20],
        [5, -5, 3, 3, 3, 3, -5, 5],
        [5, -5, 3, 3, 3, 3, -5, 5],
        [20, -5, 15, 3, 3, 15, -5, 20],
        [-20, -40, -5, -5, -5, -5, -40, -20],
        [120, -20, 20, 5, 5, 20, -20, 120]
    ]

    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == Colour:
                my_score += position_weights[x - 1][y - 1] * 0.1
            elif board[x][y] == opponent:
                opp_score += position_weights[x - 1][y - 1] * 0.1

    my_mobility = len(PossibleMove(Colour, board))
    opp_mobility = len(PossibleMove(opponent, board))
    my_score += my_mobility * 5
    opp_score += opp_mobility * 5

    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for (x, y) in corners:
        if board[x][y] == Colour:
            my_score += 40
        elif board[x][y] == opponent:
            opp_score += 40

    my_stable = count_stable_discs(Colour, board)
    opp_stable = count_stable_discs(opponent, board)
    my_score += my_stable * 15
    opp_score += opp_stable * 15

    return my_score - opp_score


def count_stable_discs(Colour, board):
    stable = 0
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]

    for corner in corners:
        cx, cy = corner
        if board[cx][cy] == Colour:
            stable += 1
            # 横向边缘连续稳定子
            for y in range(cy + 1, 9):
                if board[cx][y] == Colour:
                    stable += 1
                else:
                    break
            # 纵向边缘连续稳定子
            for x in range(cx + 1, 9):
                if board[x][cy] == Colour:
                    stable += 1
                else:
                    break
    return stable


def gives_opponent_corner(Colour, Board, move):
    opponent = -Colour
    (x, y) = move
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    adjacent_corners = {
        (1, 1): [(1, 2), (2, 1), (2, 2)],
        (1, 8): [(1, 7), (2, 8), (2, 7)],
        (8, 1): [(7, 1), (8, 2), (7, 2)],
        (8, 8): [(7, 8), (8, 7), (7, 7)]
    }

    for corner in corners:
        if Board[corner[0]][corner[1]] != Empty:
            continue
        for adj in adjacent_corners[corner]:
            if (x, y) == adj:
                temp_board = BoardCopy(Board)
                temp_board[x][y] = Colour
                if corner in PossibleMove(opponent, temp_board):
                    return True
    return False
