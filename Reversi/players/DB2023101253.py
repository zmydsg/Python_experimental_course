# Reversi_GUI.py
from Reversi import *
import random

def player(Colour, Board):
    """
    玩家函数，根据当前棋盘状态返回最佳落子位置
    """
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)  # 无合法移动时返回(0,0)

    empty_count = sum(row.count(Empty) for row in Board)

    # 动态策略选择
    if empty_count > 40:  # 开局阶段（剩余空格>40）
        return opening_strategy(Colour, Board, moves)
    elif empty_count > 12:  # 中局阶段（剩余空格13-40）
        return midgame_strategy(Colour, Board, moves)
    else:  # 终局阶段（剩余空格<=12）
        return endgame_strategy(Colour, Board, moves)


def opening_strategy(Colour, Board, moves):
    """开局策略：优先占据角落和边缘安全位置"""
    # 1. 优先占据四个角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner

    # 2. 次优选择边缘安全位置（远离角落但不易被翻转）
    edge_safe = [(1, 3), (1, 6), (3, 1), (6, 1), (3, 8), (6, 8), (8, 3), (8, 6)]
    for spot in edge_safe:
        if spot in moves:
            return spot

    # 3. 动态评估系统（基于位置权重和翻转数量）
    return dynamic_evaluate(Colour, Board, moves,
                            position_weight=2.0,  # 开局更注重位置控制
                            mobility_weight=1.5,  # 行动力评估权重
                            flip_weight=0.8)  # 翻转数量权重


def midgame_strategy(Colour, Board, moves):
    """中局策略：平衡位置控制与行动力"""
    # 1. 优先占据角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner

    # 2. 动态评估系统（调整权重，平衡发展与控制）
    return dynamic_evaluate(Colour, Board, moves,
                            position_weight=1.2,  # 位置权重降低
                            mobility_weight=1.8,  # 行动力权重提高
                            flip_weight=1.5,  # 翻转权重提高
                            risk_penalty=200)  # 风险惩罚（避免给对手角落）


def endgame_strategy(Colour, Board, moves):
    """终局策略：直接计算最终棋子数量差"""
    best_move = None
    max_score = -float('inf')

    for move in moves:
        x, y = move
        # 模拟落子后的棋盘状态
        new_board = BoardCopy(Board)
        new_board = PlaceMove(Colour, new_board, x, y)

        # 计算双方棋子数量差（最大化我方优势）
        my_count = evaluate_board(new_board, Colour)
        opponent_count = evaluate_board(new_board, -Colour)
        score = my_count - opponent_count

        if score > max_score:
            max_score = score
            best_move = move

    return best_move if best_move else (0, 0)


def dynamic_evaluate(Colour, Board, moves, **weights):
    """
    动态评估系统：综合考虑位置权重、翻转数量和行动力
    """
    # 位置评分矩阵（角落最高，边缘次之，内部较低）
    position_matrix = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 500, -50, 30, 15, 15, 30, -50, 500, 0],
        [0, -50, -100, -15, -8, -8, -15, -100, -50, 0],
        [0, 30, -15, 20, 5, 5, 20, -15, 30, 0],
        [0, 15, -8, 5, 3, 3, 5, -8, 15, 0],
        [0, 15, -8, 5, 3, 3, 5, -8, 15, 0],
        [0, 30, -15, 20, 5, 5, 20, -15, 30, 0],
        [0, -50, -100, -15, -8, -8, -15, -100, -50, 0],
        [0, 500, -50, 30, 15, 15, 30, -50, 500, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    best_score = -float('inf')
    best_moves = []

    for x, y in moves:
        score = 0

        # 1. 位置评分（基于预定义矩阵）
        score += position_matrix[x][y] * weights.get('position_weight', 1.0)

        # 2. 翻转数量评分（翻转越多越好）
        flipped = count_flipped(Board, Colour, x, y)
        score += flipped * weights.get('flip_weight', 1.0)

        # 3. 行动力评分（计算下一步双方的可能移动数）
        temp_board = BoardCopy(Board)
        temp_board = PlaceMove(Colour, temp_board, x, y)
        my_moves_count = len(PossibleMove(Colour, temp_board))
        opponent_moves_count = len(PossibleMove(-Colour, temp_board))
        score += (my_moves_count - opponent_moves_count) * weights.get('mobility_weight', 1.0)

        # 4. 风险评估（避免给对手角落）
        risk_penalty = 0
        for corner in [(1, 1), (1, 8), (8, 1), (8, 8)]:
            if corner in PossibleMove(-Colour, temp_board):
                risk_penalty += weights.get('risk_penalty', 150)
        score -= risk_penalty

        # 更新最佳移动
        if score > best_score:
            best_score = score
            best_moves = [(x, y)]
        elif score == best_score:
            best_moves.append((x, y))

    # 随机选择最佳移动（避免总是选择相同位置）
    return random.choice(best_moves) if best_moves else (0, 0)


def count_flipped(Board, Colour, x, y):
    """计算落子(x,y)后翻转的棋子数量"""
    flipped = 0
    for dx, dy in [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]:
        cx, cy = x + dx, y + dy
        temp_flips = 0
        while ValidCell(cx, cy) and Board[cx][cy] == -Colour:
            temp_flips += 1
            cx += dx
            cy += dy
        if ValidCell(cx, cy) and Board[cx][cy] == Colour:
            flipped += temp_flips
    return flipped

def evaluate_board(Board, Colour):
    """评估棋盘状态：计算指定颜色的棋子数量"""
    return sum(1 for x in range(1, 9) for y in range(1, 9) if Board[x][y] == Colour)
