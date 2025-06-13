# Module for Python course project V3.0 2025
# This module is an example of player function to be submitted

from Reversi import *
import tkinter as tk

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

# consider rings, coners and neighbour player's cells
# Place the chess-pieces at the outer corners/rings as much as possible
def player(Colour, Board):
    """使用Alpha-Beta剪枝搜索最佳落子点"""
    max_depth = 4  # 控制最大深度，降低总耗时
    best_move = None
    alpha = float('-inf')
    beta = float('inf')

    val, move = alpha_beta(Colour, Board, max_depth, alpha, beta, True)
    return move if move else (0, 0)

def alpha_beta(player, board, depth, alpha, beta, maximizing_player):
    if depth == 0 or not PossibleMove(player, board):
        return evaluate_board(board, player), None

    possible_moves = PossibleMove(player, board)
    if not possible_moves:
        return evaluate_board(board, player), None

    # 移动排序：提升剪枝效率
    possible_moves.sort(key=lambda move: move_heuristic(player, board, move), reverse=maximizing_player)

    best_move = None
    original_board = [row[:] for row in board]  # 备份当前棋盘状态用于回溯

    if maximizing_player:
        max_eval = float('-inf')
        for move in possible_moves:
            r, c = move
            flipped = PlaceMoveInPlace(player, board, r, c)  # 原地修改棋盘
            eval_, _ = alpha_beta(opposite_color(player), board, depth-1, alpha, beta, False)
            restore_board(board, original_board, flipped)  # 恢复棋盘

            if eval_ > max_eval:
                max_eval = eval_
                best_move = move
            alpha = max(alpha, eval_)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in possible_moves:
            r, c = move
            flipped = PlaceMoveInPlace(player, board, r, c)
            eval_, _ = alpha_beta(opposite_color(player), board, depth-1, alpha, beta, True)
            restore_board(board, original_board, flipped)

            if eval_ < min_eval:
                min_eval = eval_
                best_move = move
            beta = min(beta, eval_)
            if beta <= alpha:
                break
        return min_eval, best_move


def move_heuristic(player, board, move):
    """评估移动的启发式值，用于排序"""
    r, c = move
    opponent = opposite_color(player)

    # 角落优先
    if (r, c) in [(1,1), (1,8), (8,1), (8,8)]:
        return 1000

    # 边缘次之
    if r == 1 or r == 8 or c == 1 or c == 8:
        return 100

    # X位惩罚
    if (r, c) in [(2,2), (2,7), (7,2), (7,7)]:
        return -500

    # C位惩罚
    if (r, c) in [(1,2), (1,7), (2,1), (2,8), (7,1), (7,8), (8,2), (8,7)]:
        return -100

    # 翻转数量
    return count_flips(player, board, r, c)


def count_flips(player, board, r, c):
    """估算该位置可翻转的棋子数"""
    opponent = opposite_color(player)
    flipped = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            count = 0
            while 1 <= nr <= 8 and 1 <= nc <= 8 and board[nr][nc] == opponent:
                count += 1
                nr += dr
                nc += dc
            if 1 <= nr <= 8 and 1 <= nc <= 8 and board[nr][nc] == player:
                flipped += count
    return flipped


def evaluate_board(board, player):
    """简化版评估函数"""
    opponent = opposite_color(player)

    my_tiles = sum(row.count(player) for row in board[1:9])
    opp_tiles = sum(row.count(opponent) for row in board[1:9])

    corners = [(1,1), (1,8), (8,1), (8,8)]
    my_corners = sum(1 for r, c in corners if board[r][c] == player)
    opp_corners = sum(1 for r, c in corners if board[r][c] == opponent)

    my_mobility = len(PossibleMove(player, board))
    opp_mobility = len(PossibleMove(opponent, board))

    score = 0
    score += 10 * (my_tiles - opp_tiles)
    score += 500 * (my_corners - opp_corners)
    score += 20 * (my_mobility - opp_mobility)

    return score


def PlaceMoveInPlace(player, board, r, c):
    """原地落子，并返回被翻转的位置列表"""
    opponent = opposite_color(player)
    flipped = []

    board[r][c] = player  # 先放自己的棋子

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            temp_flipped = []
            nr, nc = r + dr, c + dc
            while 1 <= nr <= 8 and 1 <= nc <= 8 and board[nr][nc] == opponent:
                temp_flipped.append((nr, nc))
                nr += dr
                nc += dc
            if 1 <= nr <= 8 and 1 <= nc <= 8 and board[nr][nc] == player:
                for x, y in temp_flipped:
                    board[x][y] = player
                flipped.extend(temp_flipped)

    return [(r, c)] + flipped


def restore_board(board, original_board, changed_positions):
    """恢复指定位置的原始值"""
    for r, c in changed_positions:
        board[r][c] = original_board[r][c]


def opposite_color(color):
    return Black if color == White else White