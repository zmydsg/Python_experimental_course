import time
from Reversi import *

# 棋盘位置权重（8x8实际区域）
# WEIGHTS[row_idx - 1][col_idx - 1]
WEIGHTS = [
    [100, -20, 10, 5, 5, 10, -20, 100],  # 对应 (1,1) (1,2) ... (1,8)
    [-20, -30, -2, -2, -2, -2, -30, -20],  # 对应 (2,1) (2,2) ... (2,8)
    [10, -2, 1, 1, 1, 1, -2, 10],
    [5, -2, 1, 1, 1, 1, -2, 5],
    [5, -2, 1, 1, 1, 1, -2, 5],
    [10, -2, 1, 1, 1, 1, -2, 10],
    [-20, -30, -2, -2, -2, -2, -30, -20],  # 对应 (7,1) (7,2) ... (7,8)
    [100, -20, 10, 5, 5, 10, -20, 100]  # 对应 (8,1) (8,2) ... (8,8)
]

# 全局置换表，存储已经计算过的棋盘状态及其评估值
# 格式：{board_hash: (depth, score, flag)}
# flag: 'exact' (精确值), 'lowerbound' (下界), 'upperbound' (上界)
transposition_table = {}


def board_to_hash(Board):
    """
    将棋盘状态转换为一个可哈希的字符串。
    只包含实际的8x8游戏区域，作为置换表的键。
    """
    return ''.join(''.join(str(cell) for cell in row[1:9]) for row in Board[1:9])


def get_possible_moves_count(Player, Board):
    """
    获取当前玩家可行的合法走法数量。
    避免重复计算 PossibleMove，提高效率。
    """
    return len(PossibleMove(Player, Board))


def mobility_score(Player, Board):
    """
    计算行动力得分：己方合法走法数 - 对手合法走法数。
    高行动力通常意味着更多的选择和主动权。
    """
    my_moves = get_possible_moves_count(Player, Board)
    opponent_moves = get_possible_moves_count(-Player, Board)
    return my_moves - opponent_moves


def stable_discs_score(Player, Board):
    """
    计算稳定子得分。
    这是简化的稳定子计算，只关注角点是否被占据。
    在奥赛罗中，角点是唯一绝对稳定的棋子。
    """
    score = 0
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for x, y in corners:
        if Board[x][y] == Player:
            score += 1
        elif Board[x][y] == -Player:
            score -= 1
    # 给予角点非常高的权重，因为它们是永久性的优势
    return score * 200


def evaluate_board(Player, Board):
    """
    启发式评估函数：根据棋盘状态为当前玩家打分。
    根据游戏阶段（总棋子数）动态调整各项启发式指标的权重。
    """
    total_discs = sum(row.count(Black) + row.count(White) for row in Board)

    # 动态权重：根据游戏进程调整各项指标的重要性
    w_pos = 0  # 位置权重
    w_mobility = 0  # 行动力权重
    w_corner_stability = 0  # 角点稳定权重
    w_disc_diff = 0  # 棋子数量差权重

    if total_discs <= 20:  # 开局 (0-20颗棋子)
        w_pos = 5
        w_mobility = 25  # 早期行动力非常关键，争取主动权
        w_corner_stability = 60  # 早期抢角至关重要
        w_disc_diff = 0  # 早期棋子数量不重要
    elif total_discs <= 50:  # 中局 (21-50颗棋子)
        w_pos = 10
        w_mobility = 15  # 行动力依然重要，但略有下降
        w_corner_stability = 70  # 角点重要性持续
        w_disc_diff = 10  # 棋子数量差开始有影响
    else:  # 残局 (51-64颗棋子)
        w_pos = 2  # 位置权重降低，因为棋盘快满了
        w_mobility = 5  # 行动力不再是主要因素
        w_corner_stability = 100  # 稳定子（特别是角点）的价值最大化
        w_disc_diff = 100  # 棋子数量差成为决定性因素，直接影响胜负

    # 1. 位置权重 (Positional Weight)
    pos_score = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Player:
                pos_score += WEIGHTS[x - 1][y - 1]  # 使用正确索引 (row-1, col-1)
            elif Board[x][y] == -Player:
                pos_score -= WEIGHTS[x - 1][y - 1]

    # 2. 行动力 (Mobility)
    mob_score = mobility_score(Player, Board)

    # 3. 稳定子 (Stability)
    corner_stab_score = stable_discs_score(Player, Board)

    # 4. 棋子数量差 (Disc Difference)
    player_discs = sum(row.count(Player) for row in Board)
    opponent_discs = sum(row.count(-Player) for row in Board)
    disc_diff = player_discs - opponent_discs

    # 综合评估得分
    score = (w_pos * pos_score +
             w_mobility * mob_score +
             w_corner_stability * corner_stab_score +
             w_disc_diff * disc_diff)

    return score


