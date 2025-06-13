# from Reversi import *
#
# # 棋盘位置权重（8x8实际区域）
# WEIGHTS = [
#     [100, -20, 10,  5,  5, 10, -20, 100],
#     [-20, -50, -2, -2, -2, -2, -50, -20],
#     [10,  -2,  -1, -1, -1, -1,  -2,  10],
#     [5,   -2,  -1, -1, -1, -1,  -2,   5],
#     [5,   -2,  -1, -1, -1, -1,  -2,   5],
#     [10,  -2,  -1, -1, -1, -1,  -2,  10],
#     [-20, -50, -2, -2, -2, -2, -50, -20],
#     [100, -20, 10,  5,  5, 10, -20, 100]
# ]
#
# # 置换表缓存结构：{board_hash: (depth, score, flag)}
# # flag表示exact, lowerbound, upperbound
# transposition_table = {}
#
# def board_to_hash(Board):
#     # 将棋盘转换为字符串做哈希（简单实现）
#     return ''.join(''.join(str(cell) for cell in row[1:9]) for row in Board[1:9])
#
# def mobility(Player, Board):
#     return len(PossibleMove(Player, Board)) - len(PossibleMove(-Player, Board))
#
# def stable_corners(Player, Board):
#     score = 0
#     for x, y in [(1,1), (1,8), (8,1), (8,8)]:
#         if Board[x][y] == Player:
#             score += 1
#         elif Board[x][y] == -Player:
#             score -= 1
#     return score * 25
#
# def evaluate_board(Player, Board):
#     total_discs = sum(row.count(Black) + row.count(White) for row in Board)
#     if total_discs <= 20:
#         w_mobility = 10; w_pos = 5; w_corner = 25; w_disc_diff = 0
#     elif total_discs <= 58:
#         w_mobility = 5; w_pos = 10; w_corner = 30; w_disc_diff = 5
#     else:
#         w_mobility = 2; w_pos = 2; w_corner = 40; w_disc_diff = 20
#
#     pos_weight = 0
#     for x in range(1, 9):
#         for y in range(1, 9):
#             if Board[x][y] == Player:
#                 pos_weight += WEIGHTS[y - 1][x - 1]
#             elif Board[x][y] == -Player:
#                 pos_weight -= WEIGHTS[y - 1][x - 1]
#
#     mob_score = mobility(Player, Board)
#     corner_score = stable_corners(Player, Board)
#
#     player_discs = sum(row.count(Player) for row in Board)
#     opponent_discs = sum(row.count(-Player) for row in Board)
#     disc_diff = player_discs - opponent_discs
#
#     score = w_pos * pos_weight + w_mobility * mob_score + w_corner * corner_score + w_disc_diff * disc_diff
#     return score
#
# def move_priority(move, Player, Board):
#     x, y = move
#     corners = {(1,1), (1,8), (8,1), (8,8)}
#     edges = {1, 8}
#     priority = 0
#     if (x, y) in corners:
#         priority += 100
#     elif x in edges or y in edges:
#         priority += 10
#
#     new_board = BoardCopy(Board)
#     PlaceMove(Player, new_board, x, y)
#     priority += len(PossibleMove(Player, new_board))
#     return priority
#
# def alphabeta(Board, Player, depth, alpha, beta, maximizing):
#     alpha_orig, beta_orig = alpha, beta
#     board_hash = board_to_hash(Board)
#
#     if board_hash in transposition_table:
#         entry_depth, entry_score, flag = transposition_table[board_hash]
#         if entry_depth >= depth:
#             if flag == 'exact':
#                 return entry_score, None
#             elif flag == 'lowerbound':
#                 alpha = max(alpha, entry_score)
#             elif flag == 'upperbound':
#                 beta = min(beta, entry_score)
#             if alpha >= beta:
#                 return entry_score, None
#     possible_moves = PossibleMove(Player, Board)
#     if depth == 0 or (not possible_moves and not PossibleMove(-Player, Board)):
#         return evaluate_board(Player, Board), None
#     if not possible_moves:
#         # 跳过回合
#         eval, _ = alphabeta(Board, -Player, depth, alpha, beta, not maximizing)
#         return eval, None
#     possible_moves.sort(key=lambda m: move_priority(m, Player, Board), reverse=True)
#     best_move = None
#     if maximizing:
#         max_eval = float('-inf')
#         for move in possible_moves:
#             new_board = BoardCopy(Board)
#             PlaceMove(Player, new_board, *move)
#             eval, _ = alphabeta(new_board, -Player, depth - 1, alpha, beta, False)
#             if eval > max_eval:
#                 max_eval = eval
#                 best_move = move
#             alpha = max(alpha, eval)
#             if beta <= alpha:
#                 break
#         if max_eval <= alpha_orig:
#             flag = 'upperbound'
#         elif max_eval >= beta:
#             flag = 'lowerbound'
#         else:
#             flag = 'exact'
#         transposition_table[board_hash] = (depth, max_eval, flag)
#         return max_eval, best_move
#     else:
#         min_eval = float('inf')
#         for move in possible_moves:
#             new_board = BoardCopy(Board)
#             PlaceMove(Player, new_board, *move)
#             eval, _ = alphabeta(new_board, -Player, depth - 1, alpha, beta, True)
#             if eval < min_eval:
#                 min_eval = eval
#                 best_move = move
#             beta = min(beta, eval)
#             if beta <= alpha:
#                 break
#         if min_eval <= alpha:
#             flag = 'upperbound'
#         elif min_eval >= beta_orig:
#             flag = 'lowerbound'
#         else:
#             flag = 'exact'
#         transposition_table[board_hash] = (depth, min_eval, flag)
#
#         return min_eval, best_move
#
#
# def iterative_deepening(Board, Player, max_depth=5, time_limit=1.4):
#     import time
#     start_time = time.time()
#     best_move = None
#
#     for depth in range(1, max_depth + 1):
#         # 检查是否超时
#         if time.time() - start_time > time_limit:
#             break
#
#         transposition_table.clear()  # 每次迭代清空缓存，防止旧缓存干扰
#         score, move = alphabeta(Board, Player, depth, float('-inf'), float('inf'), True)
#
#         if time.time() - start_time > time_limit:
#             break
#
#         if move is not None:
#             best_move = move
#
#     return best_move
#
# def player(Colour, Board):
#     move = iterative_deepening(Board, Colour, max_depth=5, time_limit=1.0)
#     return move if move else (0, 0)
from Reversi import *

