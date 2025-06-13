# Module for Python course project V3.0 2025
# This module is an example of player function to be submitted

from Reversi import *


def player(Colour, Board):
    """
    强化版黑白棋AI策略（单函数实现）：
    1. 角落优先占据
    2. 动态阶段评分系统
    3. 威胁规避与翻转链评估
    4. 全逻辑内聚无外部依赖
    """
    # 棋盘位置基础评分表（1-8对应棋盘坐标，0为边界填充）
    position_weights = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 100, -20, 10, 5, 5, 10, -20, 100, 0],  # (1,y)
        [0, -20, -30, -5, -5, -5, -5, -30, -20, 0],  # (2,y)
        [0, 10, -5, 10, 3, 3, 10, -5, 10, 0],  # (3,y)
        [0, 5, -5, 3, 2, 2, 3, -5, 5, 0],  # (4,y)
        [0, 5, -5, 3, 2, 2, 3, -5, 5, 0],  # (5,y)
        [0, 10, -5, 10, 3, 3, 10, -5, 10, 0],  # (6,y)
        [0, -20, -30, -5, -5, -5, -5, -30, -20, 0],  # (7,y)
        [0, 100, -20, 10, 5, 5, 10, -20, 100, 0],  # (8,y)
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    # 游戏阶段权重配置（早期/中期/后期）
    stage_weights = {
        'early': (4, 3, 1),
        'mid': (3, 2, 2),
        'late': (2, 1, 4)
    }

    # 获取所有合法移动
    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0)

    # 计算总棋子数判断游戏阶段
    total_pieces = sum(row.count(1) + row.count(-1) for row in Board)
    stage = 'early' if total_pieces < 20 else 'mid' if total_pieces < 40 else 'late'
    w_pos, w_mob, w_pce = stage_weights[stage]

    best_score = -float('inf')
    best_move = None

    # 角落优先检查（绝对优先级）
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for move in possible_moves:
        if move in corners:
            return move  # 直接返回角落坐标

    # 辅助函数：计算落子后的翻转棋子数
    def calculate_flips(x, y):
        flips = 0
        for dx, dy in NeighbourPosition:
            chain = 0
            cx, cy = x + dx, y + dy
            while ValidCell(cx, cy) and Board[cx][cy] == -Colour:
                chain += 1
                cx += dx
                cy += dy
                if Board[cx][cy] == Colour:
                    flips += chain
                    break
        return flips

    # 辅助函数：检查是否给对手创造角落机会
    def has_corner_threat(new_board):
        for x, y in corners:
            if new_board[x][y] == 0 and len(PossibleMove(-Colour, new_board)) > 0:
                return True
        return False

    # 遍历所有合法移动进行评估
    for (x, y) in possible_moves:
        # 危险区域惩罚（靠近角落的陷阱位置）
        if (x in (2, 7) and y in (1, 8)) or (x in (1, 8) and y in (2, 7)):
            score = -50
        else:
            # 基础位置评分
            score = position_weights[y][x] * w_pos
            # 行动力评分：减少对手可移动数量
            new_board = BoardCopy(Board)
            new_board = PlaceMove(Colour, new_board, x, y)
            opponent_moves = PossibleMove(-Colour, new_board)
            score -= len(opponent_moves) * w_mob * 2
            # 棋子数量评分
            current = sum(row.count(Colour) for row in Board)
            new_pce = sum(row.count(Colour) for row in new_board)
            score += (new_pce - current) * w_pce * 2
            # 边缘控制加分（非角落边缘）
            if (x in (1, 8) or y in (1, 8)) and (x, y) not in corners:
                score += 15 * w_pos
            # 角落威胁扣分
            if has_corner_threat(new_board):
                score -= 30
            # 翻转链长度加分（后期权重更高）
            if stage == 'late':
                score += calculate_flips(x, y) * 1.5

        # 更新最佳移动
        if score > best_score or (score == best_score and calculate_flips(x, y) > calculate_flips(*best_move)):
            best_score = score
            best_move = (x, y)

    # 备用策略：若无有效评分则选择翻转最多的位置
    if not best_move:
        best_move = max(possible_moves, key=lambda m: calculate_flips(*m))

    return best_move if best_move else possible_moves[0]