from Reversi import PossibleMove, ValidCell
import random

# 八个方向偏移 (dx, dy)
DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

# 静态阶段权重表（含边框填充）
STAGE_WEIGHTS = {
    'opening': [
        [0]*10,
        [0,120,-180,8,8,8,8,-180,120,0],
        [0,-180,-250,-5,-5,-5,-5,-250,-180,0],
        [0,8,-5,5,3,3,5,-5,8,0],
        [0,8,-5,3,0,0,3,-5,8,0],
        [0,8,-5,3,0,0,3,-5,8,0],
        [0,8,-5,5,3,3,5,-5,8,0],
        [0,-180,-250,-5,-5,-5,-5,-250,-180,0],
        [0,120,-180,8,8,8,8,-180,120,0],
        [0]*10
    ],
    'midgame': [
        [0]*10,
        [0,100,-80,12,12,12,12,-80,100,0],
        [0,-80,-120,-5,-5,-5,-5,-120,-80,0],
        [0,12,-5,10,8,8,10,-5,12,0],
        [0,12,-5,8,5,5,8,-5,12,0],
        [0,12,-5,8,5,5,8,-5,12,0],
        [0,12,-5,10,8,8,10,-5,12,0],
        [0,-80,-120,-5,-5,-5,-5,-120,-80,0],
        [0,100,-80,12,12,12,12,-80,100,0],
        [0]*10
    ],
    'endgame': [
        [0]*10,
        [0,100,-50,5,5,5,5,-50,100,0],
        [0,-50,-80,-3,-3,-3,-3,-80,-50,0],
        [0,5,-3,5,3,3,5,-3,5,0],
        [0,5,-3,3,0,0,3,-3,5,0],
        [0,5,-3,3,0,0,3,-3,5,0],
        [0,5,-3,5,3,3,5,-3,5,0],
        [0,-50,-80,-3,-3,-3,-3,-80,-50,0],
        [0,100,-50,5,5,5,5,-50,100,0],
        [0]*10
    ]
}

# 应用走法并返回被翻转的棋子列表
def apply_move(board, color, x, y):
    flips = []
    opponent = -color
    for dx, dy in DIRECTIONS:
        path = []
        cx, cy = x + dx, y + dy
        while ValidCell(cx, cy) and board[cx][cy] == opponent:
            path.append((cx, cy))
            cx += dx; cy += dy
        if ValidCell(cx, cy) and board[cx][cy] == color and path:
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

# 计算稳定子数量
def count_stable_discs(board, color):
    stable = 0
    for x in range(1,9):
        for y in range(1,9):
            if board[x][y] != color: continue
            is_stable = False
            for dx, dy in DIRECTIONS:
                cx, cy = x + dx, y + dy
                blocked = False
                while ValidCell(cx, cy):
                    if board[cx][cy] == -color:
                        break
                    if board[cx][cy] == color or not ValidCell(cx, cy):
                        blocked = True; break
                    cx += dx; cy += dy
                if blocked:
                    is_stable = True; break
            if is_stable: stable += 1
    return stable

# 边缘连续性奖励
def edge_continuity_bonus(board, color, x, y):
    bonus = 0
    if x in [1,8]:
        for dy in (-1,1):
            if ValidCell(x, y+dy) and board[x][y+dy] == color:
                bonus += 5
    if y in [1,8]:
        for dx in (-1,1):
            if ValidCell(x+dx, y) and board[x+dx][y] == color:
                bonus += 5
    return bonus

# 获取当前阶段权重
def get_stage(board):
    total = sum(r.count(1) + r.count(-1) for r in board)
    if total <= 16: return 'opening'
    if total <= 48: return 'midgame'
    return 'endgame'

# 评估函数
def evaluate_board(board, color):
    stage = get_stage(board)
    weights = STAGE_WEIGHTS[stage]
    opponent = -color
    score = 0
    # 基础位置分
    for x in range(1,9):
        for y in range(1,9):
            if board[x][y] == color:
                score += weights[x][y]
            elif board[x][y] == opponent:
                score -= weights[x][y]
    # 稳定子
    stable_gain = count_stable_discs(board, color) - count_stable_discs(board, opponent)
    score += stable_gain * (5 if stage!='endgame' else 2)
    return score

# Minimax + α–β 剪枝（就地修改+撤销+排序）
def minimax(board, depth, alpha, beta, maximizing, color):
    if depth == 0:
        return evaluate_board(board, color), None
    current = color if maximizing else -color
    moves = PossibleMove(current, board)
    if not moves:
        val, _ = minimax(board, depth-1, alpha, beta, not maximizing, color)
        return val, None
    # 排序：角落首选，危险区最末
    danger = {(1,2),(2,1),(2,2),(1,7),(2,7),(2,8),(7,1),(7,2),(8,2),(7,7),(7,8),(8,7)}
    def key(m):
        return (0 if m in [(1,1),(1,8),(8,1),(8,8)] else
                2 if m in danger else
                1)
    moves.sort(key=key)
    best_move = moves[0]
    if maximizing:
        max_eval = -1e9
        for x,y in moves:
            flips = apply_move(board, current, x, y)
            val, _ = minimax(board, depth-1, alpha, beta, False, color)
            undo_move(board, current, x, y, flips)
            if val > max_eval:
                max_eval, best_move = val, (x,y)
            alpha = max(alpha, val)
            if alpha >= beta: break
        return max_eval, best_move
    else:
        min_eval = 1e9
        for x,y in moves:
            flips = apply_move(board, current, x, y)
            val, _ = minimax(board, depth-1, alpha, beta, True, color)
            undo_move(board, current, x, y, flips)
            val = val
            if val < min_eval:
                min_eval, best_move = val, (x,y)
            beta = min(beta, val)
            if beta <= alpha: break
        return min_eval, best_move

# AI 主函数
def player(color, board):
    moves = PossibleMove(color, board)
    if not moves: return (0,0)
    # 角落抢占
    for c in [(1,1),(1,8),(8,1),(8,8)]:
        if c in moves: return c
    # 动态深度
    total = sum(r.count(1)+r.count(-1) for r in board)
    rem = 64 - total
    depth = rem if rem<=8 else 5 if total>50 else 3
    _, best = minimax(board, depth, -1e9, 1e9, True, color)
    if best not in moves:
        best = random.choice(moves)
    return best

# 兼容接口
advanced_player = player
