# Module for Python course project V3.0 2025
# Corrected Smart Reversi player function

from Reversi import *
import random

# 定义棋盘位置价值
CORNER = 1000     # 角落位置价值最高
EDGE = 20         # 边缘位置价值
NEAR_CORNER = -50 # 靠近角落的位置危险

# 角落位置
corners = [(1,1), (1,8), (8,1), (8,8)]

# 靠近角落的危险位置
near_corners = [
    (1,2), (2,1), (2,2),  # 靠近(1,1)
    (1,7), (2,7), (2,8),  # 靠近(1,8)
    (7,1), (7,2), (8,2),  # 靠近(8,1)
    (7,7), (7,8), (8,7)   # 靠近(8,8)
]

# 边缘位置
edges = [(x,1) for x in range(2,8)] + [(x,8) for x in range(2,8)] + \
        [(1,y) for y in range(2,8)] + [(8,y) for y in range(2,8)]

def evaluate_move(Colour, Board, move):
    """评估一个移动的价值"""
    x, y = move
    value = 0
    flip_count = 0
    
    # 检查位置类型
    if (x,y) in corners:
        value += CORNER
    elif (x,y) in near_corners:
        value += NEAR_CORNER
    elif (x,y) in edges:
        value += EDGE
    
    # 计算翻转数量
    for i in range(8):
        dx, dy = NeighbourDirection[NeighbourDirection1[i]]
        nx, ny = x + dx, y + dy
        temp_flips = 0
        
        while ValidCell(nx, ny) and Board[nx][ny] == -Colour:
            temp_flips += 1
            nx += dx
            ny += dy
        
        if ValidCell(nx, ny) and Board[nx][ny] == Colour and temp_flips > 0:
            flip_count += temp_flips
            value += temp_flips * 2
    
    return value, flip_count

def count_pieces(Board):
    """计算棋盘上黑白棋子的数量"""
    black = white = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Black:
                black += 1
            elif Board[x][y] == White:
                white += 1
    return black, white

def player(Colour, Board):
    """智能Reversi玩家主函数"""
    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0)
    
    # 评估所有可能的移动
    evaluated_moves = []
    for move in possible_moves:
        value, flips = evaluate_move(Colour, Board, move)
        evaluated_moves.append((value, flips, move))
    
    # 游戏阶段判断
    black, white = count_pieces(Board)
    total_pieces = black + white
    game_phase = "early" if total_pieces < 20 else "late" if total_pieces > 50 else "mid"
    
    # 1. 总是优先选择角落
    corner_moves = [m for v, f, m in evaluated_moves if m in corners]
    if corner_moves:
        return random.choice(corner_moves)
    
    # 2. 游戏早期避免危险位置
    if game_phase == "early":
        safe_moves = [(v, f, m) for v, f, m in evaluated_moves 
                     if m not in near_corners or v > 0]
        if safe_moves:
            evaluated_moves = safe_moves
    
    # 3. 选择最佳移动
    if evaluated_moves:
        # 按价值排序
        evaluated_moves.sort(reverse=True)
        max_value = evaluated_moves[0][0]
        # 筛选价值最高的移动
        best_moves = [m for v, f, m in evaluated_moves if v == max_value]
        
        # 如果多个移动价值相同，选择翻转最多的
        if len(best_moves) > 1:
            max_flips = max(f for v, f, m in evaluated_moves if v == max_value)
            best_moves = [m for v, f, m in evaluated_moves 
                         if v == max_value and f == max_flips]
        
        return random.choice(best_moves)
    
    # 默认情况：随机选择
    return random.choice(possible_moves)