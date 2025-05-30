# Module for Python course project V3.0 2025
# Optimized AI player using Minimax with Alpha-Beta pruning
# 优化后的AI玩家，使用带Alpha-Beta剪枝的Minimax算法

from Reversi import *
import copy

# 简化的位置权重表
POSITION_WEIGHTS = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,  16,   3,   3,  16,  -2,  10],
    [  5,  -2,   3,   3,   3,   3,  -2,   5],
    [  5,  -2,   3,   3,   3,   3,  -2,   5],
    [ 10,  -2,  16,   3,   3,  16,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100]
]

def evaluate_board(board, color):
    """优化后的评估函数 - 减少计算复杂度"""
    score = 0
    opponent = -color
    
    my_pieces = 0
    opp_pieces = 0
    position_score = 0
    corner_score = 0
    
    # 一次遍历完成所有计算
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == color:
                my_pieces += 1
                position_score += POSITION_WEIGHTS[x-1][y-1]
                # 角落奖励
                if (x, y) in [(1,1), (1,8), (8,1), (8,8)]:
                    corner_score += 30
            elif board[x][y] == opponent:
                opp_pieces += 1
                position_score -= POSITION_WEIGHTS[x-1][y-1]
                if (x, y) in [(1,1), (1,8), (8,1), (8,8)]:
                    corner_score -= 30
    
    # 简化的行动力评估
    my_moves = len(PossibleMove(color, board))
    opp_moves = len(PossibleMove(opponent, board))
    mobility_score = (my_moves - opp_moves) * 2
    
    # 根据游戏阶段调整权重
    total_pieces = my_pieces + opp_pieces
    if total_pieces > 50:  # 后期重视棋子数量
        piece_score = (my_pieces - opp_pieces) * 8
        score = piece_score + position_score + corner_score + mobility_score
    else:  # 前中期重视位置和行动力
        piece_score = (my_pieces - opp_pieces) * 2
        score = piece_score + position_score * 2 + corner_score + mobility_score * 2
    
    return score

def minimax(board, depth, alpha, beta, maximizing_player, color):
    """优化后的Minimax算法"""
    if depth == 0:
        return evaluate_board(board, color), None
    
    current_color = color if maximizing_player else -color
    possible_moves = PossibleMove(current_color, board)
    
    if not possible_moves:
        opponent_moves = PossibleMove(-current_color, board)
        if not opponent_moves:
            return evaluate_board(board, color), None
        else:
            return minimax(board, depth-1, alpha, beta, not maximizing_player, color)
    
    # 移动排序优化 - 优先尝试角落和边缘位置
    def move_priority(move):
        x, y = move
        if (x, y) in [(1,1), (1,8), (8,1), (8,8)]:
            return 0  # 最高优先级
        elif x == 1 or x == 8 or y == 1 or y == 8:
            return 1  # 次高优先级
        else:
            return 2  # 普通优先级
    
    possible_moves.sort(key=move_priority)
    best_move = possible_moves[0]
    
    if maximizing_player:
        max_eval = float('-inf')
        for move in possible_moves:
            # 使用更轻量的棋盘复制方法
            new_board = [row[:] for row in board]  # 浅拷贝替代深拷贝
            new_board = PlaceMove(current_color, new_board, move[0], move[1])
            eval_score, _ = minimax(new_board, depth-1, alpha, beta, False, color)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Alpha-Beta剪枝
        
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in possible_moves:
            new_board = [row[:] for row in board]  # 浅拷贝替代深拷贝
            new_board = PlaceMove(current_color, new_board, move[0], move[1])
            eval_score, _ = minimax(new_board, depth-1, alpha, beta, True, color)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha-Beta剪枝
        
        return min_eval, best_move

def get_opening_move(board, color):
    """简化的开局策略"""
    moves = PossibleMove(color, board)
    if not moves:
        return None
    
    # 简化的开局优先位置
    priority_positions = [
        (3, 3), (3, 6), (6, 3), (6, 6),  # 内角
        (4, 3), (3, 4), (5, 6), (6, 5)   # 次优位置
    ]
    
    for pos in priority_positions:
        if pos in moves:
            return pos
    
    return moves[0]

def player(color, board):
    """优化后的AI玩家主函数"""
    moves = PossibleMove(color, board)
    
    if not moves:
        return (0, 0)
    
    # 如果只有一个选择，直接返回
    if len(moves) == 1:
        return moves[0]
    
    # 计算当前棋盘上的棋子总数
    total_pieces = sum(row.count(1) + row.count(-1) for row in board)
    
    # 开局阶段使用简单策略
    if total_pieces <= 12:
        opening_move = get_opening_move(board, color)
        if opening_move:
            return opening_move
    
    # 大幅降低搜索深度以提高性能
    if total_pieces <= 20:      # 开局
        depth = 3
    elif total_pieces <= 45:    # 中局
        depth = 3
    else:                       # 残局
        depth = 4
    
    # 使用Minimax算法选择最佳走法
    _, best_move = minimax(board, depth, float('-inf'), float('inf'), True, color)
    
    return best_move if best_move else moves[0]

# 为了兼容性，也提供一个简化的接口
def advanced_player(color, board):
    """优化后的AI玩家 - 兼容接口"""
    return player(color, board)