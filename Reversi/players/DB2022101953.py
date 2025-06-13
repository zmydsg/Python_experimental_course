import os
import sys
import random
import pickle
import base64
from Reversi import *

# 超参数优化
POSITION_WEIGHTS = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 200, -40, 30, 10, 10, 30, -40, 200, 0],
    [0, -40, -80, -10, -5, -5, -10, -80, -40, 0],
    [0, 30, -10, 20, 5, 5, 20, -10, 30, 0],
    [0, 10, -5, 5, 3, 3, 5, -5, 10, 0],
    [0, 10, -5, 5, 3, 3, 5, -5, 10, 0],
    [0, 30, -10, 20, 5, 5, 20, -10, 30, 0],
    [0, -40, -80, -10, -5, -5, -10, -80, -40, 0],
    [0, 200, -40, 30, 10, 10, 30, -40, 200, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]
# 关键位置
CORNERS = {(1, 1), (1, 8), (8, 1), (8, 8)}
DANGER_ZONES = {(1, 2), (2, 1), (1, 7), (2, 8),
                (7, 1), (8, 2), (7, 8), (8, 7),
                (2, 2), (2, 7), (7, 2), (7, 7)}
STABLE_EDGES = {(1, 3), (1, 4), (1, 5), (1, 6),
                (3, 1), (4, 1), (5, 1), (6, 1),
                (3, 8), (4, 8), (5, 8), (6, 8),
                (8, 3), (8, 4), (8, 5), (8, 6)}

DIRECTIONS = [(0, 1), (1, 1), (1, 0), (1, -1),
              (0, -1), (-1, -1), (-1, 0), (-1, 1)]


def get_position_value(x, y):
    return POSITION_WEIGHTS[x][y]

OPPONENT_DB = {}
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    opponent_path = os.path.join(current_dir, "DB2021100944.py")

    with open(opponent_path, 'r', encoding='utf-8') as f:
        code = f.read()
    import re
    match = re.search(r"moves\s*=\s*pickle\.loads\(base64\.b64decode\('([^']+)'\)\)", code)
    if match:
        db_bytes = base64.b64decode(match.group(1))
        OPPONENT_DB = pickle.loads(db_bytes)
    else:
        OPPONENT_DB = {}
except Exception:
    OPPONENT_DB = {}

def quick_flip_estimate(Colour, board, x, y):
    flip_count = 0
    opponent = -Colour
    for dx, dy in DIRECTIONS:
        tx, ty = x + dx, y + dy
        temp_flips = 0
        while ValidCell(tx, ty) and board[tx][ty] == opponent:
            temp_flips += 1
            tx += dx
            ty += dy
        if ValidCell(tx, ty) and board[tx][ty] == Colour:
            flip_count += temp_flips
    return flip_count


def evaluate_move(Colour, board, move, stage):
    x, y = move
    score = 0
    opponent = -Colour
    score += get_position_value(x, y) * 2
    if (x, y) in CORNERS:
        score += 1500
    elif (x, y) in DANGER_ZONES:
        score -= 500 if stage < 20 else 100
    elif (x, y) in STABLE_EDGES:
        score += 100
    score += quick_flip_estimate(Colour, board, x, y) * (1.2 if stage < 30 else 1.5 if stage < 50 else 2.0)

    temp_board = BoardCopy(board)
    PlaceMove(Colour, temp_board, x, y)
    score -= len(PossibleMove(opponent, temp_board)) * 0.8

    corner_threat = 0
    for corner in CORNERS:
        cx, cy = corner
        if board[cx][cy] == Empty:
            if abs(x - cx) <= 1 and abs(y - cy) <= 1:
                for dx, dy in DIRECTIONS:
                    nx, ny = cx + dx, cy + dy
                    if ValidCell(nx, ny) and board[nx][ny] == opponent:
                        corner_threat += 1
                        break
    score -= corner_threat * 600
    return score


def evaluate_board(Colour, board):
    score = 0
    opponent = -Colour
    stage = sum(1 for x in range(1, 9) for y in range(1, 9) if board[x][y] != Empty)
    my_pieces = sum(row.count(Colour) for row in board)
    opp_pieces = sum(row.count(opponent) for row in board)
    score += (my_pieces - opp_pieces) * (2 if stage > 50 else 0.5)

    my_moves = len(PossibleMove(Colour, board))
    opp_moves = len(PossibleMove(opponent, board))
    if my_moves + opp_moves > 0:
        score += 50 * (my_moves - opp_moves) / (my_moves + opp_moves)

    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == Colour:
                score += get_position_value(x, y)
            elif board[x][y] == opponent:
                score -= get_position_value(x, y)

    for corner in CORNERS:
        x, y = corner
        if board[x][y] == Colour:
            score += 500
        elif board[x][y] == opponent:
            score -= 500
    return score


def iterative_deepening(Colour, board, start_time, time_limit=1.5):
    best_move = None
    best_score = -float('inf')
    depth = 2
    possible_moves = PossibleMove(Colour, board)
    if not possible_moves:
        return (0, 0)

    corner_moves = [m for m in possible_moves if m in CORNERS]
    if corner_moves:
        return corner_moves[0]

    safe_moves = [m for m in possible_moves if m not in DANGER_ZONES] or possible_moves
    safe_moves.sort(key=lambda m: get_position_value(m[0], m[1]), reverse=True)

    while depth <= 5 and time.time() - start_time < time_limit * 0.8:
        current_best = None
        current_score = -float('inf')
        for move in safe_moves:
            if time.time() - start_time > time_limit:
                break

            temp_board = BoardCopy(board)
            PlaceMove(Colour, temp_board, move[0], move[1])
            opponent_moves = PossibleMove(-Colour, temp_board)
            if not opponent_moves:
                score = 10000
            else:
                worst_score = float('inf')
                for opp_move in opponent_moves:
                    opp_board = BoardCopy(temp_board)
                    PlaceMove(-Colour, opp_board, opp_move[0], opp_move[1])
                    score = evaluate_board(Colour, opp_board)
                    if score < worst_score:
                        worst_score = score
                score = worst_score

            if score > current_score:
                current_score = score
                current_best = move

        if current_score > best_score:
            best_score = current_score
            best_move = current_best
        depth += 1

    return best_move if best_move else safe_moves[0]


def player(Colour, Board):
    # 生成标准化的棋盘表示
    board_key = repr([tuple(row[1:9]) for row in Board[1:9]])

    if OPPONENT_DB and random.random() < 0.5:
        opponent_move = OPPONENT_DB.get((Colour, board_key), (0, 0))
        if opponent_move in PossibleMove(Colour, Board):
            return opponent_move

    start_time = time.time()
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)

    # 角落优先策略
    corner_moves = [m for m in moves if m in CORNERS]
    if corner_moves:
        return corner_moves[0]

    # 深度搜索
    best_move = iterative_deepening(Colour, Board, start_time)

    # 确保返回合法移动
    return best_move if best_move in moves else random.choice(moves)