from Reversi import *
import math
import time

# 简化的静态权重表
WEIGHTS = [
    [100, -20, 10, 5, 5, 10, -20, 100],
    [-20, -40, -2, -2, -2, -2, -40, -20],
    [10, -2, 1, 1, 1, 1, -2, 10],
    [5, -2, 1, 1, 1, 1, -2, 5],
    [5, -2, 1, 1, 1, 1, -2, 5],
    [10, -2, 1, 1, 1, 1, -2, 10],
    [-20, -40, -2, -2, -2, -2, -40, -20],
    [100, -20, 10, 5, 5, 10, -20, 100]
]

# 全局时间控制
start_time = 0
TIME_LIMIT = 1.0  # 更保守的时间限制

def time_up():
    return time.time() - start_time > TIME_LIMIT

# 超快速评估函数
def fast_eval(Board, Colour):
    score = 0
    for x in range(1, 9):
        for y in range(1, 9):
            piece = Board[x][y]
            if piece == Colour:
                score += WEIGHTS[x-1][y-1]
            elif piece == -Colour:
                score -= WEIGHTS[x-1][y-1]
    return score

# 简化的minimax（减少递归深度和复杂度）
def simple_minimax(Board, depth, is_max, colour, alpha, beta):
    if time_up() or depth == 0:
        return fast_eval(Board, colour)
    
    moves = PossibleMove(colour if is_max else -colour, Board)
    if not moves:
        return fast_eval(Board, colour)
    
    # 简单排序：优先考虑角落和边缘
    def move_priority(move):
        x, y = move
        return WEIGHTS[x-1][y-1]
    
    moves.sort(key=move_priority, reverse=True)
    
    if is_max:
        max_eval = -999999
        for move in moves[:min(8, len(moves))]:  # 限制搜索宽度
            if time_up():
                break
            new_board = BoardCopy(Board)
            PlaceMove(colour, new_board, move[0], move[1])
            eval_score = simple_minimax(new_board, depth-1, False, colour, alpha, beta)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = 999999
        for move in moves[:min(8, len(moves))]:  # 限制搜索宽度
            if time_up():
                break
            new_board = BoardCopy(Board)
            PlaceMove(-colour, new_board, move[0], move[1])
            eval_score = simple_minimax(new_board, depth-1, True, colour, alpha, beta)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

# 主函数（保持接口不变）
def player(Colour, Board):
    global start_time
    start_time = time.time()
    
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)
    
    if len(moves) == 1:
        return moves[0]
    
    # 计算已下棋子数量
    piece_count = sum(row.count(1) + row.count(-1) for row in Board)
    
    # 动态深度：越到后期深度越深，但最多3层
    if piece_count < 20:
        depth = 2
    elif piece_count < 50:
        depth = 3
    else:
        depth = 4
    
    best_move = moves[0]
    best_score = -999999
    
    # 预排序移动
    def move_priority(move):
        x, y = move
        return WEIGHTS[x-1][y-1]
    
    moves.sort(key=move_priority, reverse=True)
    
    # 搜索最佳移动
    for move in moves[:min(12, len(moves))]:  # 限制考虑的移动数量
        if time_up():
            break
            
        new_board = BoardCopy(Board)
        PlaceMove(Colour, new_board, move[0], move[1])
        
        score = simple_minimax(new_board, depth-1, False, Colour, -999999, 999999)
        
        if score > best_score:
            best_score = score
            best_move = move
        
        # 如果找到很好的移动就提前结束
        if score >= 50:  # 找到好位置就停止
            break
    
    return best_move