# 棋盘位置权重（8x8实际区域）
WEIGHTS = [
    [100, -20, 10,  5,  5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [10,  -2,  -1, -1, -1, -1,  -2,  10],
    [5,   -2,  -1, -1, -1, -1,  -2,   5],
    [5,   -2,  -1, -1, -1, -1,  -2,   5],
    [10,  -2,  -1, -1, -1, -1,  -2,  10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10,  5,  5, 10, -20, 100]
]

# 置换表缓存结构：{board_hash: (depth, score, flag)}
# flag表示exact, lowerbound, upperbound
transposition_table = {}

def board_to_hash(Board):
    # 将棋盘转换为字符串做哈希（简单实现）
    return ''.join(''.join(str(cell) for cell in row[1:9]) for row in Board[1:9])

def mobility(Player, Board):
    return len(PossibleMove(Player, Board)) - len(PossibleMove(-Player, Board))

def stable_corners(Player, Board):
    score = 0
    for x, y in [(1,1), (1,8), (8,1), (8,8)]:
        if Board[x][y] == Player:
            score += 1
        elif Board[x][y] == -Player:
            score -= 1
    return score * 25

def evaluate_board(Player, Board):
    total_discs = sum(row.count(Black) + row.count(White) for row in Board)
    if total_discs <= 20:
        w_mobility = 10; w_pos = 5; w_corner = 25; w_disc_diff = 0
    elif total_discs <= 58:
        w_mobility = 5; w_pos = 10; w_corner = 30; w_disc_diff = 5
    else:
        w_mobility = 2; w_pos = 2; w_corner = 40; w_disc_diff = 20

    pos_weight = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Player:
                pos_weight += WEIGHTS[y - 1][x - 1]
            elif Board[x][y] == -Player:
                pos_weight -= WEIGHTS[y - 1][x - 1]

    mob_score = mobility(Player, Board)
    corner_score = stable_corners(Player, Board)

    player_discs = sum(row.count(Player) for row in Board)
    opponent_discs = sum(row.count(-Player) for row in Board)
    disc_diff = player_discs - opponent_discs

    score = w_pos * pos_weight + w_mobility * mob_score + w_corner * corner_score + w_disc_diff * disc_diff
    return score

def move_priority(move, Player, Board):
    x, y = move
    corners = {(1,1), (1,8), (8,1), (8,8)}
    edges = {1, 8}
    priority = 0
    if (x, y) in corners:
        priority += 100
    elif x in edges or y in edges:
        priority += 10

    new_board = BoardCopy(Board)
    PlaceMove(Player, new_board, x, y)
    priority += len(PossibleMove(Player, new_board))
    return priority

import time

def alphabeta(Board, Player, depth, alpha, beta, maximizing, start_time, time_limit):
    if time.time() - start_time >= time_limit:
        return evaluate_board(Player, Board), None

    alpha_orig, beta_orig = alpha, beta
    board_hash = board_to_hash(Board)

    if board_hash in transposition_table:
        entry_depth, entry_score, flag = transposition_table[board_hash]
        if entry_depth >= depth:
            if flag == 'exact':
                return entry_score, None
            elif flag == 'lowerbound':
                alpha = max(alpha, entry_score)
            elif flag == 'upperbound':
                beta = min(beta, entry_score)
            if alpha >= beta:
                return entry_score, None

    possible_moves = PossibleMove(Player, Board)
    if depth == 0 or (not possible_moves and not PossibleMove(-Player, Board)):
        return evaluate_board(Player, Board), None
    if not possible_moves:
        eval, _ = alphabeta(Board, -Player, depth, alpha, beta, not maximizing, start_time, time_limit)
        return eval, None

    possible_moves.sort(key=lambda m: move_priority(m, Player, Board), reverse=True)
    best_move = None

    if maximizing:
        max_eval = float('-inf')
        for move in possible_moves:
            if time.time() - start_time >= time_limit:
                break
            new_board = BoardCopy(Board)
            PlaceMove(Player, new_board, *move)
            eval, _ = alphabeta(new_board, -Player, depth - 1, alpha, beta, False, start_time, time_limit)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        flag = (
            'upperbound' if max_eval <= alpha_orig else
            'lowerbound' if max_eval >= beta else
            'exact'
        )
        transposition_table[board_hash] = (depth, max_eval, flag)
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in possible_moves:
            if time.time() - start_time >= time_limit:
                break
            new_board = BoardCopy(Board)
            PlaceMove(Player, new_board, *move)
            eval, _ = alphabeta(new_board, -Player, depth - 1, alpha, beta, True, start_time, time_limit)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        flag = (
            'upperbound' if min_eval <= alpha else
            'lowerbound' if min_eval >= beta_orig else
            'exact'
        )
        transposition_table[board_hash] = (depth, min_eval, flag)
        return min_eval, best_move


def iterative_deepening(Board, Player, max_depth=5, time_limit=1.4):
    start_time = time.time()
    best_move = None

    for depth in range(1, max_depth + 1):
        if time.time() - start_time >= time_limit:
            break
        transposition_table.clear()  # 每次迭代清空缓存，防止旧缓存干扰
        score, move = alphabeta(Board, Player, depth, float('-inf'), float('inf'),
                                True, start_time, time_limit)
        if time.time() - start_time >= time_limit:
            break
        if move is not None:
            best_move = move

    return best_move

def player(Colour, Board):
    move = iterative_deepening(Board, Colour, max_depth=4, time_limit=1)
    return move if move else (0, 0)
