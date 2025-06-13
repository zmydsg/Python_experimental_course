from Reversi import *
import random

CORNER_POSITIONS = [(1, 1), (1, 8), (8, 1), (8, 8)]  # 预计算角落位置
EDGE_ROW_INDICES = {1, 8}  # 预计算边行
EDGE_COLUMN_INDICES = {1, 8}  # 预计算边列
RISKY_POSITIONS = {(2, 2), (2, 7), (7, 2), (7, 7),
                   (1, 2), (2, 1), (1, 7), (2, 8),
                   (7, 1), (8, 2), (7, 8), (8, 7),
                   (2, 3), (3, 2), (2, 6), (3, 7),
                   (6, 2), (7, 3), (6, 7), (7, 6)}  # 扩展危险区

# 棋盘位置权重
BOARD_WEIGHTS = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 100, -20, 10, 5, 5, 10, -20, 100, 0],
    [0, -20, -50, -2, -2, -2, -2, -50, -20, 0],
    [0, 10, -2, 3, 2, 2, 3, -2, 10, 0],
    [0, 5, -2, 2, 1, 1, 2, -2, 5, 0],
    [0, 5, -2, 2, 1, 1, 2, -2, 5, 0],
    [0, 10, -2, 3, 2, 2, 3, -2, 10, 0],
    [0, -20, -50, -2, -2, -2, -2, -50, -20, 0],
    [0, 100, -20, 10, 5, 5, 10, -20, 100, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]


def player(Colour, Board):
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)

    # 优先占据角落
    corner_moves = [move for move in moves if move in CORNER_POSITIONS]
    if corner_moves:
        return random.choice(corner_moves)

    # 避免危险区
    safe_moves = [move for move in moves if move not in RISKY_POSITIONS]
    if safe_moves:
        moves = safe_moves

    best_score = -float('inf')
    best_move = None

    for move in moves:
        x, y = move

        # 快速计算基础分值
        score = 0

        # 棋盘位置权重
        score += BOARD_WEIGHTS[x][y]

        # 模拟落子
        temp_board = BoardCopy(Board)
        PlaceMove(Colour, temp_board, x, y)

        # 翻转棋子数
        flipped = sum(row.count(Colour) for row in temp_board) - sum(row.count(Colour) for row in Board)
        score += flipped * 2

        # 行动力（Mobility）：使对手的下一步选择最少
        opponent_moves = PossibleMove(-Colour, temp_board)
        score -= len(opponent_moves) * 3  # 对手可移动点越少越好

        # 对手的潜在角落威胁
        opponent_corner_potential = sum(1 for corner in CORNER_POSITIONS if corner in opponent_moves)
        score -= opponent_corner_potential * 100

        # 评估当前棋盘状态
        my_count = sum(row.count(Colour) for row in temp_board)
        opp_count = sum(row.count(-Colour) for row in temp_board)
        score += (my_count - opp_count) * 0.5

        # 对手潜在威胁评估
        for dx, dy in NeighbourPosition:
            nx, ny = x + dx, y + dy
            if (nx, ny) in CORNER_POSITIONS and Board[nx][ny] == Empty:
                score -= 20  # 危险位置扣分

        if score > best_score:
            best_score = score
            best_move = move

    return best_move if best_move else random.choice(moves)

