# -*- coding: utf-8 -*-

from Reversi import *
import random
import math

def player(Colour, Board):
    """基于模式识别和动态评估的黑白棋AI
    
    参数:
    Colour -- 玩家颜色(黑=1 或 白=-1)
    Board -- 当前棋盘状态
    
    返回:
    (x, y) -- 下一步坐标，若无合法移动则返回(0, 0)
    """
    # 获取所有合法移动
    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0)
    
    # 棋盘模式识别
    game_pattern = recognize_pattern(Board)
    
    # 动态评估所有可能的移动
    best_move = None
    best_score = -math.inf
    
    for move in possible_moves:
        # 模拟移动
        temp_board = BoardCopy(Board)
        PlaceMove(Colour, temp_board, move[0], move[1])
        
        # 综合评估
        score = dynamic_evaluate(Colour, temp_board, move, game_pattern)
        
        # 添加微小随机性打破平局
        score += random.uniform(0, 0.01)
        
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move

def recognize_pattern(Board):
    """识别当前棋盘的特定模式"""
    pattern = {
        'corner_control': 0,  # 角落控制情况
        'edge_dominance': 0,  # 边缘优势
        'center_presence': 0,  # 中心存在感
        'mobility_ratio': 0   # 移动力比率
    }
    
    # 角落分析
    corners = [(1,1), (1,8), (8,1), (8,8)]
    for x, y in corners:
        if Board[x][y] != Empty:
            pattern['corner_control'] += 1
    
    # 边缘分析(非角落)
    edge_positions = []
    for i in range(2, 8):
        edge_positions.extend([(1,i), (8,i), (i,1), (i,8)])
    
    edge_count = 0
    for x, y in edge_positions:
        if Board[x][y] != Empty:
            edge_count += 1
    pattern['edge_dominance'] = edge_count / len(edge_positions)
    
    # 中心分析(4x4中心区域)
    center_count = 0
    for x in range(3, 7):
        for y in range(3, 7):
            if Board[x][y] != Empty:
                center_count += 1
    pattern['center_presence'] = center_count / 16
    
    return pattern

def dynamic_evaluate(Colour, Board, move, pattern):
    """动态评估函数，根据识别到的模式调整权重"""
    x, y = move
    
    # 1. 基础位置价值
    base_value = get_position_value(x, y)
    
    # 2. 翻转潜力评估
    flip_potential = evaluate_flip_potential(Colour, Board, x, y)
    
    # 3. 未来移动选择评估
    future_options = evaluate_future_options(Colour, Board)
    
    # 4. 对手限制评估
    opponent_constraint = evaluate_opponent_constraint(Colour, Board)
    
    # 5. 模式适应调整
    pattern_adjustment = 0
    if pattern['corner_control'] < 2:  # 如果角落控制不足
        # 增加角落附近位置的权重
        if is_near_corner(x, y):
            pattern_adjustment += 20
    
    # 动态权重调整
    weights = {
        'base': 0.4,
        'flip': 0.3,
        'future': 0.2,
        'opponent': 0.1,
        'pattern': 0.3
    }
    
    # 综合评分
    score = (
        weights['base'] * base_value +
        weights['flip'] * flip_potential +
        weights['future'] * future_options +
        weights['opponent'] * opponent_constraint +
        weights['pattern'] * pattern_adjustment
    )
    
    return score

def get_position_value(x, y):
    """位置价值评估，采用环形权重分布"""
    # 构建环形价值分布
    ring_values = {
        0: 100,   # 角落
        1: -30,    # 角落相邻的危险位置
        2: 10,     # 边缘
        3: 5,      # 次边缘
        4: 3,      # 中心区域
        5: 1       # 最中心
    }
    
    # 计算位置到最近角落的距离
    corners = [(1,1), (1,8), (8,1), (8,8)]
    min_dist = min(abs(x-cx) + abs(y-cy) for cx, cy in corners)
    
    # 确定环形区域
    if min_dist == 0:
        ring = 0  # 角落
    elif min_dist == 1:
        ring = 1  # 危险区域
    elif x == 1 or x == 8 or y == 1 or y == 8:
        ring = 2  # 边缘
    elif x == 2 or x == 7 or y == 2 or y == 7:
        ring = 3  # 次边缘
    elif x == 3 or x == 6 or y == 3 or y == 6:
        ring = 4  # 中心区域
    else:
        ring = 5  # 最中心
    
    return ring_values[ring]

def evaluate_flip_potential(Colour, Board, x, y):
    """评估该位置潜在的翻转能力"""
    # 模拟移动前的棋盘状态
    temp_board = BoardCopy(Board)
    PlaceMove(Colour, temp_board, x, y)
    
    # 计算翻转的棋子数量
    original_count = sum(row.count(Colour) for row in Board[1:9])
    new_count = sum(row.count(Colour) for row in temp_board[1:9])
    
    return new_count - original_count

def evaluate_future_options(Colour, Board):
    """评估未来移动选择的可能性"""
    # 当前移动选择数量
    current_moves = len(PossibleMove(Colour, Board))
    
    # 对手可能的回应移动数量
    opponent_moves = len(PossibleMove(-Colour, Board))
    
    # 移动力比率
    if opponent_moves == 0:
        return 100  # 极大优势，对手无路可走
    return current_moves / opponent_moves * 10

def evaluate_opponent_constraint(Colour, Board):
    """评估对对手的限制程度"""
    # 找出对手的关键位置
    opponent_moves = PossibleMove(-Colour, Board)
    constraint_score = 0
    
    for x, y in opponent_moves:
        # 评估这些位置的重要性
        pos_value = get_position_value(x, y)
        if pos_value > 0:  # 如果是对手的好位置
            constraint_score -= pos_value * 2  # 需要限制
    
    return constraint_score

def is_near_corner(x, y):
    """判断是否靠近角落"""
    corners = [(1,1), (1,8), (8,1), (8,8)]
    return any(abs(x-cx) <= 2 and abs(y-cy) <= 2 for cx, cy in corners)