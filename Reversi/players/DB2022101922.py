from Reversi import *

def player(Colour, Board):
    """
    参数:
        Colour: 当前玩家颜色 (1=Black, -1=White)
        Board: 当前棋盘状态
    返回:
        (x, y): 最佳移动位置
    """
    # 获取所有合法移动
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)

    # 根据游戏阶段选择不同策略
    empty_count = sum(row.count(Empty) for row in Board)
    if empty_count > 40:  # 开局阶段
        return perfect_opening(Colour, Board, moves)
    elif empty_count > 12:  # 中局阶段
        return aggressive_midgame(Colour, Board, moves)
    else:  # 终局阶段
        return perfect_endgame(Colour, Board, moves)


def perfect_opening(Colour, Board, moves):
    """完美开局策略：基于开局库和严格的位置价值"""
    # 标准开局库 - 优先走这些位置
    opening_book = {
        # 白方第一手标准最优走法
        ((4, 4, -1, 4, 5, 1, 5, 5, -1, 5, 4, 1), -1): [(3, 5), (5, 3), (6, 4), (4, 6)],

        # 黑方应对白方各种开局的标准走法
        ((4, 4, -1, 4, 5, 1, 5, 5, -1, 5, 4, 1, 3, 5, 1), 1): [(5, 3), (3, 3), (3, 6)],
        ((4, 4, -1, 4, 5, 1, 5, 5, -1, 5, 4, 1, 5, 3, 1), 1): [(3, 5), (3, 3), (6, 3)],
    }

    # 尝试匹配开局库
    board_key = tuple(Board[x][y] for x in range(10) for y in range(10))
    if (board_key, Colour) in opening_book:
        for move in opening_book[(board_key, Colour)]:
            if move in moves:
                return move

    # 棋盘位置权重 (完美开局)
    position_weights = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 999, -100, 50, 15, 15, 50, -100, 999, 0],  # 角落价值极高
        [0, -100, -150, -20, -8, -8, -20, -150, -100, 0],
        [0, 50, -20, 30, 5, 5, 30, -20, 50, 0],
        [0, 15, -8, 5, 3, 3, 5, -8, 15, 0],
        [0, 15, -8, 5, 3, 3, 5, -8, 15, 0],
        [0, 50, -20, 30, 5, 5, 30, -20, 50, 0],
        [0, -100, -150, -20, -8, -8, -20, -150, -100, 0],
        [0, 999, -100, 50, 15, 15, 50, -100, 999, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    # 1. 绝对优先选择角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner

    # 2. 次优先选择边缘位置
    edges = []
    for x in range(1, 9):
        edges.append((x, 1))
        edges.append((x, 8))
    for y in range(2, 8):
        edges.append((1, y))
        edges.append((8, y))

    for edge in edges:
        if edge in moves:
            # 检查是否会直接给对手创造角落机会
            temp_board = BoardCopy(Board)
            temp_board = PlaceMove(Colour, temp_board, edge[0], edge[1])
            opponent_moves = PossibleMove(-Colour, temp_board)
            opponent_corner = any(corner in opponent_moves for corner in corners)
            if not opponent_corner:
                return edge

    # 3. 评估其他位置
    best_score = -float('inf')
    best_move = moves[0]

    for x, y in moves:
        # 计算位置权重
        score = position_weights[x][y]

        # 模拟走棋后的棋盘
        temp_board = BoardCopy(Board)
        temp_board = PlaceMove(Colour, temp_board, x, y)

        # 严重惩罚会给对手角落机会的移动
        opponent_moves = PossibleMove(-Colour, temp_board)
        opponent_corner = any(corner in opponent_moves for corner in corners)
        if opponent_corner:
            score -= 500  # 比之前更大的惩罚

        # 计算行动力差
        my_mobility = len(PossibleMove(Colour, temp_board))
        opponent_mobility = len(opponent_moves)
        mobility = my_mobility - opponent_mobility

        # 计算潜在稳定性
        stability = calculate_potential_stability(temp_board, Colour, x, y)

        # 综合评分
        total_score = 0.5 * score + 0.2 * mobility + 0.3 * stability

        if total_score > best_score:
            best_score = total_score
            best_move = (x, y)

    return best_move


def aggressive_midgame(Colour, Board, moves):
    """激进中局策略：最大化翻转数同时控制关键位置"""
    # 棋盘位置权重 (中局)
    position_weights = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 999, -80, 40, 10, 10, 40, -80, 999, 0],
        [0, -80, -120, -15, -5, -5, -15, -120, -80, 0],
        [0, 40, -15, 25, 5, 5, 25, -15, 40, 0],
        [0, 10, -5, 5, 3, 3, 5, -5, 10, 0],
        [0, 10, -5, 5, 3, 3, 5, -5, 10, 0],
        [0, 40, -15, 25, 5, 5, 25, -15, 40, 0],
        [0, -80, -120, -15, -5, -5, -15, -120, -80, 0],
        [0, 999, -80, 40, 10, 10, 40, -80, 999, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    # 1. 绝对优先选择角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner

    # 2. 评估每个移动
    best_score = -float('inf')
    best_move = moves[0]

    for x, y in moves:
        # 计算翻转数
        flipped = count_flipped(Board, Colour, x, y)

        # 计算位置权重
        score = position_weights[x][y]

        # 模拟走棋
        temp_board = BoardCopy(Board)
        temp_board = PlaceMove(Colour, temp_board, x, y)

        # 严重惩罚会给对手角落机会的移动
        opponent_moves = PossibleMove(-Colour, temp_board)
        opponent_corner = any(corner in opponent_moves for corner in corners)
        if opponent_corner:
            score -= 600  # 比开局阶段更大的惩罚

        # 计算行动力差
        my_mobility = len(PossibleMove(Colour, temp_board))
        opponent_mobility = len(opponent_moves)
        mobility = my_mobility - opponent_mobility

        # 计算潜在稳定性
        stability = calculate_potential_stability(temp_board, Colour, x, y)

        # 计算边缘控制
        edge_control = calculate_edge_control(temp_board, Colour)

        # 综合评分
        total_score = (0.3 * flipped + 0.3 * score + 0.2 * mobility +
                       0.1 * stability + 0.1 * edge_control)

        if total_score > best_score:
            best_score = total_score
            best_move = (x, y)

    return best_move


def perfect_endgame(Colour, Board, moves):
    """完美终局策略：带深度搜索的终局算法"""
    # 1. 优先选择角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner

    # 2. 如果剩余棋子很少，进行深度搜索
    empty_count = sum(row.count(Empty) for row in Board)
    if empty_count <= 10:
        return endgame_search(Colour, Board, moves, depth=3)
    else:
        return endgame_search(Colour, Board, moves, depth=2)


def endgame_search(Colour, Board, moves, depth):
    """带alpha-beta剪枝的终局搜索"""
    best_score = -float('inf')
    best_move = moves[0]
    alpha = -float('inf')
    beta = float('inf')

    for move in moves:
        temp_board = BoardCopy(Board)
        temp_board = PlaceMove(Colour, temp_board, move[0], move[1])

        score = -negamax(-Colour, temp_board, depth - 1, -beta, -alpha)

        if score > best_score:
            best_score = score
            best_move = move

        if best_score > alpha:
            alpha = best_score

        if alpha >= beta:
            break

    return best_move


def negamax(Colour, Board, depth, alpha, beta):
    """Negamax算法实现"""
    if depth == 0:
        return evaluate_endgame(Board, -Colour)  # 注意符号

    moves = PossibleMove(Colour, Board)
    if not moves:
        if not PossibleMove(-Colour, Board):  # 游戏结束
            return final_evaluation(Board, -Colour)
        return -negamax(-Colour, Board, depth - 1, -beta, -alpha)

    best_value = -float('inf')
    for move in moves:
        temp_board = BoardCopy(Board)
        temp_board = PlaceMove(Colour, temp_board, move[0], move[1])

        value = -negamax(-Colour, temp_board, depth - 1, -beta, -alpha)

        if value > best_value:
            best_value = value

        if value > alpha:
            alpha = value

        if alpha >= beta:
            break

    return best_value


def evaluate_endgame(Board, Colour):
    """终局评估函数"""
    my_count = 0
    opp_count = 0
    corner_bonus = 0
    edge_bonus = 0

    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    edges = []
    for x in range(1, 9):
        edges.append((x, 1))
        edges.append((x, 8))
    for y in range(2, 8):
        edges.append((1, y))
        edges.append((8, y))

    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Colour:
                my_count += 1
                if (x, y) in corners:
                    corner_bonus += 15
                elif (x, y) in edges:
                    edge_bonus += 5
            elif Board[x][y] == -Colour:
                opp_count += 1

    return (my_count - opp_count) + corner_bonus + edge_bonus


def final_evaluation(Board, Colour):
    """游戏结束时的最终评估"""
    my_count = 0
    opp_count = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Colour:
                my_count += 1
            elif Board[x][y] == -Colour:
                opp_count += 1

    if my_count > opp_count:
        return 10000 + my_count  # 确保胜利
    elif my_count < opp_count:
        return -10000 - opp_count  # 确保失败
    else:
        return 0  # 平局


def calculate_potential_stability(Board, Colour, x, y):
    """计算潜在稳定性 - 预测棋子未来是否容易被翻转"""
    stability = 0
    # 角落棋子最稳定
    if (x, y) in [(1, 1), (1, 8), (8, 1), (8, 8)]:
        stability += 50

    # 边缘棋子比较稳定
    if x == 1 or x == 8 or y == 1 or y == 8:
        stability += 20

    # 检查是否被两个方向固定
    fixed_directions = 0
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if ValidCell(nx, ny) and Board[nx][ny] == Colour:
            fixed_directions += 1

    if fixed_directions >= 2:
        stability += 30

    return stability


def calculate_edge_control(Board, Colour):
    """计算边缘控制力"""
    edge_positions = []
    for x in range(1, 9):
        edge_positions.append((x, 1))
        edge_positions.append((x, 8))
    for y in range(2, 8):
        edge_positions.append((1, y))
        edge_positions.append((8, y))

    control = 0
    for pos in edge_positions:
        x, y = pos
        if Board[x][y] == Colour:
            control += 1
        elif Board[x][y] == -Colour:
            control -= 1

    return control


def count_flipped(Board, Colour, x, y):
    """计算在(x,y)落子后会翻转多少对手棋子"""
    flipped = 0
    for i in range(8):
        xcurrent = x
        ycurrent = y
        Direction = NeighbourDirection1[i]
        cell = NeighbourCell(Board, Direction, xcurrent, ycurrent)
        while ValidCell(xcurrent, ycurrent):
            if cell == (-1) * Colour:
                xcurrent += NeighbourDirection[Direction][0]
                ycurrent += NeighbourDirection[Direction][1]
                cell = NeighbourCell(Board, Direction, xcurrent, ycurrent)
                flipped += 1
                continue
            elif cell == Colour:
                break
            else:
                flipped = 0
                break
    return flipped
