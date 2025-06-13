# Module for Python course project V3.0 2025
# This module is an example of player function to be submitted

# Module for Python course project V3.0 2025
# This module provides the fundamental functions needed for Reversi
from Reversi import *
import random
import time
import copy



def player(Colour, Board):
  
    
    # ---------------------- 辅助函数优化 ----------------------
    def get_stage(empty_count):
        """更精确的阶段划分"""
        if empty_count > 45:   return "opening"
        elif empty_count > 12: return "midgame"
        else:                  return "endgame"
    
    # 优化后的动态权重矩阵 (8x8)
    position_weights = [
        [500, -150, 30, 10, 10, 30, -150, 500],
        [-150, -250, -20, -5, -5, -20, -250, -150],
        [30,   -20,  15, 3, 3, 15,  -20, 30],
        [10,    -5,   3, 1, 1, 3,   -5, 10],
        [10,    -5,   3, 1, 1, 3,   -5, 10],
        [30,   -20,  15, 3, 3, 15,  -20, 30],
        [-150, -250, -20, -5, -5, -20, -250, -150],
        [500, -150, 30, 10, 10, 30, -150, 500]
    ]

    # 角落和边缘的稳定性控制
    corner_positions = [(1,1), (1,8), (8,1), (8,8)]
    edge_positions = [(x,y) for x in [1,8] for y in range(2,8)] + \
                    [(x,y) for y in [1,8] for x in range(2,8)]
    
    # ---------------------- 评估函数优化 ----------------------
    def evaluate_state(temp_board, eval_color):
        """强化评估函数，考虑更多因素"""
        my_score = 0
        opp_score = 0
        empty_count = 0
        
        # 计算棋盘状态
        for x in range(1, 9):
            for y in range(1, 9):
                if temp_board[x][y] == eval_color:
                    my_score += 1
                    # 位置权重
                    my_score += position_weights[x-1][y-1] * 0.01
                    
                    # 角落控制
                    if (x,y) in corner_positions:
                        my_score += 50
                    
                    # 边缘控制
                    elif (x,y) in edge_positions:
                        my_score += 5
                        
                elif temp_board[x][y] == -eval_color:
                    opp_score += 1
                else:
                    empty_count += 1
        
        # 行动力计算
        my_mobility = len(PossibleMove(eval_color, temp_board))
        opp_mobility = len(PossibleMove(-eval_color, temp_board))
        
        # 潜在行动力（可下位置数）
        my_potential = len(PossibleMove(eval_color, temp_board))
        opp_potential = len(PossibleMove(-eval_color, temp_board))
        
        # 阶段调整
        stage = get_stage(empty_count)
        mobility_factor = 0.8 if stage == "opening" else 0.5
        stability_factor = 0.2 if stage == "opening" else 0.5
        coin_factor = 0 if stage != "endgame" else 1.0
        
        # 综合评估
        score = 0
        score += (my_mobility - opp_mobility) * mobility_factor
        score += (my_potential - opp_potential) * 0.3
        score += (my_score - opp_score) * coin_factor
        
        # 终局特殊处理
        if stage == "endgame":
            score += (my_score - opp_score) * 5
        
        return score

    # ---------------------- 搜索算法优化 ----------------------
    def alpha_beta_search(board, color, depth, alpha, beta):
        """带深度优化的Alpha-Beta搜索"""
        # 到达叶子节点或游戏结束
        if depth == 0:
            return evaluate_state(board, Colour)  # 始终从根玩家视角评估
        
        moves = PossibleMove(color, board)
        
        # 无合法移动时处理
        if not moves:
            # 检查对手是否也无移动
            if not PossibleMove(-color, board):
                return evaluate_state(board, Colour)
            # 只有一方无移动，跳过回合
            return -alpha_beta_search(board, -color, depth-1, -beta, -alpha)
        
        # 最大化玩家（当前玩家）
        if color == Colour:
            max_eval = float('-inf')
            for move in moves:
                new_board = BoardCopy(board)
                PlaceMove(color, new_board, move[0], move[1])
                
                eval_score = alpha_beta_search(
                    new_board, 
                    -color, 
                    depth-1, 
                    alpha, 
                    beta
                )
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Alpha剪枝
            
            return max_eval
        
        # 最小化玩家（对手）
        else:
            min_eval = float('inf')
            for move in moves:
                new_board = BoardCopy(board)
                PlaceMove(color, new_board, move[0], move[1])
                
                eval_score = alpha_beta_search(
                    new_board, 
                    -color, 
                    depth-1, 
                    alpha, 
                    beta
                )
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Beta剪枝
            
            return min_eval

    # ---------------------- 主逻辑优化 ----------------------
    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0)
    
    # 动态调整搜索深度
    empty_count = sum(1 for x in range(1,9) for y in range(1,9) if Board[x][y] == Empty)
    depth = 3 if empty_count > 30 else (4 if empty_count > 15 else 6)
    
    best_score = float('-inf')
    best_move = possible_moves[0]
    
    # 搜索前先按启发式排序
    def move_priority(move):
        x, y = move
        priority = position_weights[x-1][y-1]
        # 角落位置最高优先级
        if (x,y) in corner_positions:
            priority += 1000
        # 边缘位置次优先级
        elif (x,y) in edge_positions:
            priority += 100
        return priority
    
    sorted_moves = sorted(possible_moves, key=move_priority, reverse=True)
    
    # 执行搜索
    for move in sorted_moves:
        new_board = BoardCopy(Board)
        PlaceMove(Colour, new_board, move[0], move[1])
        
        # 终局直接使用评估函数
        if empty_count <= 8:
            score = evaluate_state(new_board, Colour)
        else:
            score = alpha_beta_search(
                new_board,
                -Colour,
                depth-1,
                float('-inf'),
                float('inf')
            )
        
        # 更新最佳移动
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move

