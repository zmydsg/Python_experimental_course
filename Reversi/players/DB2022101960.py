from Reversi import *

def player(Colour, Board):
    """
    智能玩家函数，基于当前棋盘状态选择最佳落子位置

    参数:
        Colour: 玩家颜色 (White 或 Black)
        Board: 当前棋盘状态

    返回:
        (x, y): 最佳落子位置，如果没有合法移动则返回 (0, 0)
    """
    # 获取所有可能的移动
    possible_moves = PossibleMove(Colour, Board)

    # 如果没有合法移动，返回 (0, 0)
    if not possible_moves:
        return (0, 0)

    # 定义中心区域权重
    center_weights = {
        (4, 4): 5, (4, 5): 5, (5, 4): 5, (5, 5): 5,
        (3, 4): 4, (4, 3): 4, (5, 6): 4, (6, 5): 4,
        (3, 5): 3, (4, 6): 3, (5, 3): 3, (6, 4): 3,
        (2, 4): 2, (4, 2): 2, (5, 7): 2, (6, 6): 2,
        (2, 5): 1, (4, 7): 1, (5, 2): 1, (6, 3): 1
    }

    # 计算每个可能移动的得分
    move_scores = []

    for (x, y) in possible_moves:
        # 基础分数：能翻转的棋子数量
        flips = 0
        for i in range(8):
            dx, dy = NeighbourDirection[NeighbourDirection1[i]]
            nx, ny = x + dx, y + dy
            temp_flips = 0

            # 检查方向上是否有可翻转的棋子
            while ValidCell(nx, ny) and Board[nx][ny] == -Colour:
                temp_flips += 1
                nx += dx
                ny += dy

            # 如果方向尽头是自己的棋子，则这些中间棋子都可以翻转
            if ValidCell(nx, ny) and Board[nx][ny] == Colour:
                flips += temp_flips

        # 如果这个移动没有翻转任何棋子，跳过（虽然PossibleMove应该已经过滤了这种情况）
        if flips == 0:
            continue

        # 计算位置分数（中心区域更有价值）
        position_score = center_weights.get((x, y), 0)

        # 总分 = 翻转的棋子数 + 位置分数
        total_score = flips + position_score

        # 额外加分：阻止对手形成连续威胁
        # 检查对手在这个位置落子后能翻转多少棋子
        opponent_colour = -Colour
        opponent_flips = 0
        for i in range(8):
            dx, dy = NeighbourDirection[NeighbourDirection1[i]]
            nx, ny = x + dx, y + dy
            temp_flips = 0

            while ValidCell(nx, ny) and Board[nx][ny] == opponent_colour:
                temp_flips += 1
                nx += dx
                ny += dy

            if ValidCell(nx, ny) and Board[nx][ny] == Colour:
                opponent_flips += temp_flips

        # 如果这个位置能显著减少对手的威胁，额外加分
        if opponent_flips > flips // 2:
            total_score += 2 * (opponent_flips - flips // 2)

        move_scores.append((total_score, flips, (x, y)))

    # 按分数排序，选择最高分的移动
    if move_scores:
        # 首先按总分排序，然后按翻转棋子数排序
        move_scores.sort(key=lambda x: (-x[0], -x[1]))
        best_move = move_scores[0][2]

        # 如果有多个相同分数的移动，随机选择一个
        same_score_moves = [m for score, flips, m in move_scores if score == move_scores[0][0]]
        if len(same_score_moves) > 1:
            return random.choice(same_score_moves)

        return best_move
    else:
        return (0, 0)