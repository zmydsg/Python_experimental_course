# player2.py - 实现一个使用极小极大算法的AI玩家
from reversi import *

# 棋盘位置的权重矩阵，角落和边缘的权重更高
WEIGHTS = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 120, -20, 20, 5, 5, 20, -20, 120, 0],
    [0, -20, -40, -5, -5, -5, -5, -40, -20, 0],
    [0, 20, -5, 15, 3, 3, 15, -5, 20, 0],
    [0, 5, -5, 3, 3, 3, 3, -5, 5, 0],
    [0, 5, -5, 3, 3, 3, 3, -5, 5, 0],
    [0, 20, -5, 15, 3, 3, 15, -5, 20, 0],
    [0, -20, -40, -5, -5, -5, -5, -40, -20, 0],
    [0, 120, -20, 20, 5, 5, 20, -20, 120, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

def evaluate_board(player, board):
    """评估棋盘对玩家的有利程度"""
    opponent = -player
    player_score = 0
    opponent_score = 0
    
    # 计算加权分数
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == player:
                player_score += WEIGHTS[x][y]
            elif board[x][y] == opponent:
                opponent_score += WEIGHTS[x][y]
    
    # 计算行动力（可行移动数量）
    player_mobility = len(PossibleMove(player, board))
    opponent_mobility = len(PossibleMove(opponent, board))
    
    # 综合评分
    return player_score - opponent_score + (player_mobility - opponent_mobility) * 2

def minimax(player, board, depth, alpha, beta, maximizing):
    """极小极大算法带Alpha-Beta剪枝"""
    if depth == 0 or GameOver(board):
        return evaluate_board(player, board), None
    
    if maximizing:
        # 玩家回合，寻找最大值
        max_eval = float('-inf')
        best_move = None
        possible_moves = PossibleMove(player, board)
        
        if not possible_moves:
            # 如果没有可行的移动，跳过回合
            eval_score, _ = minimax(player, board, depth - 1, alpha, beta, False)
            return eval_score, None
        
        for move in possible_moves:
            x, y = move
            new_board = PlaceMove(player, board, x, y)
            eval_score, _ = minimax(player, new_board, depth - 1, alpha, beta, False)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta剪枝
        
        return max_eval, best_move
    else:
        # 对手回合，寻找最小值
        min_eval = float('inf')
        best_move = None
        opponent = -player
        possible_moves = PossibleMove(opponent, board)
        
        if not possible_moves:
            # 如果没有可行的移动，跳过回合
            eval_score, _ = minimax(player, board, depth - 1, alpha, beta, True)
            return eval_score, None
        
        for move in possible_moves:
            x, y = move
            new_board = PlaceMove(opponent, board, x, y)
            eval_score, _ = minimax(player, new_board, depth - 1, alpha, beta, True)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha剪枝
        
        return min_eval, best_move

def player2(player, board):
    """使用极小极大算法的AI玩家"""
    # 获取所有可能的移动
    possible_moves = PossibleMove(player, board)
    
    # 如果没有可行的移动，返回(-1, -1)表示跳过
    if not possible_moves:
        return (-1, -1)
    
    # 使用极小极大算法选择最佳移动
    # 深度设置为3，可以根据需要调整
    _, best_move = minimax(player, board, 3, float('-inf'), float('inf'), True)
    
    return best_move if best_move else possible_moves[0]