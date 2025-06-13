# Module for Python course project V3.0 2025
# This module provide the fundamental functions needed for Reversi


from Reversi import *
import random
import time
import copy

def player(Colour, Board):
    # 0. 严格时间控制 - 立即开始计时
    start_time = time.perf_counter()
    TIME_LIMIT = 1.3  # 严格时间限制，留出0.2秒安全边界
    
    # 1. 获取所有合法移动
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)
    
    # 2. 绝对优先选择角落位置 - 翻转棋黄金法则
    CORNERS = [(1,1), (1,8), (8,1), (8,8)]
    for move in moves:
        if move in CORNERS:
            return move
    
    # 3. 严格避免危险位置（C位） - 防止被翻角
    DANGER_POSITIONS = [(2,2), (2,7), (7,2), (7,7)]
    safe_moves = [move for move in moves if move not in DANGER_POSITIONS]
    if not safe_moves:
        safe_moves = moves
    
    # 4. 预定义权重矩阵 - 避免重复计算
    WEIGHTS = [
        [1000, -150, 100,  50,  50, 100, -150, 1000],
        [-150, -250, -20, -10, -10, -20, -250, -150],
        [100,  -20,   5,   2,   2,   5,  -20,  100],
        [50,   -10,   2,   1,   1,   2,  -10,   50],
        [50,   -10,   2,   1,   1,   2,  -10,   50],
        [100,  -20,   5,   2,   2,   5,  -20,  100],
        [-150, -250, -20, -10, -10, -20, -250, -150],
        [1000, -150, 100,  50,  50, 100, -150, 1000],
    ]
    
    # 5. 极简评价函数 - 避免任何复杂计算
    def evaluate(board):
        score = 0
        # 只计算位置价值 - 避免任何额外计算
        for x in range(1, 9):
            for y in range(1, 9):
                if board[x][y] == Colour:
                    score += WEIGHTS[y-1][x-1]
                elif board[x][y] == -Colour:
                    score -= WEIGHTS[y-1][x-1]
        return score
    
    # 6. 简化α-β剪枝 - 限制递归深度
    def simple_alphabeta(board, depth, alpha, beta, maximizing):
        # 时间检查 - 每个节点都检查
        if time.perf_counter() - start_time > TIME_LIMIT:
            raise TimeoutError()
            
        if depth == 0:
            return evaluate(board)
        
        player_color = Colour if maximizing else -Colour
        moves_local = PossibleMove(player_color, board)
        
        # 如果没有合法移动，跳过回合
        if not moves_local:
            return simple_alphabeta(board, depth-1, alpha, beta, not maximizing)
        
        # 按位置价值排序移动 - 提高剪枝效率
        moves_local.sort(key=lambda m: WEIGHTS[m[1]-1][m[0]-1], reverse=maximizing)
        
        if maximizing:
            max_val = float('-inf')
            for x, y in moves_local:
                # 时间检查 - 每个移动前检查
                if time.perf_counter() - start_time > TIME_LIMIT:
                    return max_val
                    
                b2 = BoardCopy(board)
                PlaceMove(player_color, b2, x, y)
                val = simple_alphabeta(b2, depth-1, alpha, beta, False)
                max_val = max(max_val, val)
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
            return max_val
        else:
            min_val = float('inf')
            for x, y in moves_local:
                if time.perf_counter() - start_time > TIME_LIMIT:
                    return min_val
                    
                b2 = BoardCopy(board)
                PlaceMove(player_color, b2, x, y)
                val = simple_alphabeta(b2, depth-1, alpha, beta, True)
                min_val = min(min_val, val)
                beta = min(beta, val)
                if beta <= alpha:
                    break
            return min_val
    
    # 7. 固定深度搜索 - 避免迭代加深的开销
    MAX_DEPTH = 4  # 固定搜索深度
    
    best_move = safe_moves[0]
    best_score = float('-inf')
    
    try:
        # 按位置价值排序移动 - 确保高价值位置优先搜索
        safe_moves.sort(key=lambda m: WEIGHTS[m[1]-1][m[0]-1], reverse=True)
        
        for move in safe_moves:
            # 严格时间检查 - 移动前检查
            if time.perf_counter() - start_time > TIME_LIMIT:
                break
                
            new_board = BoardCopy(Board)
            PlaceMove(Colour, new_board, move[0], move[1])
            
            # 评估对手的最佳回应
            score = simple_alphabeta(new_board, MAX_DEPTH-1, float('-inf'), float('inf'), False)
            
            if score > best_score:
                best_score = score
                best_move = move
    except TimeoutError:
        # 超时立即返回当前最佳
        return best_move
    
    # 最终时间检查
    if time.perf_counter() - start_time > TIME_LIMIT:
        return best_move
    
    return best_move