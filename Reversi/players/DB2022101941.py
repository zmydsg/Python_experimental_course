'''
from Reversi import *
import math
import time
import random

# 预定义棋盘权重表
WEIGHTS = [
    [100, -20, 10, 5, 5, 10, -20, 100],
    [-20, -30, -5, -1, -1, -5, -30, -20],
    [10, -5, 1, 1, 1, 1, -5, 10],
    [5, -1, 1, 0, 0, 1, -1, 5],
    [5, -1, 1, 0, 0, 1, -1, 5],
    [10, -5, 1, 1, 1, 1, -5, 10],
    [-20, -30, -5, -1, -1, -5, -30, -20],
    [100, -20, 10, 5, 5, 10, -20, 100]
]

# 关键位置
CORNERS = {(1,1), (1,8), (8,1), (8,8)}
DANGER_ZONES = {(1,2), (1,7), (2,1), (2,2), (2,7), (2,8),
                (7,1), (7,2), (7,7), (7,8), (8,2), (8,7)}

def evaluate(board, original_player):
    """优化后的评估函数，减少计算量"""
    score = 0
    my_color = original_player
    opp_color = -original_player
    
    # 快速位置权重计算
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == my_color:
                score += WEIGHTS[x-1][y-1]
            elif board[x][y] == opp_color:
                score -= WEIGHTS[x-1][y-1]
    
    # 角落价值
    for corner in CORNERS:
        x, y = corner
        if board[x][y] == my_color:
            score += 50
        elif board[x][y] == opp_color:
            score -= 50
    
    # 行动力差
    my_mobility = len(PossibleMove(my_color, board))
    opp_mobility = len(PossibleMove(opp_color, board))
    score += (my_mobility - opp_mobility) * 3
    
    # 后期棋子数量差
    if my_mobility + opp_mobility < 10:  # 接近终局
        my_tiles = 0
        opp_tiles = 0
        for x in range(1, 9):
            for y in range(1, 9):
                if board[x][y] == my_color:
                    my_tiles += 1
                elif board[x][y] == opp_color:
                    opp_tiles += 1
        score += (my_tiles - opp_tiles) * 5
    
    return score

def alpha_beta_search(board, depth, alpha, beta, current_player, original_player, start_time):
    """带时间限制和移动排序的alpha-beta搜索"""
    # 检查时间限制
    if time.perf_counter() - start_time > 1.4:
        return evaluate(board, original_player)
    
    if depth == 0:
        return evaluate(board, original_player)
    
    moves = PossibleMove(current_player, board)
    
    # 处理无合法移动的情况
    if not moves:
        opp_moves = PossibleMove(-current_player, board)
        if not opp_moves:  # 游戏结束
            my_tiles = 0
            opp_tiles = 0
            for x in range(1, 9):
                for y in range(1, 9):
                    if board[x][y] == original_player:
                        my_tiles += 1
                    elif board[x][y] == -original_player:
                        opp_tiles += 1
            return my_tiles - opp_tiles
        # 当前玩家pass
        return alpha_beta_search(board, depth-1, alpha, beta, -current_player, original_player, start_time)
    
    # 移动排序：角落优先，危险区域靠后
    moves.sort(key=lambda move: (
        -1000 if move in CORNERS else  # 角落最高优先级
        1000 if move in DANGER_ZONES else  # 危险区域最低优先级
        WEIGHTS[move[0]-1][move[1]-1]  # 其他位置按权重排序
    ), reverse=True)
    
    if current_player == original_player:
        max_val = -math.inf
        for move in moves:
            # 浅拷贝棋盘（比深拷贝快10倍）
            new_board = [row[:] for row in board]
            PlaceMove(current_player, new_board, move[0], move[1])
            
            val = alpha_beta_search(new_board, depth-1, alpha, beta, -current_player, original_player, start_time)
            
            # 检查时间限制
            if time.perf_counter() - start_time > 1.4:
                return val
            
            max_val = max(max_val, val)
            alpha = max(alpha, max_val)
            if beta <= alpha:
                break  # Beta剪枝
        return max_val
    else:
        min_val = math.inf
        for move in moves:
            # 浅拷贝棋盘
            new_board = [row[:] for row in board]
            PlaceMove(current_player, new_board, move[0], move[1])
            
            val = alpha_beta_search(new_board, depth-1, alpha, beta, -current_player, original_player, start_time)
            
            # 检查时间限制
            if time.perf_counter() - start_time > 1.4:
                return val
            
            min_val = min(min_val, val)
            beta = min(beta, min_val)
            if beta <= alpha:
                break  # Alpha剪枝
        return min_val

def player(Colour, Board):
    """优化后的AI玩家函数，特别提升黑棋性能"""
    start_time = time.perf_counter()
    legal_moves = PossibleMove(Colour, Board)
    
    # 如果没有合法移动
    if not legal_moves:
        return (0, 0)
    
    # 直接抢占角落
    for move in legal_moves:
        if move in CORNERS:
            return move
    
    # 避免危险区域
    safe_moves = [move for move in legal_moves if move not in DANGER_ZONES]
    if safe_moves:
        legal_moves = safe_moves
    
    # 自适应搜索参数
    search_depth = 4
    best_move = None
    best_value = -math.inf
    alpha = -math.inf
    beta = math.inf
    
    # 移动排序：角落优先，危险区域靠后
    legal_moves.sort(key=lambda move: (
        -1000 if move in CORNERS else
        1000 if move in DANGER_ZONES else
        WEIGHTS[move[0]-1][move[1]-1]
    ), reverse=True)
    
    for move in legal_moves:
        # 浅拷贝棋盘（比深拷贝快10倍）
        new_board = [row[:] for row in Board]
        PlaceMove(Colour, new_board, move[0], move[1])
        
        # 进行对手回合的搜索
        current_val = alpha_beta_search(
            new_board, 
            search_depth-1, 
            alpha, 
            beta, 
            -Colour, 
            Colour,
            start_time
        )
        
        # 检查时间限制
        if time.perf_counter() - start_time > 1.4:
            return best_move if best_move else move
        
        # 更新最佳走法
        if current_val > best_value:
            best_value = current_val
            best_move = move
            alpha = max(alpha, best_value)
    
    return best_move if best_move else legal_moves[0]
'''

