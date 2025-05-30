from Reversi import PossibleMove
import random

# 八个方向偏移 (dx, dy)
DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

# 位置权重矩阵
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

# 应用走法并返回被翻转的棋子列表
def apply_move(board, color, x, y):
    flips = []
    opponent = -color
    for dx, dy in DIRECTIONS:
        path = []
        cx, cy = x + dx, y + dy
        while 1 <= cx <= 8 and 1 <= cy <= 8 and board[cx][cy] == opponent:
            path.append((cx, cy))
            cx += dx; cy += dy
        if 1 <= cx <= 8 and 1 <= cy <= 8 and board[cx][cy] == color and path:
            flips.extend(path)
    board[x][y] = color
    for fx, fy in flips:
        board[fx][fy] = color
    return flips

# 撤销走法
def undo_move(board, color, x, y, flips):
    board[x][y] = 0
    for fx, fy in flips:
        board[fx][fy] = -color

# 评估函数
def evaluate_board(board, color):
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
    my_moves = len(PossibleMove(color, board))
    opp_moves = len(PossibleMove(opponent, board))
    mobility_score = (my_moves - opp_moves) * 2
    total = my_pieces + opp_pieces
    diff = my_pieces - opp_pieces
    if total > 50:
        return diff*8 + position_score + corner_score + mobility_score
    else:
        return diff*2 + position_score*2 + corner_score + mobility_score*2

# Minimax + α–β 剪枝（就地修改 + 撤销）
def minimax(board, depth, alpha, beta, maximizing, color):
    if depth == 0:
        return evaluate_board(board, color), None
    current = color if maximizing else -color
    moves = PossibleMove(current, board)
    if not moves:
        val, _ = minimax(board, depth-1, alpha, beta, not maximizing, color)
        return val, None
    # 按角落、边缘、其他排序
    def move_key(m):
        x, y = m
        if (x, y) in [(1,1),(1,8),(8,1),(8,8)]: return 0
        if x in (1,8) or y in (1,8):      return 1
        return 2
    moves.sort(key=move_key)
    best_move = moves[0]
    if maximizing:
        max_eval = -float('inf')
        for x, y in moves:
            flips = apply_move(board, current, x, y)
            eval_v, _ = minimax(board, depth-1, alpha, beta, False, color)
            undo_move(board, current, x, y, flips)
            if eval_v > max_eval:
                max_eval, best_move = eval_v, (x, y)
            alpha = max(alpha, eval_v)
            if alpha >= beta:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for x, y in moves:
            flips = apply_move(board, current, x, y)
            eval_v, _ = minimax(board, depth-1, alpha, beta, True, color)
            undo_move(board, current, x, y, flips)
            if eval_v < min_eval:
                min_eval, best_move = eval_v, (x, y)
            beta = min(beta, eval_v)
            if beta <= alpha:
                break
        return min_eval, best_move

# 简易开局策略
def get_opening_move(board, color):
    moves = PossibleMove(color, board)
    order = [(3,3),(3,6),(6,3),(6,6),(4,3),(3,4),(5,6),(6,5)]
    for pos in order:
        if pos in moves:
            return pos
    return moves[0] if moves else None

# AI 主函数
def player(color, board):
    moves = PossibleMove(color, board)
    if not moves:
        return (0, 0)
    # 计算阶段
    total = sum(r.count(1)+r.count(-1) for r in board)
    if total <= 12:
        om = get_opening_move(board, color)
        if om: return om
    rem = 64 - total
    if rem <= 8:
        depth = rem
    elif total > 50:
        depth = 5
    else:
        depth = 3
    _, best = minimax(board, depth, -float('inf'), float('inf'), True, color)
    if best not in moves:
        best = random.choice(moves)
    return best

# 兼容接口
advanced_player = player
