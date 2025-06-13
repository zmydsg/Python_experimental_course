
import Reversi
import time
import functools

# 位置价值矩阵（保留或升级为多因素评估）
weight_matrix = [
    [120, -20, 20, 5, 5, 20, -20, 120],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [120, -20, 20, 5, 5, 20, -20, 120]
]

# 缓存位置估值
@functools.lru_cache(maxsize=None)
def evaluate_move(x, y):
    return weight_matrix[x-1][y-1]

# 改进的静态评估，包括潜在块和稳定块
def static_evaluate(Board, Color):
    my_pieces = 0
    opp_pieces = 0
    my_stable = 0
    opp_stable = 0
    mobility = len(Reversi.PossibleMove(Color, Board))
    opp_moves = len(Reversi.PossibleMove(-Color, Board))
    positional_score = 0

    # 位置价值与稳定块评估
    for x in range(1, 9):
        for y in range(1, 9):
            cell = Board[x][y]
            if cell == Color:
                my_pieces +=1
                positional_score += evaluate_move(x, y)
                # 判断稳定块（边角的策略）
            elif cell == -Color:
                opp_pieces +=1
                positional_score -= evaluate_move(x, y)
    # 角落控制积分
    corners = [(1,1),(1,8),(8,1),(8,8)]
    stable_bonus = 0
    for cx, cy in corners:
        if Board[cx][cy] == Color:
            stable_bonus += 50
        elif Board[cx][cy] == -Color:
            stable_bonus -= 50

    # 综合评分
    piece_diff = 100 * (my_pieces - opp_pieces) / max(1, my_pieces + opp_pieces)
    mobility_score = 10 * (len(Reversi.PossibleMove(Color, Board)) - opp_moves) / max(1, opp_moves + len(Reversi.PossibleMove(-Color, Board)))
    score = (positional_score * 1.2) + piece_diff + mobility_score + stable_bonus

    return score

# Move排序优先考虑角落和边界优先
def move_sort(moves, Board, Color):
    def move_score(move):
        x, y = move
        score = evaluate_move(x, y)
        # 增加角落优先级
        if (x, y) in [(1,1),(1,8),(8,1),(8,8)]:
            score += 1000
        # 边缘优先
        elif x == 1 or x == 8 or y == 1 or y == 8:
            score += 100
        return score

    return sorted(moves, key=move_score, reverse=True)
# 翻转函数
def flip(board, x, y, color):
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),           (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]
    flips = []
    for dx, dy in directions:
        temp = []
        nx, ny = x + dx, y + dy
        while Reversi.ValidCell(nx, ny) and board[nx][ny] == -color:
            temp.append((nx, ny))
            nx += dx
            ny += dy
        if Reversi.ValidCell(nx, ny) and board[nx][ny] == color:
            flips.extend(temp)
    return flips
# 主搜索：带转置表、深度限定、多变参数调整
transposition_table = {}

def alpha_beta(Board, Color, depth, alpha, beta, start_time, time_limit):
    current_time = time.time()
    if current_time - start_time > time_limit:
        return static_evaluate(Board, Color)

    # 转置表查找
    board_key = tuple(map(tuple, Board))
    if board_key in transposition_table:
        entry = transposition_table[board_key]
        if entry['depth'] >= depth:
            if entry['flag'] == 'exact':
                return entry['value']
            elif entry['flag'] == 'lowerbound':
                alpha = max(alpha, entry['value'])
            elif entry['flag'] == 'upperbound':
                beta = min(beta, entry['value'])
            if alpha >= beta:
                return entry['value']

    moves = Reversi.PossibleMove(Color, Board)
    if depth == 0 or not moves:
        val = static_evaluate(Board, Color)
        transposition_table[board_key] = {'value': val, 'depth': depth, 'flag': 'exact'}
        return val

    moves = move_sort(moves, Board, Color)
    value = -float('inf')

    for move in moves:
        x, y = move
        nb = [row[:] for row in Board]
        nb[x][y] = Color
        for fx, fy in flip(nb, x, y, Color):
            nb[fx][fy] = Color

        score = -alpha_beta(nb, -Color, depth - 1, -beta, -alpha, start_time, time_limit)

        if score > value:
            value = score
        if value > alpha:
            alpha = value
        if alpha >= beta:
            break

    # 记录转置表
    # 这里可以根据当前搜索的结果设置标志
    if value <= alpha:
        flag = 'upperbound'
    elif value >= beta:
        flag = 'lowerbound'
    else:
        flag = 'exact'
    transposition_table[board_key] = {'value': value, 'depth': depth, 'flag': flag}
    return value

def player(Col, Board):
    start_time = time.time()

    # 直接抢角
    for corner in [(1,1),(1,8),(8,1),(8,8)]:
        if corner in Reversi.PossibleMove(Col, Board):
            return corner

    total_pieces = sum(row.count(1)+row.count(-1) for row in Board)
    if total_pieces < 20:
        max_depth = 5
        time_limit = 0.3
    elif total_pieces < 50:
        max_depth = 6
        time_limit = 0.5
    else:
        max_depth = 7
        time_limit = 1.0

    best_move = None
    best_score = -float('inf')

    # 尝试逐层递增搜索深度，利用时间
    for depth in range(1, max_depth + 1):
        current_best = None
        current_best_score = -float('inf')
        for move in Reversi.PossibleMove(Col, Board):
            x, y = move
            nb = [row[:] for row in Board]
            nb[x][y] = Col
            for fx, fy in flip(nb, x, y, Col):
                nb[fx][fy] = Col
            score = -alpha_beta(nb, -Col, depth - 1, -float('inf'), -float('inf'), start_time, time_limit)
            if score > current_best_score:
                current_best_score = score
                current_best = move
        if current_best_score > best_score:
            best_score = current_best_score
            best_move = current_best
        # 时间提前结束
        if time.time() - start_time > time_limit:
            break

    return best_move if best_move else Reversi.PossibleMove(Col, Board)[0]
