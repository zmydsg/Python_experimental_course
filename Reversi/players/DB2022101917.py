from Reversi import *

# 自定义权重矩阵，用于评估棋盘上每个位置的战略价值
weight_matrix = [
    [20, -3, 11, 8, 8, 11, -3, 20],
    [-3, -7, -4, -1, -1, -4, -7, -3],
    [11, -4, 2, 2, 2, 2, -4, 11],
    [8, -1, 2, 1, 1, 2, -1, 8],
    [8, -1, 2, 1, 1, 2, -1, 8],
    [11, -4, 2, 2, 2, 2, -4, 11],
    [-3, -7, -4, -1, -1, -4, -7, -3],
    [20, -3, 11, 8, 8, 11, -3, 20]
]

# 定义角落和危险区域
corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
danger_zones = [(1, 2), (2, 1), (2, 2),
                (1, 7), (2, 7), (2, 8),
                (7, 1), (7, 2), (8, 2),
                (7, 7), (7, 8), (8, 7)]
edges = [(1, y) for y in range(2, 8)] + [(8, y) for y in range(2, 8)] + \
        [(x, 1) for x in range(2, 8)] + [(x, 8) for x in range(2, 8)]

def player(Colour, Board):
    possible_moves = PossibleMove(Colour, Board)

    if not possible_moves:
        return (0, 0)

    # 根据游戏阶段选择不同策略
    empty_count = sum(row.count(Empty) for row in Board)

    if empty_count > 40:  # 开局阶段
        # 优先选择角落
        for corner in corners:
            if corner in possible_moves:
                return corner
        # 避免危险区域
        safe_moves = [move for move in possible_moves if move not in danger_zones]
        if safe_moves:
            # 计算权重
            weighted_moves = []
            for (x, y) in safe_moves:
                weight_x = x - 1
                weight_y = y - 1
                weight = weight_matrix[weight_x][weight_y]
                weighted_moves.append((weight, (x, y)))
            _, best_move = max(weighted_moves, key=lambda move: move[0])
            return best_move
        else:
            # 计算权重
            weighted_moves = []
            for (x, y) in possible_moves:
                weight_x = x - 1
                weight_y = y - 1
                weight = weight_matrix[weight_x][weight_y]
                weighted_moves.append((weight, (x, y)))
            _, best_move = max(weighted_moves, key=lambda move: move[0])
            return best_move

    elif empty_count > 12:  # 中局阶段
        # 优先选择角落
        for corner in corners:
            if corner in possible_moves:
                return corner
        # 考虑边和权重
        edge_moves = [move for move in possible_moves if move in edges]
        if edge_moves:
            weighted_moves = []
            for (x, y) in edge_moves:
                weight_x = x - 1
                weight_y = y - 1
                weight = weight_matrix[weight_x][weight_y]
                weighted_moves.append((weight, (x, y)))
            _, best_move = max(weighted_moves, key=lambda move: move[0])
            return best_move
        else:
            weighted_moves = []
            for (x, y) in possible_moves:
                weight_x = x - 1
                weight_y = y - 1
                weight = weight_matrix[weight_x][weight_y]
                weighted_moves.append((weight, (x, y)))
            _, best_move = max(weighted_moves, key=lambda move: move[0])
            return best_move

    else:  # 终局阶段
        # 优先选择角落
        for corner in corners:
            if corner in possible_moves:
                return corner
        # 计算每步棋后的棋子数量
        best_move = max(possible_moves, key=lambda move: evaluate_move(Colour, Board, move))
        return best_move

def evaluate_move(Colour, Board, move):
    temp_board = PlaceMove(Colour, BoardCopy(Board), move[0], move[1])
    my_count = 0
    opp_count = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if temp_board[x][y] == Colour:
                my_count += 1
            elif temp_board[x][y] == -Colour:
                opp_count += 1
    return my_count - opp_count