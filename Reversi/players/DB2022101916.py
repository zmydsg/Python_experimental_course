from Reversi import *
import random
import time

# --- 评估参数 ---
# 使用动态位置权重、边缘权重和稳定性检查
POSITION_WEIGHTS = [
    [100, -20, 30, 5, 5, 30, -20, 100],
    [-20, -50, -10, -5, -5, -10, -50, -20],
    [30, -10, 20, 3, 3, 20, -10, 30],
    [5, -5, 3, 1, 1, 3, -5, 5],
    [5, -5, 3, 1, 1, 3, -5, 5],
    [30, -10, 20, 3, 3, 20, -10, 30],
    [-20, -50, -10, -5, -5, -10, -50, -20],
    [100, -20, 30, 5, 5, 30, -20, 100]
]

CORNERS = [(1, 1), (1, 8), (8, 1), (8, 8)]
DANGER_ZONE = {(2, 2), (2, 7), (7, 2), (7, 7), (1, 2), (2, 1), (1, 7), (2, 8), (7, 1), (8, 2), (7, 8), (8, 7)}

def count_flips(Colour, Board, x, y):
    """估计翻转的棋子数量"""
    flip_count = 0
    for direction in NeighbourDirection1:
        dx, dy = NeighbourDirection[direction]
        tx, ty = x + dx, y + dy
        temp_flips = 0
        while ValidCell(tx, ty) and Board[tx][ty] == -Colour:
            temp_flips += 1
            tx += dx
            ty += dy
        if ValidCell(tx, ty) and Board[tx][ty] == Colour:
            flip_count += temp_flips
    return flip_count

def evaluate_board(Colour, Board):
    """基于棋子数量、行动力、稳定性和位置评估棋盘"""
    score = 0
    my_pieces = sum(row.count(Colour) for row in Board)
    opp_pieces = sum(row.count(-Colour) for row in Board)
    empty_cells = sum(row.count(0) for row in Board)

    # 根据棋子数量打分
    score += (my_pieces - opp_pieces) * 10

    # 根据行动力打分（可行动数越多越好）
    my_moves = len(PossibleMove(Colour, Board))
    opp_moves = len(PossibleMove(-Colour, Board))
    score += (my_moves - opp_moves) * 20

    # 根据稳定性打分（难以被翻转的棋子更好）
    stability_weight = 0
    for r in range(1, 9):
        for c in range(1, 9):
            if Board[r][c] == Colour:
                if (r, c) in CORNERS:
                    stability_weight += 100
                elif r == 1 or r == 8 or c == 1 or c == 8:
                    stability_weight += 30
    score += stability_weight

    # 根据位置打分（优先战略位置）
    for r in range(1, 9):
        for c in range(1, 9):
            if Board[r][c] == Colour:
                score += POSITION_WEIGHTS[r-1][c-1]
    
    return score

def player(Colour, Board):
    """主玩家函数，结合所有策略"""
    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0)

    # 优先选择角落位置
    corner_moves = [move for move in possible_moves if move in CORNERS]
    if corner_moves:
        return random.choice(corner_moves)

    # 避免危险区域
    safe_moves = [move for move in possible_moves if move not in DANGER_ZONE]
    if safe_moves:
        possible_moves = safe_moves

    # 根据位置、翻转数和对手行动评估每一步
    best_score = -float('inf')
    best_move = None
    for move in possible_moves:
        temp_board = BoardCopy(Board)
        PlaceMove(Colour, temp_board, move[0], move[1])
        flips = count_flips(Colour, Board, move[0], move[1])
        move_score = evaluate_board(Colour, temp_board) + flips * 0.5
        
        if move_score > best_score:
            best_score = move_score
            best_move = move

    return best_move if best_move else random.choice(possible_moves)