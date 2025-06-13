from Reversi import *
import random
import time


def count_total_flips(player_color, board, x, y):
    """
    计算在给定位置落子会翻转多少对手棋子
    参数:
        player_color (int): 当前玩家颜色 (1=黑棋, -1=白棋)
        board (2D list): 当前棋盘状态
        x (int): 行坐标
        y (int): 列坐标
    返回:
        int: 总翻转棋子数
    """
    total_flips = 0
    # 遍历所有八个方向
    for direction in NeighbourDirection1:
        dx, dy = NeighbourDirection[direction]
        temp_x, temp_y = x + dx, y + dy
        direction_flips = 0

        # 沿当前方向检查连续对手棋子
        while ValidCell(temp_x, temp_y) and board[temp_x][temp_y] == -player_color:
            direction_flips += 1
            temp_x += dx
            temp_y += dy

        # 如果在连续对手棋子后是己方棋子，则计入总数
        if ValidCell(temp_x, temp_y) and board[temp_x][temp_y] == player_color:
            total_flips += direction_flips

    return total_flips


def player(player_color, board):
    """
    AI玩家决策函数
    参数:
        player_color (int): 当前玩家颜色 (1=黑棋, -1=白棋)
        board (2D list): 当前棋盘状态
    返回:
        tuple: 最优移动坐标 (行, 列)
    """
    # 获取所有可行移动位置
    valid_moves = PossibleMove(player_color, board)

    # 无可行移动时返回(0,0)
    if not valid_moves:
        return (0, 0)

    # 定义棋盘关键位置
    corner_positions = [(1, 1), (1, 8), (8, 1), (8, 8)]
    edge_positions = ([(x, 1) for x in range(2, 8)] +
                      [(x, 8) for x in range(2, 8)] +
                      [(1, y) for y in range(2, 8)] +
                      [(8, y) for y in range(2, 8)])

    # 优先选择角落位置
    corner_moves = [move for move in valid_moves if move in corner_positions]
    if corner_moves:
        return random.choice(corner_moves)

    # 定义危险位置（角落相邻点）
    risky_positions = [(1, 2), (2, 1), (2, 2), (1, 7),
                       (2, 7), (2, 8), (7, 1), (7, 2),
                       (8, 2), (7, 7), (7, 8), (8, 7)]

    # 评估每个可行移动的分数
    move_scores = []
    for move in valid_moves:
        score = 0

        # 边缘位置加分
        if move in edge_positions:
            score += 10

        # 模拟移动后棋盘状态
        simulated_board = BoardCopy(board)
        simulated_board = PlaceMove(player_color, simulated_board, move[0], move[1])

        # 计算对手移动数量并惩罚
        opponent_moves = len(PossibleMove(-player_color, simulated_board))
        score -= opponent_moves * 0.5  # 减少对手选择权

        # 翻转数量加分
        flip_count = count_total_flips(player_color, board, move[0], move[1])
        score += flip_count * 0.2

        # 避免危险位置（角落相邻点）
        if move in risky_positions:
            score -= 15

        move_scores.append((move, score))

    # 选择最高分移动
    move_scores.sort(key=lambda x: x[1], reverse=True)
    best_score = move_scores[0][1]
    best_moves = [move for move, score in move_scores if score == best_score]

    # 多个最优解时随机选择
    return random.choice(best_moves)