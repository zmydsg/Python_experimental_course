"""
Module for Python course project V3.0 2025
优化的高速Reversi AI玩家 - 大幅简化以提升运行速度
"""

from Reversi import *
import random

# 位置权重表（简化版）- 角落最重要，边缘次之
POSITION_WEIGHTS = [
    [0,  0,  0,  0,  0,  0,  0,  0,  0, 0],
    [0,100,-10, 10,  5,  5, 10,-10,100, 0],
    [0,-10,-20, -1, -1, -1, -1,-20,-10, 0], 
    [0, 10, -1,  5,  1,  1,  5, -1, 10, 0],
    [0,  5, -1,  1,  1,  1,  1, -1,  5, 0],
    [0,  5, -1,  1,  1,  1,  1, -1,  5, 0],
    [0, 10, -1,  5,  1,  1,  5, -1, 10, 0],
    [0,-10,-20, -1, -1, -1, -1,-20,-10, 0],
    [0,100,-10, 10,  5,  5, 10,-10,100, 0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0, 0]
]

def quick_evaluate(board, color):
    """快速评估函数 - 只考虑位置权重和行动力"""
    score = 0
    my_moves = len(PossibleMove(color, board))
    opp_moves = len(PossibleMove(-color, board))
    
    # 位置分数
    for r in range(1, 9):
        for c in range(1, 9):
            if board[r][c] == color:
                score += POSITION_WEIGHTS[r][c]
            elif board[r][c] == -color:
                score -= POSITION_WEIGHTS[r][c]
    
    # 行动力差异（早期重要）
    score += (my_moves - opp_moves) * 3
    
    return score

def count_flips(board, color, r, c):
    """快速计算落子能翻转的棋子数"""
    if board[r][c] != 0:
        return 0
    
    total_flips = 0
    directions = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
    
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        flips = 0
        while ValidCell(nr, nc) and board[nr][nc] == -color:
            flips += 1
            nr += dr
            nc += dc
        if ValidCell(nr, nc) and board[nr][nc] == color and flips > 0:
            total_flips += flips
    
    return total_flips

def minimax_lite(board, color, depth, maximizing):
    """轻量级minimax搜索 - 最大深度2"""
    moves = PossibleMove(color, board)
    
    if depth == 0 or not moves:
        return quick_evaluate(board, color if maximizing else -color), None
    
    # 按翻转数排序（简单启发式）
    moves.sort(key=lambda m: count_flips(board, color, m[0], m[1]), reverse=True)
    
    best_move = moves[0]
    
    if maximizing:
        best_val = -999999
        for move in moves[:6]:  # 只考虑前6个候选
            new_board = BoardCopy(board)
            PlaceMove(color, new_board, move[0], move[1])
            val, _ = minimax_lite(new_board, -color, depth-1, False)
            if val > best_val:
                best_val = val
                best_move = move
        return best_val, best_move
    else:
        best_val = 999999
        for move in moves[:6]:  # 只考虑前6个候选
            new_board = BoardCopy(board)
            PlaceMove(color, new_board, move[0], move[1])
            val, _ = minimax_lite(new_board, -color, depth-1, True)
            if val < best_val:
                best_val = val
                best_move = move
        return best_val, best_move

def player(Colour, Board):
    """
    主函数入口 - 高速优化版本
    策略：位置权重 + 有限深度搜索 + 翻转最大化
    """
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)
    
    if len(moves) == 1:
        return moves[0]
    
    # 统计棋盘上的棋子数判断游戏阶段
    total_pieces = sum(row.count(1) + row.count(-1) for row in Board)
    
    # 开局和中局：使用简单启发式
    if total_pieces < 50:
        # 优先选择角落
        corner_moves = [(r, c) for r, c in moves if (r, c) in [(1,1), (1,8), (8,1), (8,8)]]
        if corner_moves:
            return corner_moves[0]
        
        # 按位置权重和翻转数评分
        best_move = moves[0]
        best_score = -999999
        
        for move in moves:
            r, c = move
            score = POSITION_WEIGHTS[r][c] * 2  # 位置分
            score += count_flips(Board, Colour, r, c) * 3  # 翻转分
            
            # 避开角落旁边的危险位置（如果角落空着）
            if (r, c) in [(1,2), (2,1), (2,2), (1,7), (2,7), (2,8), 
                         (7,1), (7,2), (8,2), (7,7), (7,8), (8,7)]:
                dangerous = False
                if r <= 2 and c <= 2 and Board[1][1] == 0:  # 左上角区域
                    dangerous = True
                elif r <= 2 and c >= 7 and Board[1][8] == 0:  # 右上角区域  
                    dangerous = True
                elif r >= 7 and c <= 2 and Board[8][1] == 0:  # 左下角区域
                    dangerous = True
                elif r >= 7 and c >= 7 and Board[8][8] == 0:  # 右下角区域
                    dangerous = True
                if dangerous:
                    score -= 50
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    # 残局：使用浅层搜索
    else:
        _, best_move = minimax_lite(Board, Colour, 2, True)
        return best_move if best_move else random.choice(moves)