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
# Module for Python course project V3.0 2025
# This module provide the fundamental functions needed for Reversi

import random
import time
import copy

# ... [文件其他部分保持不变] ...

# 修改后的智能玩家函数
def player(Colour, Board):
    '''强化版AI玩家：结合深度搜索、位置评估和对手行动限制策略'''
    
    # 预定义位置权重矩阵（角落高权重，危险位置负权重）
    WEIGHT_MATRIX = [
        [100, -30, 15, 5, 5, 15, -30, 100],
        [-30, -50, -10, -5, -5, -10, -50, -30],
        [15, -10, 3, 1, 1, 3, -10, 15],
        [5, -5, 1, 0, 0, 1, -5, 5],
        [5, -5, 1, 0, 0, 1, -5, 5],
        [15, -10, 3, 1, 1, 3, -10, 15],
        [-30, -50, -10, -5, -5, -10, -50, -30],
        [100, -30, 15, 5, 5, 15, -30, 100]
    ]
    
    # 危险位置（应尽量避免）
    DANGER_POSITIONS = [(2,2), (2,7), (7,2), (7,7),  # X位
                        (1,2), (2,1), (1,7), (2,8), (7,1), (8,2), (7,8), (8,7)]  # C位
    
    # 计算棋盘空格数量
    def count_empty(board):
        return sum(row.count(Empty) for row in board) - 4  # 初始有4个棋子
    
    # 深度评估函数
    def evaluate_move(move, colour, board, depth=2):
        '''递归评估移动的价值，考虑多层博弈'''
        x, y = move
        
        # 直接占据角落的情况给予最高优先级
        if (x, y) in [(1, 1), (1, 8), (8, 1), (8, 8)]:
            return 1000  # 最高优先级
        
        # 创建模拟棋盘
        sim_board = BoardCopy(board)
        sim_board = PlaceMove(colour, sim_board, x, y)
        
        # 计算对手可用移动数（越少越好）
        opponent = -colour
        opponent_moves = PossibleMove(opponent, sim_board)
        opponent_options = len(opponent_moves)
        
        # 位置权重奖励
        position_weight = WEIGHT_MATRIX[y-1][x-1]
        
        # 深度搜索（递归评估对手的最佳应对）
        opponent_best = float('-inf')
        if depth > 0 and opponent_options > 0:
            for opp_move in opponent_moves:
                # 递归评估对手的移动价值（减少深度）
                opp_value = evaluate_move(opp_move, opponent, sim_board, depth-1)
                if opp_value > opponent_best:
                    opponent_best = opp_value
        
        # 综合评分公式
        score = (200 - opponent_options * 10)  # 基础分 - 对手选项惩罚
        score += position_weight  # 位置权重
        score -= opponent_best * 0.5  # 考虑对手的最佳应对
        
        # 危险位置惩罚
        if move in DANGER_POSITIONS:
            # 根据游戏阶段调整惩罚强度
            empty = count_empty(board)
            penalty = -200 if empty > 40 else -100 if empty > 20 else -50
            score += penalty
        
        return score

    # 主逻辑开始
    legal_moves = PossibleMove(Colour, Board)
    if not legal_moves:
        return (0, 0)
    
    # 为所有合法移动评分
    scored_moves = []
    for move in legal_moves:
        # 根据剩余空格调整搜索深度
        empty = count_empty(Board)
        depth = 2 if empty < 25 else 1  # 空格少时增加搜索深度
        score = evaluate_move(move, Colour, Board, depth)
        scored_moves.append((move, score))
    
    # 选择最高分移动
    scored_moves.sort(key=lambda x: -x[1])
    best_score = scored_moves[0][1]
    best_moves = [move for move, score in scored_moves if score == best_score]
    
    # 若有多个最佳选择，优先选择边缘位置
    edge_moves = [move for move in best_moves 
                 if move[0] in (1, 8) or move[1] in (1, 8)]
    if edge_moves:
        return random.choice(edge_moves)
    
    return random.choice(best_moves)