def move_priority(move, Player, Board):
    """
    为可能的走法打分，用于提高 Alpha-Beta 剪枝效率 (走法排序)。
    优先选择能带来好位置、高行动力、避免陷阱的走法。
    """
    x, y = move
    priority = 0

    # 1. 角点优先级：最高优先级
    corners = {(1, 1), (1, 8), (8, 1), (8, 8)}
    if (x, y) in corners:
        priority += 2000  # 显著提高角点优先级

    # 2. 避免 C位 和 X位 陷阱：极低优先级
    # C位: (1,2), (2,1), (1,7), (2,8), (7,1), (8,2), (7,8), (8,7)
    # X位: (2,2), (2,7), (7,2), (7,7) (在WEIGHTS中已是负值，这里再加强)
    c_x_positions = {
        (1, 2), (2, 1), (1, 7), (2, 8),
        (7, 1), (8, 2), (7, 8), (8, 7),
        (2, 2), (2, 7), (7, 2), (7, 7)
    }
    if (x, y) in c_x_positions:
        priority -= 1000  # 大力惩罚 C/X 位，让它们排在后面

    # 3. 边缘优先级 (非C/X位)：次高优先级
    edges = {1, 8}
    if (x in edges or y in edges) and (x, y) not in corners and (x, y) not in c_x_positions:
        priority += 100  # 边缘位置通常比中心好

    # 4. 模拟落子后的行动力变化：非常重要的排序因素
    temp_board = BoardCopy(Board)
    # PlaceMove 会修改 temp_board，并返回被翻转的棋子列表
    PlaceMove(Player, temp_board, x, y)

    # 模拟落子后的己方行动力：越多越好
    new_my_mobility = get_possible_moves_count(Player, temp_board)
    priority += new_my_mobility * 50  # 倾向于能增加己方行动力的走法

    # 模拟落子后的对手行动力：越少越好
    new_opponent_mobility = get_possible_moves_count(-Player, temp_board)
    priority -= new_opponent_mobility * 50  # 倾向于能减少对手行动力的走法

    return priority


def alphabeta(Board, Player, depth, alpha, beta, maximizing_player, start_time, time_limit):
    """
    Minimax 算法与 Alpha-Beta 剪枝。
    """
    # 检查是否超时，如果超时则立即返回当前评估值
    if time.time() - start_time >= time_limit:
        # 如果搜索被中断，返回当前局面评估值，但不返回最佳走法
        # 上层 iterative_deepening 会使用此前已找到的最佳走法
        return evaluate_board(Player, Board), None

    # 保存原始 alpha 值，用于置换表的 flag 判断
    alpha_orig = alpha
    beta_orig = beta  # 赋值为原始 beta

    # 检查置换表：如果当前棋盘状态已在置换表中，且存储的深度满足要求，则直接使用结果
    board_h = board_to_hash(Board)
    if board_h in transposition_table:
        entry_depth, entry_score, flag = transposition_table[board_h]
        if entry_depth >= depth:  # 如果存储的深度大于或等于当前深度
            if flag == 'exact':
                return entry_score, None  # 找到了确切值
            elif flag == 'lowerbound':
                alpha = max(alpha, entry_score)  # 更新 alpha (下界)
            elif flag == 'upperbound':
                beta = min(beta, entry_score)  # 更新 beta (上界)
            if alpha >= beta:  # 可以剪枝
                return entry_score, None

    # 获取当前玩家的合法走法
    possible_moves = PossibleMove(Player, Board)

    # 终止条件：
    # 1. 达到搜索深度上限
    # 2. 游戏结束 (双方都无合法走法)
    if depth == 0 or (not possible_moves and not PossibleMove(-Player, Board)):
        return evaluate_board(Player, Board), None

    # 如果当前玩家无合法走法，则跳过该回合
    if not possible_moves:
        # 递归调用alphabeta，切换到对手，深度减1
        eval, _ = alphabeta(Board, -Player, depth - 1, alpha, beta, not maximizing_player, start_time, time_limit)
        # 将跳过回合的评估值存储到置换表（视为精确值，因为是强制跳过）
        transposition_table[board_h] = (depth, eval, 'exact')
        return eval, None  # 没有走法可返回，因为是跳过

    # 走法排序，提高剪枝效率
    possible_moves.sort(key=lambda m: move_priority(m, Player, Board), reverse=True)

    best_move = None

    if maximizing_player:  # 最大化玩家的回合 (寻找最高得分)
        max_eval = float('-inf')
        for move in possible_moves:
            # 在循环中再次检查时间，防止在单个走法模拟中超时
            if time.time() - start_time >= time_limit:
                break

            new_board = BoardCopy(Board)  # 复制棋盘进行模拟
            PlaceMove(Player, new_board, *move)  # 模拟落子

            # 递归调用alphabeta，切换到最小化玩家
            eval, _ = alphabeta(new_board, -Player, depth - 1, alpha, beta, False, start_time, time_limit)

            # 如果是因时间中断而返回，那么这个eval可能不准确，跳过当前循环，让上层决定
            if time.time() - start_time >= time_limit:
                break

            if eval > max_eval:
                max_eval = eval
                best_move = move  # 更新当前深度下的最佳走法
            alpha = max(alpha, eval)  # 更新 alpha 值
            if beta <= alpha:  # Beta 剪枝：如果当前最佳值已超过对手的上限，则无需继续搜索
                break

        # 将结果存储到置换表
        flag = 'exact'  # 默认是精确值
        if max_eval <= alpha_orig:  # 如果最大值小于或等于原始 alpha，则为上限
            flag = 'upperbound'
        elif max_eval >= beta:  # 如果最大值大于或等于 beta (被剪枝)，则为下限
            flag = 'lowerbound'
        transposition_table[board_h] = (depth, max_eval, flag)

        return max_eval, best_move
    else:  # 最小化玩家的回合 (寻找最低得分)
        min_eval = float('inf')
        for move in possible_moves:
            # 再次检查时间
            if time.time() - start_time >= time_limit:
                break

            new_board = BoardCopy(Board)
            PlaceMove(Player, new_board, *move)

            # 递归调用alphabeta，切换到最大化玩家
            eval, _ = alphabeta(new_board, -Player, depth - 1, alpha, beta, True, start_time, time_limit)

            # 如果是因时间中断而返回
            if time.time() - start_time >= time_limit:
                break

            if eval < min_eval:
                min_eval = eval
                best_move = move  # 更新当前深度下的最佳走法
            beta = min(beta, eval)  # 更新 beta 值
            if beta <= alpha:  # Alpha 剪枝：如果当前最佳值已低于对手的下限，则无需继续搜索
                break

        # 将结果存储到置换表
        flag = 'exact'
        if min_eval <= alpha:  # 如果最小值小于或等于 alpha (被剪枝)，则为上限
            flag = 'upperbound'
        elif min_eval >= beta_orig:  # 如果最小值大于或等于原始 beta，则为下限
            flag = 'lowerbound'
        transposition_table[board_h] = (depth, min_eval, flag)

        return min_eval, best_move


