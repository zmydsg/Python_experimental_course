from Reversi import *
import math
import time

# 位置权重矩阵
WEIGHTS = [
    [100, -20, 10, 5, 5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [10, -2, -1, -1, -1, -1, -2, 10],
    [5, -2, -1, -1, -1, -1, -2, 5],
    [5, -2, -1, -1, -1, -1, -2, 5],
    [10, -2, -1, -1, -1, -1, -2, 10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10, 5, 5, 10, -20, 100],
]


# 行动力（可行走步数差）
def mobility(Board, Colour):
    my_moves = len(PossibleMove(Colour, Board))
    opp_moves = len(PossibleMove(-Colour, Board))
    return 100 * (my_moves - opp_moves) / (my_moves + opp_moves + 1)


evaluate_cache: dict = {}


# 棋盘评分函数：位置价值 + 行动力
def evaluate(Board, Colour):
    # 计算棋盘哈希
    board_hash = 0
    for x in range(1, 9):
        for y in range(1, 9):
            board_hash = board_hash * 3 + (Board[x][y] + 1)  # 0/1/-1 映射为 1/2/0
    key = (board_hash, Colour)
    if key in evaluate_cache:
        return evaluate_cache[key]

    position_score = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Colour:
                position_score += WEIGHTS[x - 1][y - 1]
            elif Board[x][y] == -Colour:
                position_score -= WEIGHTS[x - 1][y - 1]

    mobility_score = mobility(Board, Colour)
    result = position_score + mobility_score
    evaluate_cache[key] = result
    return result


# 启发式排序走法
def sorted_moves(moves, Colour, Board):
    return sorted(moves, key=lambda m: WEIGHTS[m[0] - 1][m[1] - 1], reverse=True)


# α-β剪枝搜索
def minimax(Board, depth, maximizingPlayer, Colour, alpha, beta):
    current_player = Colour if maximizingPlayer else -Colour
    possible_moves = PossibleMove(current_player, Board)
    if depth == 0 or not possible_moves:
        return evaluate(Board, Colour), None

    best_move = None
    ordered_moves = sorted_moves(possible_moves, current_player, Board)

    if maximizingPlayer:
        max_eval = -math.inf
        for move in ordered_moves:
            new_board = BoardCopy(Board)
            PlaceMove(current_player, new_board, move[0], move[1])
            eval, _ = minimax(new_board, depth - 1, False, Colour, alpha, beta)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in ordered_moves:
            new_board = BoardCopy(Board)
            PlaceMove(current_player, new_board, move[0], move[1])
            eval, _ = minimax(new_board, depth - 1, True, Colour, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move


# 主函数：动态控制搜索深度，控制用时
def player(Colour, Board):
    possible = PossibleMove(Colour, Board)
    if not possible:
        return (0, 0)

    total_pieces = sum(row.count(1) + row.count(-1) for row in Board)
    # 根据盘面进度决定搜索深度
    if total_pieces <= 20:
        depth = 3
    elif total_pieces <= 50:
        depth = 3
    else:
        depth = 4  # 后期提升深度但保持效率

    start_time = time.time()
    _, best_move = minimax(
        Board,
        depth,
        maximizingPlayer=True,
        Colour=Colour,
        alpha=-math.inf,
        beta=math.inf,
    )
    end_time = time.time()
#   print(f"[INFO] Move calculated in {(end_time - start_time)*1000:.2f} ms")

    return best_move
