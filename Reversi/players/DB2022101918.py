# -*- coding: utf-8 -*-

from Reversi import *
import random

def player(Colour, Board):
    """
    此函数实现了一个改进的黑白棋玩家策略。
    它会依据游戏所处的不同阶段，运用不同的策略来挑选下一步的落子位置。

    参数:
    Colour -- 玩家的棋子颜色，黑棋为 1，白棋为 -1
    Board -- 当前的游戏棋盘状态

    返回:
    下一步落子的坐标，如果没有可行的落子位置，则返回 (0, 0)
    """
    # 获取当前玩家所有可行的落子位置
    valid_moves = PossibleMove(Colour, Board)
    if not valid_moves:
        return (0, 0)

    # 统计当前棋盘上空格的数量，以此判断游戏阶段
    empty_spaces = sum(row.count(Empty) for row in Board[1:9])
    if empty_spaces > 45:
        game_stage = "early"
    elif empty_spaces > 20:
        game_stage = "mid"
    else:
        game_stage = "late"

    # 在游戏后期且空格少于 12 个时，采用深度为 3 的极小极大算法选择落子
    if game_stage == "late" and empty_spaces < 12:
        return minimax_strategy(Colour, Board, 3)

    # 正常情况下，使用加权评估函数来选择最佳落子
    best_move = None
    max_score = float('-inf')

    for move in valid_moves:
        x, y = move
        move_score = evaluate_move(Colour, Board, move, game_stage)

        # 加入随机扰动，避免在得分相同时总是选择相同的落子
        move_score += random.uniform(0, 0.1)

        if move_score > max_score:
            max_score = move_score
            best_move = move

    return best_move

def evaluate_move(player_color, current_board, move, stage):
    """
    对一个潜在的落子位置进行综合评估，考虑多个战略因素。

    参数:
    player_color -- 玩家的棋子颜色
    current_board -- 当前的游戏棋盘状态
    move -- 潜在的落子位置
    stage -- 游戏所处的阶段

    返回:
    该落子位置的综合得分
    """
    x, y = move
    new_board = BoardCopy(current_board)
    PlaceMove(player_color, new_board, x, y)

    # 位置评估得分
    position_value = assess_position(move, stage)

    # 行动力评估得分
    opponent_current_mobility = len(PossibleMove(-player_color, current_board))
    player_next_mobility = len(PossibleMove(player_color, new_board))
    opponent_next_mobility = len(PossibleMove(-player_color, new_board))
    mobility_value = player_next_mobility - opponent_next_mobility

    # 边界棋子评估得分，边界棋子越少越好
    frontier_value = -count_frontier_pieces(player_color, new_board)

    # 棋子数量差异得分，在游戏后期更重要
    player_piece_count = sum(row.count(player_color) for row in new_board[1:9])
    opponent_piece_count = sum(row.count(-player_color) for row in new_board[1:9])
    piece_difference = player_piece_count - opponent_piece_count

    # 棋子稳定性评估得分，稳定的棋子不易被翻转
    stability_value = assess_piece_stability(player_color, new_board)

    # 角位控制评估得分，角位的控制很关键
    corner_value = assess_corner_control(player_color, new_board)

    # 根据游戏阶段调整各因素的权重
    if stage == "early":
        total_score = (
            5 * position_value +
            3 * mobility_value +
            3 * stability_value +
            1 * frontier_value +
            10 * corner_value +
            0.5 * piece_difference
        )
    elif stage == "mid":
        total_score = (
            4 * position_value +
            2 * mobility_value +
            4 * stability_value +
            2 * frontier_value +
            8 * corner_value +
            1 * piece_difference
        )
    else:
        total_score = (
            2 * position_value +
            1 * mobility_value +
            5 * stability_value +
            1 * frontier_value +
            5 * corner_value +
            3 * piece_difference
        )

    return total_score

def assess_position(move, stage):
    """
    评估一个落子位置的价值。

    参数:
    move -- 落子位置
    stage -- 游戏阶段

    返回:
    该位置的得分
    """
    x, y = move

    # 静态位置权重矩阵，可根据实际情况调整
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

    # 在游戏后期，位置的重要性相对降低
    if stage == "late":
        position_weights = [[1 for _ in range(8)] for _ in range(8)]

    return position_weights[y - 1][x - 1]

