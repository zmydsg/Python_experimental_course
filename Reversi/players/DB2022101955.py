from Reversi import *
from copy import deepcopy
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

WEIGHTS = [
    [0]*10,
    [0, 500, -75,  30,  15,  15,  30, -75, 500, 0],
    [0, -75,-150, -10, -10, -10, -10,-150, -75, 0],
    [0,  30, -10,  20,   5,   5,  20, -10,  30, 0],
    [0,  15, -10,   5,   3,   3,   5, -10,  15, 0],
    [0,  15, -10,   5,   3,   3,   5, -10,  15, 0],
    [0,  30, -10,  20,   5,   5,  20, -10,  30, 0],
    [0, -75,-150, -10, -10, -10, -10,-150, -75, 0],
    [0, 500, -75,  30,  15,  15,  30, -75, 500, 0],
    [0]*10
]

OPENING_BOOK = {
    ((0,)*10,)*4 + (
        (0,0,0,0,0,0,0,0,0,0),
        (0,0,0,0,0,2,1,0,0,0),
        (0,0,0,0,0,1,2,0,0,0),
        (0,0,0,0,0,0,0,0,0,0),
    ) + ((0,)*10,)*2: (5, 4)
}

TT_CACHE = {}

def clone_board(Board):
    return [row[:] for row in Board]

def is_stable(Board, x, y):
    for dx, dy in [(1,0),(0,1),(-1,0),(0,-1)]:
        nx, ny = x+dx, y+dy
        if ValidCell(nx,ny) and Board[nx][ny] == 0:
            return False
    return True

def evaluate_board(Colour, Board):
    key = tuple(tuple(row) for row in Board)
    if key in TT_CACHE:
        return TT_CACHE[key]

    score = mobility = corner = stable = 0
    corners = [(1,1),(1,8),(8,1),(8,8)]
    
    for x in range(1,9):
        for y in range(1,9):
            val = Board[x][y]
            if val != 0:
                weight = WEIGHTS[x][y]
                if val == Colour:
                    score += weight
                    if x in (1,8) or y in (1,8):
                        stable += 10 if is_stable(Board, x, y) else 5
                else:
                    score -= weight

    my_moves = len(PossibleMove(Colour, Board))
    opp_moves = len(PossibleMove(-Colour, Board))
    mobility = 15 * (my_moves - opp_moves)
    
    for x, y in corners:
        if Board[x][y] == Colour: corner += 100
        elif Board[x][y] == -Colour: corner -= 100

    result = score + mobility + corner + stable
    TT_CACHE[key] = result
    return result

def sort_moves(Colour, Board, moves):
    return sorted(
        moves,
        key=lambda m: (
            WEIGHTS[m[0]][m[1]],
            count_flips(Colour, Board, *m),
            -abs(m[0]-4.5) - abs(m[1]-4.5)
        ),
        reverse=True
    )

def minimax(Colour, Board, depth, alpha, beta, maximizing, start_time, time_limit):
    if time.time() - start_time > time_limit:
        raise TimeoutError

    moves = PossibleMove(Colour, Board)
    if depth == 0 or not moves:
        return evaluate_board(Colour if maximizing else -Colour, Board), None

    best_move = None
    sorted_moves = sort_moves(Colour, Board, moves)

    if maximizing:
        max_eval = -math.inf
        for move in sorted_moves:
            new_board = clone_board(Board)
            PlaceMove(Colour, new_board, *move)
            try:
                eval, _ = minimax(-Colour, new_board, depth-1, alpha, beta, False, start_time, time_limit)
                if eval > max_eval:
                    max_eval, best_move = eval, move
                alpha = max(alpha, eval)
                if beta <= alpha: break
            except TimeoutError:
                raise
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in sorted_moves:
            new_board = clone_board(Board)
            PlaceMove(Colour, new_board, *move)
            try:
                eval, _ = minimax(-Colour, new_board, depth-1, alpha, beta, True, start_time, time_limit)
                if eval < min_eval:
                    min_eval, best_move = eval, move
                beta = min(beta, eval)
                if beta <= alpha: break
            except TimeoutError:
                raise
        return min_eval, best_move

def count_flips(Colour, Board, x, y):
    total = 0
    for dx, dy in NeighbourDirection.values():
        nx, ny = x + dx, y + dy
        count = 0
        while ValidCell(nx, ny) and Board[nx][ny] == -Colour:
            count += 1
            nx += dx
            ny += dy
        if ValidCell(nx, ny) and Board[nx][ny] == Colour:
            total += count
    return total

def get_best_heuristic_move(Colour, Board):
    moves = PossibleMove(Colour, Board)
    corners = [(1,1),(1,8),(8,1),(8,8)]
    for x,y in corners:
        if (x,y) in moves and Board[x][y] == 0:
            return (x,y)
    return max(moves, key=lambda m: WEIGHTS[m[0]][m[1]])

def evaluate_move(Colour, Board, move, depth, start_time, time_limit):
    if time.time() - start_time > time_limit:
        raise TimeoutError
    new_board = clone_board(Board)
    PlaceMove(Colour, new_board, *move)
    remaining_moves = 60 - sum(cell != 0 for row in Board for cell in row)
    final_depth = max(depth, 4 if remaining_moves < 15 else depth)
    score, _ = minimax(
        -Colour, new_board, final_depth-1,
        -math.inf, math.inf, False,
        start_time, time_limit
    )
    return score

def player(Colour, Board, time_limit=0.5):
    start_time = time.time()
    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0)
    
    board_key = tuple(tuple(row) for row in Board)
    if board_key in OPENING_BOOK:
        return OPENING_BOOK[board_key]
    
    move_count = sum(cell != 0 for row in Board for cell in row)
    if move_count < 12:
        return get_best_heuristic_move(Colour, Board)

    best_move = None
    best_score = -math.inf

    for depth in range(3, 6):
        try:
            if depth >= 5:
                with ThreadPoolExecutor() as executor:
                    futures = {
                        executor.submit(
                            evaluate_move, Colour, Board, move, depth, start_time, time_limit*0.8
                        ): move for move in possible_moves
                    }
                    for future in as_completed(futures):
                        if time.time() - start_time > time_limit*0.8:
                            raise TimeoutError
                        move = futures[future]
                        try:
                            score = future.result()
                            if score > best_score:
                                best_score = score
                                best_move = move
                        except TimeoutError:
                            continue
            else:
                for move in possible_moves:
                    score = evaluate_move(Colour, Board, move, depth, start_time, time_limit*0.8)
                    if score > best_score:
                        best_score = score
                        best_move = move
        except TimeoutError:
            break

    if best_move is None:
        best_move = max(possible_moves, key=lambda m: count_flips(Colour, Board, *m))
    return best_move
