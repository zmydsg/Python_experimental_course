"""
黑白棋AI策略模块
提供高级AI实现，符合player(Colour, Board)测试接口
优化版本 - 提升运行速度
"""

import random
import copy
import time
from Reversi import PossibleMove, ValidCell, PlaceMove, BoardCopy, Black, White, Empty

# 置换表，用于缓存已计算的棋盘状态
transposition_table = {}

# 强大的minimax AI实现，符合测试接口要求
def player(Colour, Board):
    '''An advanced AI player using enhanced minimax algorithm with alpha-beta pruning.
    Function signature follows the required testing format: player(Colour, Board) -> (x, y)
    Optimized version with better performance for complex board situations.'''
    
    # 位置权重表 - 更精细的权重设计
    weight_table = [
        [150, -30, 25, 12, 12, 25, -30, 150],  # 角落价值提高
        [-30, -50, -15, -10, -10, -15, -50, -30],  # 角落旁边更危险
        [25, -15, 8, 4, 4, 8, -15, 25],
        [12, -10, 4, 1, 1, 4, -10, 12],
        [12, -10, 4, 1, 1, 4, -10, 12],
        [25, -15, 8, 4, 4, 8, -15, 25],
        [-30, -50, -15, -10, -10, -15, -50, -30],
        [150, -30, 25, 12, 12, 25, -30, 150]
    ]
    
    def board_to_hash(board):
        '''将棋盘转换为可哈希的字符串，用于置换表'''
        return ''.join(''.join(str(board[i][j]) for j in range(10)) for i in range(10))
    
    def count_pieces(board, colour):
        '''计算棋盘上特定颜色的棋子数量'''
        count = 0
        for i in range(1, 9):
            for j in range(1, 9):
                if board[i][j] == colour:
                    count += 1
        return count
    
    def quick_evaluate(board, colour):
        '''快速评估函数，用于移动排序'''
        score = 0
        for i in range(1, 9):
            for j in range(1, 9):
                if board[i][j] == colour:
                    score += weight_table[j-1][i-1]
                elif board[i][j] == -colour:
                    score -= weight_table[j-1][i-1]
        return score
    
    def order_moves(moves, board, colour):
        '''移动排序优化，优先考虑可能更好的移动'''
        # 角落移动最优先
        corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
        corner_moves = [move for move in moves if move in corners]
        
        # 其他移动按快速评估排序
        other_moves = [move for move in moves if move not in corners]
        
        # 为其他移动计算快速评估分数
        move_scores = []
        for move in other_moves:
            x, y = move
            board_copy = BoardCopy(board)
            PlaceMove(colour, board_copy, x, y)
            score = quick_evaluate(board_copy, colour)
            move_scores.append((score, move))
        
        # 按分数降序排序
        move_scores.sort(reverse=True)
        sorted_other_moves = [move for _, move in move_scores]
        
        return corner_moves + sorted_other_moves
    
    def evaluate_board(board, colour):
        '''简化的评估函数，减少计算复杂度'''
        # 计算棋盘上的总棋子数，判断游戏阶段
        my_count = count_pieces(board, colour)
        opp_count = count_pieces(board, -colour)
        total_pieces = my_count + opp_count
        
        # 计算位置价值
        position_score = 0
        for i in range(1, 9):
            for j in range(1, 9):
                if board[i][j] == colour:
                    position_score += weight_table[j-1][i-1]
                elif board[i][j] == -colour:
                    position_score -= weight_table[j-1][i-1]
        
        # 计算行动力（合法移动数量）
        my_mobility = len(PossibleMove(colour, board))
        opp_mobility = len(PossibleMove(-colour, board))
        
        # 根据游戏阶段调整策略
        if total_pieces <= 20:  # 开局
            # 开局重视位置价值和行动力
            mobility_factor = 5 if my_mobility + opp_mobility > 0 else 0
            mobility_score = mobility_factor * (my_mobility - opp_mobility)
            return position_score + mobility_score
        elif total_pieces >= 50:  # 残局
            # 残局重视棋子数量差异
            return 100 * (my_count - opp_count) + position_score * 0.5
        else:  # 中局
            # 中局平衡位置和行动力
            mobility_factor = 3 if my_mobility + opp_mobility > 0 else 0
            mobility_score = mobility_factor * (my_mobility - opp_mobility)
            return position_score + mobility_score
    
    def minimax(board, depth, alpha, beta, is_maximizing, colour, start_time, time_limit=1.0):
        '''优化的Minimax算法，带时间控制和置换表'''
        # 时间控制 - 如果超时则返回
        if time.time() - start_time > time_limit:
            return evaluate_board(board, colour)
        
        # 置换表查找
        board_hash = board_to_hash(board)
        if board_hash in transposition_table:
            cached_depth, cached_score = transposition_table[board_hash]
            if cached_depth >= depth:
                return cached_score
        
        # 达到搜索深度时评估棋盘
        if depth == 0:
            score = evaluate_board(board, colour)
            transposition_table[board_hash] = (depth, score)
            return score
        
        # 检查游戏是否结束
        my_moves = PossibleMove(colour if is_maximizing else -colour, board)
        opp_moves = PossibleMove(-colour if is_maximizing else colour, board)
        
        if not my_moves and not opp_moves:
            # 游戏结束
            my_count = count_pieces(board, colour)
            opp_count = count_pieces(board, -colour)
            if my_count > opp_count:
                score = 10000
            elif my_count < opp_count:
                score = -10000
            else:
                score = 0
            transposition_table[board_hash] = (depth, score)
            return score
        
        if is_maximizing:
            max_eval = float('-inf')
            moves = PossibleMove(colour, board)
            
            if not moves:
                # 跳过回合
                return minimax(board, depth-1, alpha, beta, False, colour, start_time, time_limit)
            
            # 移动排序优化
            moves = order_moves(moves, board, colour)
            
            for move in moves:
                # 时间检查
                if time.time() - start_time > time_limit:
                    break
                    
                x, y = move
                board_copy = BoardCopy(board)
                PlaceMove(colour, board_copy, x, y)
                
                eval_score = minimax(board_copy, depth-1, alpha, beta, False, colour, start_time, time_limit)
                max_eval = max(max_eval, eval_score)
                
                # Alpha-Beta剪枝
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            transposition_table[board_hash] = (depth, max_eval)
            return max_eval
        else:
            min_eval = float('inf')
            moves = PossibleMove(-colour, board)
            
            if not moves:
                # 跳过回合
                return minimax(board, depth-1, alpha, beta, True, colour, start_time, time_limit)
            
            # 移动排序优化
            moves = order_moves(moves, board, -colour)
            
            for move in moves:
                # 时间检查
                if time.time() - start_time > time_limit:
                    break
                    
                x, y = move
                board_copy = BoardCopy(board)
                PlaceMove(-colour, board_copy, x, y)
                
                eval_score = minimax(board_copy, depth-1, alpha, beta, True, colour, start_time, time_limit)
                min_eval = min(min_eval, eval_score)
                
                # Alpha-Beta剪枝
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            
            transposition_table[board_hash] = (depth, min_eval)
            return min_eval
    
    def iterative_deepening_search(board, colour, time_limit=1.0):
        '''迭代深化搜索，在时间限制内尽可能深入搜索'''
        start_time = time.time()
        possible_moves = PossibleMove(colour, board)
        
        if not possible_moves:
            return (0, 0)
        
        best_move = possible_moves[0]
        
        # 迭代深化
        for depth in range(1, 8):  # 降低最大深度到8层
            if time.time() - start_time > time_limit * 0.7:  # 留30%时间作为缓冲
                break
            
            current_best_score = float('-inf')
            current_best_move = best_move
            
            # 移动排序优化
            ordered_moves = order_moves(possible_moves, board, colour)
            
            for move in ordered_moves:
                if time.time() - start_time > time_limit * 0.7:
                    break
                
                x, y = move
                board_copy = BoardCopy(board)
                PlaceMove(colour, board_copy, x, y)
                
                move_score = minimax(board_copy, depth-1, float('-inf'), float('inf'), 
                                   False, colour, start_time, time_limit)
                
                if move_score > current_best_score:
                    current_best_score = move_score
                    current_best_move = move
            
            best_move = current_best_move
        
        return best_move
    
    # 清理置换表，避免内存过大
    if len(transposition_table) > 10000:
        transposition_table.clear()
    
    # 获取所有可能的移动
    possible_moves = PossibleMove(Colour, Board)
    
    # 如果没有合法移动，返回(0,0)
    if not possible_moves:
        return (0, 0)
    
    # 检查角落位置是否可用（最高优先级）
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for move in corners:
        if move in possible_moves:
            return move
    
    # 计算剩余空位数量，决定搜索策略
    empty_count = 0
    for i in range(1, 9):
        empty_count += Board[i].count(Empty)
    
    # 根据游戏阶段调整时间限制
    if empty_count <= 10:
        time_limit = 1.4  # 残局稍长但不超过1.5秒
    elif empty_count <= 20:
        time_limit = 1.2
    elif empty_count <= 40:
        time_limit = 1.0
    else:
        time_limit = 0.8  # 开局快速决策
    
    # 使用迭代深化搜索
    return iterative_deepening_search(Board, Colour, time_limit) 