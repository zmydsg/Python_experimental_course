from Reversi import *


def player(Colour, Board):
    # 棋盘位置权重矩阵，角落和边缘位置具有更高的价值
    weight_matrix = [
        [100, -20, 10, 5, 5, 10, -20, 100],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [10, -2, 3, 2, 2, 3, -2, 10],
        [5, -2, 2, 1, 1, 2, -2, 5],
        [5, -2, 2, 1, 1, 2, -2, 5],
        [10, -2, 3, 2, 2, 3, -2, 10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [100, -20, 10, 5, 5, 10, -20, 100],
    ]

    # 获取所有合法移动
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)

    # 计算当前玩家的棋子数目
    original_count = sum(Board[x][y] == Colour for x in range(1, 9) for y in range(1, 9))

    max_score = -float('inf')
    best_moves = []

    for (x, y) in moves:
        # 复制棋盘进行模拟
        temp_board = BoardCopy(Board)
        PlaceMove(Colour, temp_board, x, y)

        # 计算翻转后的棋子数目
        new_count = sum(temp_board[x1][y1] == Colour for x1 in range(1, 9) for y1 in range(1, 9))
        flips = new_count - original_count - 1  # 计算翻转数量

        # 获取位置权重
        pos_score = weight_matrix[x - 1][y - 1] if 0 <= x - 1 < 8 and 0 <= y - 1 < 8 else 0

        # 综合评分（位置权重 + 翻转数*5）
        total_score = pos_score + flips * 5

        # 更新最佳移动
        if total_score > max_score:
            max_score = total_score
            best_moves = [(x, y)]
        elif total_score == max_score:
            best_moves.append((x, y))

    # 随机选择得分最高的移动
    return random.choice(best_moves)
