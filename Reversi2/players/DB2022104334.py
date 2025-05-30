from Reversi import *
import copy
import random

# Simplified position weights
POSITION_WEIGHTS = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,  16,   3,   3,  16,  -2,  10],
    [  5,  -2,   3,   3,   3,   3,  -2,   5],
    [  5,  -2,   3,   3,   3,   3,  -2,   5],
    [ 10,  -2,  16,   3,   3,  16,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100]
]

def evaluate_board(board, color):
    """评估当前棋局状态的分值 """
    score = 0
    opponent = -color
    my_pieces = opp_pieces = 0
    position_score = corner_score = 0

    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == color:
                my_pieces += 1
                position_score += POSITION_WEIGHTS[x-1][y-1]
                if (x, y) in [(1,1),(1,8),(8,1),(8,8)]:
                    corner_score += 30
            elif board[x][y] == opponent:
                opp_pieces += 1
                position_score -= POSITION_WEIGHTS[x-1][y-1]
                if (x, y) in [(1,1),(1,8),(8,1),(8,8)]:
                    corner_score -= 30

    # 行动力评估
    my_moves = len(PossibleMove(color, board))
    opp_moves = len(PossibleMove(opponent, board))
    mobility_score = (my_moves - opp_moves) * 2

    total = my_pieces + opp_pieces
    # 根据游戏阶段调整权重
    if total > 50:  # 结束阶段：重视棋子数量、更深搜索
        piece_score = (my_pieces - opp_pieces) * 8
        score = piece_score + position_score + corner_score + mobility_score
    else:         # 中前期：重视位置和行动力
        piece_score = (my_pieces - opp_pieces) * 2
        score = piece_score + position_score * 2 + corner_score + mobility_score * 2

    return score


def minimax(board, depth, alpha, beta, maximizing, color):
    """带Alpha-Beta剪枝的Minimax算法"""
    if depth == 0:
        return evaluate_board(board, color), None

    current = color if maximizing else -color
    moves = PossibleMove(current, board)
    # 无棋可下：跳过到下一层
    if not moves:
        _, move = minimax(board, depth-1, alpha, beta, not maximizing, color)
        return _, move

    # 优先尝试角落、边缘
    def move_key(m):
        x, y = m
        if (x, y) in [(1,1),(1,8),(8,1),(8,8)]: return 0
        if x in (1,8) or y in (1,8):      return 1
        return 2
    moves.sort(key=move_key)

    best_move = moves[0]
    if maximizing:
        max_eval = -float('inf')
        for m in moves:
            newb = [row[:] for row in board]
            PlaceMove(current, newb, m[0], m[1])
            eval_v, _ = minimax(newb, depth-1, alpha, beta, False, color)
            if eval_v > max_eval:
                max_eval, best_move = eval_v, m
            alpha = max(alpha, eval_v)
            if alpha >= beta:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for m in moves:
            newb = [row[:] for row in board]
            PlaceMove(current, newb, m[0], m[1])
            eval_v, _ = minimax(newb, depth-1, alpha, beta, True, color)
            if eval_v < min_eval:
                min_eval, best_move = eval_v, m
            beta = min(beta, eval_v)
            if beta <= alpha:
                break
        return min_eval, best_move


def get_opening_move(board, color):
    """简化开局策略：优先内角和关键位置"""
    moves = PossibleMove(color, board)
    if not moves:
        return None
    order = [(3,3),(3,6),(6,3),(6,6), (4,3),(3,4),(5,6),(6,5)]
    for pos in order:
        if pos in moves:
            return pos
    return moves[0]


def player(color, board):
    """优化后的AI玩家主函数"""
    moves = PossibleMove(color, board)
    if not moves:
        return (0, 0)

    # 当前棋盘已有棋子数
    total_pieces = sum(r.count(1) + r.count(-1) for r in board)
    remaining = 64 - total_pieces

    # 开局阶段：使用开局策略
    if total_pieces <= 12:
        om = get_opening_move(board, color)
        if om and om in moves:
            return om

    # 动态调整搜索深度
    if remaining <= 8:
        depth = min(remaining, 6)
    elif total_pieces > 50:
        depth = 5
    else:
        depth = 3

    # 执行Minimax搜索
    _, best = minimax(board, depth, -float('inf'), float('inf'), True, color)

    # 安全检查：确保合法
    if best not in moves:
        best = random.choice(moves)
    return best

# 兼容接口
advanced_player = player