def iterative_deepening(Board, Player, max_depth=8, time_limit=1.5):
    """
    迭代加深搜索。
    逐步增加搜索深度，直到达到最大深度或超出时间限制。
    """
    start_time = time.time()
    best_move_found = None  # 存储在任何深度下找到的最佳走法

    # 在每次新的决策开始时清空置换表，确保不被上一轮对局的缓存干扰
    global transposition_table
    transposition_table = {}

    all_possible_moves = PossibleMove(Player, Board)
    if not all_possible_moves:
        return (0, 0)  # 无合法走法，返回 (0,0)

    # 初始排序，用于第一层搜索。即使时间限制非常短，也能返回一个相对较好的初始走法。
    all_possible_moves.sort(key=lambda m: move_priority(m, Player, Board), reverse=True)
    best_move_found = all_possible_moves[0]  # 初始化最佳走法为优先级最高的走法

    for depth in range(1, max_depth + 1):
        # 检查是否已超时，如果已经超时，则停止当前深度的搜索并返回
        if time.time() - start_time >= time_limit:
            break

        # 在当前深度进行 Alpha-Beta 搜索
        current_eval, current_move = alphabeta(Board, Player, depth, float('-inf'), float('inf'),
                                               True, start_time, time_limit)

        # 如果搜索因时间限制被中断 (current_move 为 None)，则跳过更新
        # 否则，更新最佳走法
        if current_move is not None:
            best_move_found = current_move

        # 再次检查是否已超时，避免在循环结束前返回
        if time.time() - start_time >= time_limit:
            break

    return best_move_found


def player(Colour, Board):
    """
    翻转棋AI玩家主函数。
    参数：
        Colour: 当前玩家颜色 (White 或 Black)
        Board: 当前棋盘状态
    返回值：
        Tuple (x, y): 最佳落子坐标 (1-8, 1-8)。
                      如果没有合法走法则返回 (0,0)。
    """

    # 设置合理的搜索时间和最大深度。
    # 比赛环境通常是1秒每回合。这里设置0.95秒留有余量，避免超时。
    # max_depth 可以根据机器性能和比赛时间限制调整，8层通常是一个不错的深度。
    move = iterative_deepening(Board, Colour, max_depth=8, time_limit=0.95)

    # iterative_deepening 已经处理了无合法走法的情况，会返回 (0,0)
    return move

