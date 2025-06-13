# Module for Python course project V3.0 2025
# This module is an example of player function to be submitted

from Reversi import *

ring1 = {(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
         (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8),
         (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (2, 8), (3, 8),
         (4, 8), (5, 8), (6, 8), (7, 8)}
coner1 = {(1,1), (1,8), (8,1), (8,8)}
ring2 = {(2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (7, 2), (7, 3),
         (7, 4), (7, 5), (7, 6), (7, 7), (3, 2), (4, 2), (5, 2), (6, 2),
         (3, 7), (4, 7), (5, 7), (6, 7)}
coner2 = {(2,2), (2,7), (7,2), (7,7)}
ring3 = {(3, 3), (3, 4), (3, 5), (3, 6), (6, 3), (6, 4), (6, 5), (6, 6),
         (4, 3), (5, 3), (4, 6), (5, 6)}
coner3 = {(3,3), (3,6), (6,3), (6,6)}
weight = {0: coner1, 1: ring1, 2: coner3, 3: ring3, 4: ring2-coner2, 5: coner2}
weight2 = {0: ring1, 1: ring3, 2: ring2}

# consider rings, coners and neighbour player's cells
# Place the chess-pieces at the outer corners/rings as much as possible
def player(Colour, Board):
    """优化策略：强化角落控制，动态边缘策略，前瞻性压制对手选项"""

    def evaluate_move(move, colour, board):
        x, y = move
        opponent = -colour

        # 直接占据角落的情况给予绝对优先
        if (x, y) in [(1, 1), (1, 8), (8, 1), (8, 8)]:
            return 10000  # 比player1更高的优先级

        # 危险区域检查（邻近未占据角落时的高风险）
        corner_risk = 0
        for (cx, cy) in [(1, 1), (1, 8), (8, 1), (8, 8)]:
            if board[cx][cy] == Empty:
                dist = max(abs(x - cx), abs(y - cy))
                if dist == 1:  # 紧邻未占据角落
                    corner_risk -= 500  # 比player1更强的惩罚
                elif dist == 2:  # 次邻近区域
                    corner_risk -= 200

        # 模拟落子后的棋盘
        sim_board = BoardCopy(board)
        sim_board = PlaceMove(colour, sim_board, x, y)

        # 计算对手的可行移动数（目标：最小化对手选择）
        opponent_moves = PossibleMove(opponent, sim_board)
        opponent_options = len(opponent_moves)

        # 计算潜在翻转数（优先长链翻转）
        flipped = 0
        for dx in range(1, 9):
            for dy in range(1, 9):
                if sim_board[dx][dy] == colour and board[dx][dy] != colour:
                    flipped += 1

        # 边缘奖励（非角落边缘位置）
        edge_bonus = 80 if (x in (1, 8) or y in (1, 8)) and (x, y) not in [(1, 1), (1, 8), (8, 1), (8, 8)] else 0

        # 稳定性评估（靠近已占据角落的加分）
        stability = 0
        for (cx, cy) in [(1, 1), (1, 8), (8, 1), (8, 8)]:
            if board[cx][cy] == colour:
                stability += 30 - 5 * max(abs(x - cx), abs(y - cy))

        # 综合评分公式（权重优化）
        return (
                flipped * 3 +  # 翻转数量优先
                stability * 2 +  # 稳定性加成
                edge_bonus +  # 边缘控制
                (-opponent_options * 8) +  # 压制对手选项（比player1更强压制）
                corner_risk  # 角落风险控制
        )

    legal_moves = PossibleMove(Colour, Board)
    if not legal_moves:
        return (0, 0)

    # 深度优化：对前3高分的移动进行一步前瞻
    scored_moves = [(move, evaluate_move(move, Colour, Board)) for move in legal_moves]
    scored_moves.sort(key=lambda x: -x[1])

    # 取前3名进行二次评估
    top_moves = scored_moves[:3]
    if len(top_moves) == 0:
        return (0, 0)

    # 二次评估：考虑对手的反制能力
    final_scores = []
    for move, _ in top_moves:
        sim_board = BoardCopy(Board)
        sim_board = PlaceMove(Colour, sim_board, move[0], move[1])
        opponent_moves = PossibleMove(-Colour, sim_board)

        # 找到对手最优反击的负面影响
        if opponent_moves:
            opponent_scores = [evaluate_move(op_move, -Colour, sim_board) for op_move in opponent_moves]
            worst_case = max(opponent_scores)  # 假设对手会选最优解
            final_score = evaluate_move(move, Colour, Board) - worst_case * 0.5
        else:
            final_score = 9999  # 对手无棋可下

        final_scores.append((move, final_score))

    final_scores.sort(key=lambda x: -x[1])
    best_move = final_scores[0][0]

    return best_move