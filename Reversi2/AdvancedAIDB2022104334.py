# Module for Python course project V3.0 2025
# Advanced AI player using Minimax with Alpha-Beta pruning
# 高级AI玩家，使用带Alpha-Beta剪枝的Minimax算法

from Reversi import *
import copy

# 位置权重表 - 基于黑白棋经典策略
POSITION_WEIGHTS = [
    [120, -20,  20,   5,   5,  20, -20, 120],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [120, -20,  20,   5,   5,  20, -20, 120]
]

def evaluate_board(board, color):
    """评估棋盘状态，返回对指定颜色的评分"""
    score = 0
    opponent = -color
    
    # 1. 棋子数量差异
    my_pieces = 0
    opp_pieces = 0
    
    # 2. 位置价值评估
    position_score = 0
    
    # 3. 稳定性评估（角落和边缘）
    stability_score = 0
    
    # 4. 行动力评估（可行走法数量）
    my_moves = len(PossibleMove(color, board))
    opp_moves = len(PossibleMove(opponent, board))
    mobility_score = my_moves - opp_moves
    
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == color:
                my_pieces += 1
                position_score += POSITION_WEIGHTS[x-1][y-1]
                
                # 角落稳定性奖励
                if (x, y) in [(1,1), (1,8), (8,1), (8,8)]:
                    stability_score += 25
                # 边缘稳定性
                elif x == 1 or x == 8 or y == 1 or y == 8:
                    stability_score += 5
                    
            elif board[x][y] == opponent:
                opp_pieces += 1
                position_score -= POSITION_WEIGHTS[x-1][y-1]
                
                if (x, y) in [(1,1), (1,8), (8,1), (8,8)]:
                    stability_score -= 25
                elif x == 1 or x == 8 or y == 1 or y == 8:
                    stability_score -= 5
    
    # 游戏后期更重视棋子数量
    total_pieces = my_pieces + opp_pieces
    if total_pieces > 50:  # 后期
        piece_score = (my_pieces - opp_pieces) * 10
    else:  # 前中期
        piece_score = (my_pieces - opp_pieces) * 2
    
    # 综合评分
    score = piece_score + position_score * 2 + stability_score + mobility_score * 3
    
    return score

def minimax(board, depth, alpha, beta, maximizing_player, color):
    """Minimax算法with Alpha-Beta剪枝"""
    if depth == 0:
        return evaluate_board(board, color), None
    
    current_color = color if maximizing_player else -color
    possible_moves = PossibleMove(current_color, board)
    
    if not possible_moves:
        # 没有可行走法，检查对手是否也没有
        opponent_moves = PossibleMove(-current_color, board)
        if not opponent_moves:
            # 游戏结束，返回最终评分
            return evaluate_board(board, color), None
        else:
            # 跳过当前玩家
            return minimax(board, depth-1, alpha, beta, not maximizing_player, color)
    
    best_move = possible_moves[0]
    
    if maximizing_player:
        max_eval = float('-inf')
        for move in possible_moves:
            new_board = PlaceMove(current_color, copy.deepcopy(board), move[0], move[1])
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
            new_board = PlaceMove(current_color, copy.deepcopy(board), move[0], move[1])
            eval_score, _ = minimax(new_board, depth-1, alpha, beta, True, color)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha-Beta剪枝
        
        return min_eval, best_move

def get_opening_move(board, color):
    """开局策略 - 优先占据有利位置"""
    moves = PossibleMove(color, board)
    if not moves:
        return None
    
    # 开局优先级位置
    priority_positions = [
        (3, 3), (3, 6), (6, 3), (6, 6),  # 内角
        (4, 3), (3, 4), (5, 6), (6, 5),  # 次优位置
        (4, 6), (6, 4), (3, 5), (5, 3)   # 其他好位置
    ]
    
    for pos in priority_positions:
        if pos in moves:
            return pos
    
    return None

def player(color, board):
    """高级AI玩家主函数"""
    moves = PossibleMove(color, board)
    
    if not moves:
        return (0, 0)
    
    # 计算当前棋盘上的棋子总数
    total_pieces = sum(row.count(1) + row.count(-1) for row in board)
    
    # 开局阶段（前12步）使用开局策略
    if total_pieces <= 16:
        opening_move = get_opening_move(board, color)
        if opening_move:
            return opening_move
    
    # 根据游戏阶段调整搜索深度
    if total_pieces <= 20:      # 开局
        depth = 4
    elif total_pieces <= 45:    # 中局
        depth = 5
    else:                       # 残局
        depth = 6
    
    # 如果只有一个选择，直接返回
    if len(moves) == 1:
        return moves[0]
    
    # 使用Minimax算法选择最佳走法
    _, best_move = minimax(board, depth, float('-inf'), float('inf'), True, color)
    
    return best_move if best_move else moves[0]

# 为了兼容性，也提供一个简化的接口
def advanced_player(color, board):
    """高级AI玩家 - 兼容接口"""
    return player(color, board)

if __name__ == "__main__":
    # 测试代码
    test_board = BoardInit()
    print("测试高级AI...")
    move = player(White, test_board)
    print(f"AI选择的走法: {move}")