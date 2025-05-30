from Reversi import PossibleMove, BoardCopy, PlaceMove, Empty, NeighbourPosition
import random

# 八个方向偏移 (dx, dy)
DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

# 原位置权重矩阵
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

# 危险区（角落相邻及边缘邻近）
DANGER_ZONES = {
    (1,2),(2,1),(2,2),(1,7),(2,7),(2,8),(7,1),(7,2),(8,2),(7,7),(7,8),(8,7)
}

# 角落
CORNERS = {(1,1),(1,8),(8,1),(8,8)}

# 应用走法并返回翻转列表
def apply_move_and_get_flips(board, color, x, y):
    flips = []
    opp = -color
    for dx, dy in DIRECTIONS:
        path = []
        cx, cy = x+dx, y+dy
        while 1 <= cx <= 8 and 1 <= cy <= 8 and board[cx][cy] == opp:
            path.append((cx, cy))
            cx += dx; cy += dy
        if 1 <= cx <= 8 and 1 <= cy <= 8 and board[cx][cy] == color and path:
            flips.extend(path)
    # 放置并翻转
    board[x][y] = color
    for fx, fy in flips:
        board[fx][fy] = color
    return flips

# 撤销走法
def undo_move(board, color, x, y, flips):
    board[x][y] = Empty
    for fx, fy in flips:
        board[fx][fy] = -color

# 综合评估函数：位置权重 + 翻转收益 + 行动力 + 边缘连通性
def evaluate_move(board, color, move):
    x, y = move
    score = 0
    # 基础位置权重
    score += POSITION_WEIGHTS[x-1][y-1]
    # 边缘额外奖励
    if (x in (1,8) or y in (1,8)) and (x,y) not in CORNERS:
        score += 10
    # 避免造成对手角落机会
    for dx, dy in NeighbourPosition:
        nx, ny = x+dx, y+dy
        if (nx, ny) in CORNERS and board[nx][ny] == Empty:
            score -= 15
    # 模拟落子
    temp = BoardCopy(board)
    flips = apply_move_and_get_flips(temp, color, x, y)
    flipped = len(flips)
    # 翻转收益权重
    score += flipped * 2
    # 行动力：限制对手
    opp_moves = PossibleMove(-color, temp)
    score -= len(opp_moves) * 3
    # 边缘连通性：相邻同色加分
    for dx, dy in DIRECTIONS:
        nx, ny = x+dx, y+dy
        if 1 <= nx <= 8 and 1 <= ny <= 8 and temp[nx][ny] == color:
            if x in (1,8) or y in (1,8):
                score += 5
    return score

# 主 AI 函数
def player(color, board):
    moves = PossibleMove(color, board)
    if not moves:
        return (0,0)
    # 优先占角
    corners = [m for m in moves if m in CORNERS]
    if corners:
        return random.choice(corners)
    # 避免危险区
    safe = [m for m in moves if m not in DANGER_ZONES]
    if safe:
        moves = safe
    # 评估并选最优
    scored = [(evaluate_move(board, color, m), m) for m in moves]
    scored.sort(reverse=True, key=lambda x: x[0])
    best_score = scored[0][0]
    best_moves = [m for s,m in scored if s == best_score]
    return random.choice(best_moves)

# 兼容接口
advanced_player = player