def assess_corner_control(player_color, board):
    """
    评估玩家对棋盘角位的控制情况。

    参数:
    player_color -- 玩家的棋子颜色
    board -- 当前的游戏棋盘状态

    返回:
    角位控制的得分
    """
    corner_positions = [(1, 1), (1, 8), (8, 1), (8, 8)]
    score = 0

    for x, y in corner_positions:
        if board[x][y] == player_color:
            score += 25  # 玩家占据角位给予高分奖励
        elif board[x][y] == -player_color:
            score -= 25  # 对手占据角位给予低分惩罚

    return score

def assess_piece_stability(player_color, board):
    """
    评估玩家棋子的稳定性。

    参数:
    player_color -- 玩家的棋子颜色
    board -- 当前的游戏棋盘状态

    返回:
    棋子稳定性的得分
    """
    stable_count = 0
    rows, cols = len(board), len(board[0])

    for i in range(1, rows):
        for j in range(1, cols):
            if board[i][j] == player_color:
                if is_stable_piece(player_color, board, i, j):
                    stable_count += 1

    return stable_count

def is_stable_piece(player_color, board, x, y):
    """
    判断一个棋子是否稳定。

    参数:
    player_color -- 玩家的棋子颜色
    board -- 当前的游戏棋盘状态
    x, y -- 棋子的坐标

    返回:
    True 表示棋子稳定，False 表示不稳定
    """
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        while 1 <= nx <= 8 and 1 <= ny <= 8:
            if board[nx][ny] == Empty:
                return False
            elif board[nx][ny] == -player_color:
                break
            nx += dx
            ny += dy

    return True

def count_frontier_pieces(player_color, board):
    """
    统计玩家的边界棋子数量。

    参数:
    player_color -- 玩家的棋子颜色
    board -- 当前的游戏棋盘状态

    返回:
    边界棋子的数量
    """
    frontier_count = 0
    rows, cols = len(board), len(board[0])
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for i in range(1, rows):
        for j in range(1, cols):
            if board[i][j] == player_color:
                for dx, dy in directions:
                    ni, nj = i + dx, j + dy
                    if 1 <= ni <= 8 and 1 <= nj <= 8 and board[ni][nj] == Empty:
                        frontier_count += 1
                        break

    return frontier_count

def minimax_strategy(player_color, board, depth):
    """
    极小极大算法，用于在游戏后期选择最佳落子。

    参数:
    player_color -- 玩家的棋子颜色
    board -- 当前的游戏棋盘状态
    depth -- 搜索的深度

    返回:
    最佳落子的坐标
    """
    best_score = float('-inf')
    best_move = None

    for move in PossibleMove(player_color, board):
        new_board = BoardCopy(board)
        PlaceMove(player_color, new_board, move[0], move[1])
        score = minimax(-player_color, new_board, depth - 1, float('-inf'), float('inf'), False)
        if score > best_score:
            best_score = score
            best_move = move

    return best_move

def minimax(player_color, board, depth, alpha, beta, is_maximizing):
    """
    极小极大算法的递归实现。

    参数:
    player_color -- 当前玩家的棋子颜色
    board -- 当前的游戏棋盘状态
    depth -- 剩余的搜索深度
    alpha -- 极大值剪枝参数
    beta -- 极小值剪枝参数
    is_maximizing -- 是否为极大化层

    返回:
    当前局面的评估得分
    """
    if depth == 0 or not PossibleMove(player_color, board):
        return evaluate_move(player_color, board, (0, 0), "late")

    if is_maximizing:
        max_eval = float('-inf')
        for move in PossibleMove(player_color, board):
            new_board = BoardCopy(board)
            PlaceMove(player_color, new_board, move[0], move[1])
            eval_score = minimax(-player_color, new_board, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in PossibleMove(player_color, board):
            new_board = BoardCopy(board)
            PlaceMove(player_color, new_board, move[0], move[1])
            eval_score = minimax(-player_color, new_board, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