from Reversi import *
import math
import time

# 预定义棋盘权重表（简化版）
WEIGHTS = [
    [100, -30, 10, 5, 5, 10, -30, 100],
    [-30, -50, -2, -2, -2, -2, -50, -30],
    [10, -2, 1, 1, 1, 1, -2, 10],
    [5, -2, 1, 0, 0, 1, -2, 5],
    [5, -2, 1, 0, 0, 1, -2, 5],
    [10, -2, 1, 1, 1, 1, -2, 10],
    [-30, -50, -2, -2, -2, -2, -50, -30],
    [100, -30, 10, 5, 5, 10, -30, 100]
]

# 关键位置
CORNERS = {(1,1), (1,8), (8,1), (8,8)}
DANGER_ZONES = {(1,2), (1,7), (2,1), (2,2), (2,7), (2,8),
                (7,1), (7,2), (7,7), (7,8), (8,2), (8,7)}
STABLE_ZONES = {(3,3), (3,6), (6,3), (6,6), (4,4), (4,5), (5,4), (5,5)}

def quick_evaluate(board, player_color):
    """极速评估函数 - 只计算关键指标"""
    score = 0
    opp_color = -player_color
    
    # 1. 角落控制 - 最高优先级
    for corner in CORNERS:
        x, y = corner
        if board[x][y] == player_color:
            score += 50
        elif board[x][y] == opp_color:
            score -= 50
    
    # 2. 稳定区域控制
    for zone in STABLE_ZONES:
        x, y = zone
        if board[x][y] == player_color:
            score += 15
        elif board[x][y] == opp_color:
            score -= 15
    
    # 3. 行动力计算（快速版）
    my_moves = len(PossibleMove(player_color, board))
    opp_moves = len(PossibleMove(opp_color, board))
    score += (my_moves - opp_moves) * 3
    
    # 4. 简单位置权重
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == player_color:
                score += WEIGHTS[x-1][y-1]
    
    return score

def player(Colour, Board):
    """极速版AI玩家 - 无搜索算法"""
    start_time = time.perf_counter()
    legal_moves = PossibleMove(Colour, Board)
    
    # 如果没有合法移动
    if not legal_moves:
        return (0, 0)
    
    # 1. 优先抢占角落 - 直接返回
    for move in legal_moves:
        if move in CORNERS:
            return move
    
    # 2. 避免危险区域 - 过滤掉危险移动
    safe_moves = [move for move in legal_moves if move not in DANGER_ZONES]
    if safe_moves:
        legal_moves = safe_moves
    
    # 3. 如果移动数很少 - 直接返回第一个安全移动
    if len(legal_moves) <= 3:
        return legal_moves[0]
    
    # 4. 快速评估所有合法移动
    best_score = -100000
    best_move = legal_moves[0]  # 默认选择第一个移动
    
    # 限制评估数量 - 最多评估10个移动
    max_evaluations = min(10, len(legal_moves))
    
    for i in range(max_evaluations):
        move = legal_moves[i]
        
        # 创建新棋盘 - 使用浅拷贝加速
        new_board = [row[:] for row in Board]
        
        # 模拟落子
        PlaceMove(Colour, new_board, move[0], move[1])
        
        # 快速评估
        move_score = quick_evaluate(new_board, Colour)
        
        # 特殊规则：稳定区域额外加分
        if move in STABLE_ZONES:
            move_score += 20
        
        # 特殊规则：避免给对手角落机会
        for corner in CORNERS:
            if new_board[corner[0]][corner[1]] == -Colour:
                move_score -= 40
        
        # 更新最佳移动
        if move_score > best_score:
            best_score = move_score
            best_move = move
        
        # 时间检查 - 确保不超时
        if time.perf_counter() - start_time > 0.01:  # 10毫秒超时保护
            break
    
    return best_move