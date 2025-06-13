# Module for Python course project V3.0 2025
# This module is an example of player function to be submitted

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

# consider rings, coners and neighbour player's cells
# Place the chess-pieces at the outer corners/rings as much as possible

def player(Colour, Board):
    """高级翻转棋AI策略
    参数:
        Colour: 当前玩家颜色 (Black=1, White=-1)
        Board: 当前棋盘状态 (10x10列表)
    返回:
        (x,y): 最佳移动坐标
    """
    # 1. 获取所有合法移动
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)

    # 2. 根据游戏阶段选择策略
    empty_count = sum(row.count(Empty) for row in Board)

    # 开局阶段(前20步) - 使用位置权重和行动力
    if empty_count > 44:
        return opening_strategy(Colour, Board, moves)
    # 中局阶段 - 使用位置权重、行动力和边缘控制
    elif empty_count > 12:
        return midgame_strategy(Colour, Board, moves)
    # 终局阶段 - 使用最小最大算法搜索
    else:
        return endgame_strategy(Colour, Board, moves, depth=3)


# 开局策略
def opening_strategy(Colour, Board, moves):
    """开局策略:优先占据关键位置"""
    # 关键位置权重(角落和边缘价值高)
    position_weights = [
        [100, -20, 10, 5, 5, 10, -20, 100],
        [-20, -40, -5, -5, -5, -5, -40, -20],
        [10, -5, 6, 2, 2, 6, -5, 10],
        [5, -5, 2, 1, 1, 2, -5, 5],
        [5, -5, 2, 1, 1, 2, -5, 5],
        [10, -5, 6, 2, 2, 6, -5, 10],
        [-20, -40, -5, -5, -5, -5, -40, -20],
        [100, -20, 10, 5, 5, 10, -20, 100]
    ]

    # 优先占据角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for move in moves:
        if move in corners:
            return move

    # 其次选择权重最高的位置
    best_move = moves[0]
    best_score = -float('inf')
    for (x, y) in moves:
        score = position_weights[x - 1][y - 1]
        # 避免给对手创造角落机会
        if not gives_opponent_corner(Colour, Board, (x, y)):
            score += 20
        if score > best_score:
            best_score = score
            best_move = (x, y)
    return best_move


# 中局策略
def midgame_strategy(Colour, Board, moves):
    """中局策略:平衡位置权重和行动力"""
    opponent = -Colour
    best_move = moves[0]
    best_score = -float('inf')

    for (x, y) in moves:
        # 1. 模拟走这一步
        new_board = PlaceMove(Colour, BoardCopy(Board), x, y)

        # 2. 计算位置权重
        position_score = evaluate_position(Colour, new_board)

        # 3. 计算行动力(我方下一步可选位置数)
        my_mobility = len(PossibleMove(Colour, new_board))

        # 4. 计算对手行动力(对手下一步可选位置数)
        opponent_mobility = len(PossibleMove(opponent, new_board))

        # 5. 综合评分
        score = position_score + 20 * (my_mobility - opponent_mobility)

        # 6. 避免给对手创造角落机会
        if gives_opponent_corner(Colour, Board, (x, y)):
            score -= 100

        if score > best_score:
            best_score = score
            best_move = (x, y)

    return best_move


# 终局策略
def endgame_strategy(Colour, Board, moves, depth):
    """终局策略:使用最小最大算法搜索"""
    opponent = -Colour
    best_move = moves[0]
    best_score = -float('inf')

    for (x, y) in moves:
        # 模拟走这一步
        new_board = PlaceMove(Colour, BoardCopy(Board), x, y)

        # 最小最大搜索
        score = minimax(opponent, new_board, depth - 1, False)

        if score > best_score:
            best_score = score
            best_move = (x, y)

    return best_move


def minimax(player, board, depth, is_maximizing):
    """最小最大算法"""
    if depth == 0:
        return evaluate_position(player, board)

    moves = PossibleMove(player, board)
    opponent = -player

    if is_maximizing:
        best_score = -float('inf')
        if not moves:
            return evaluate_position(player, board)
        for (x, y) in moves:
            new_board = PlaceMove(player, BoardCopy(board), x, y)
            score = minimax(opponent, new_board, depth - 1, False)
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = float('inf')
        if not moves:
            return evaluate_position(player, board)
        for (x, y) in moves:
            new_board = PlaceMove(player, BoardCopy(board), x, y)
            score = minimax(opponent, new_board, depth - 1, True)
            best_score = min(best_score, score)
        return best_score


def evaluate_position(Colour, board):
    """评估棋盘状态"""
    opponent = -Colour
    my_score = 0
    opp_score = 0

    # 1. 棋子数量
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == Colour:
                my_score += 1
            elif board[x][y] == opponent:
                opp_score += 1

    # 2. 位置权重
    position_weights = [
        [100, -20, 10, 5, 5, 10, -20, 100],
        [-20, -40, -5, -5, -5, -5, -40, -20],
        [10, -5, 6, 2, 2, 6, -5, 10],
        [5, -5, 2, 1, 1, 2, -5, 5],
        [5, -5, 2, 1, 1, 2, -5, 5],
        [10, -5, 6, 2, 2, 6, -5, 10],
        [-20, -40, -5, -5, -5, -5, -40, -20],
        [100, -20, 10, 5, 5, 10, -20, 100]
    ]

    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == Colour:
                my_score += position_weights[x - 1][y - 1] * 0.1
            elif board[x][y] == opponent:
                opp_score += position_weights[x - 1][y - 1] * 0.1

    # 3. 行动力(可选移动数量)
    my_mobility = len(PossibleMove(Colour, board))
    opp_mobility = len(PossibleMove(opponent, board))
    my_score += my_mobility * 5
    opp_score += opp_mobility * 5

    # 4. 角落控制
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for (x, y) in corners:
        if board[x][y] == Colour:
            my_score += 30
        elif board[x][y] == opponent:
            opp_score += 30

    return my_score - opp_score


def gives_opponent_corner(Colour, Board, move):
    """检查这个移动是否会为对手创造角落机会"""
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
                # 检查对手是否能通过这个移动获得角落
                temp_board = BoardCopy(Board)
                temp_board[x][y] = Colour
                if corner in PossibleMove(opponent, temp_board):
                    return True
    return False

