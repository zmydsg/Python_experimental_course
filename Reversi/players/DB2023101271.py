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
def player2(Colour, Board):
    a = set(PossibleMove(Colour, Board))
    la = len(a)
    if la>0:
        for i in range(len(weight)):
            b = list(a & weight[i])
            lb = len(b)
            if lb > 0:
                c = list(Neighbour(Board, b[j][0],b[j][1]).count(Colour) for j in range(lb))
                return b[c.index(max(c))]
    else:
        return (0,0)

def player(Colour, Board):
    """
    使用带 α-β 剪枝的极大极小搜索（深度 3)＋启发式评估函数，
    在合理时间内(<1.5s)寻找使最终得分尽可能高的落子。
    """
    import time
    from copy import deepcopy

    # 启发式评估函数权重
    WEIGHTS = {
        'piece_diff': 1.0,
        'corner': 25.0,
        'mobility': 2.0,
        'position': 5.0  # 新增位置权重
    }
    CORNERS = [(1,1), (1,8), (8,1), (8,8)]
    MAX_DEPTH = 3
    start_time = time.perf_counter()

    # 位置权重矩阵
    POSITION_WEIGHTS = [
     [100, -20, 10,  5,  5, 10, -20, 100],
     [-20, -50, -2, -2, -2, -2, -50, -20],
     [10,  -2,  0,  0,  0,  0,  -2,  10],
     [5,   -2,  0,  0,  0,  0,  -2,   5],
     [5,   -2,  0,  0,  0,  0,  -2,   5],
     [10,  -2,  0,  0,  0,  0,  -2,  10],
     [-20, -50, -2, -2, -2, -2, -50, -20],
     [100, -20, 10,  5,  5, 10, -20, 100]
 ]

    def evaluate(board):
        """对局面进行评分：棋子差 + 角位控制 + 行动力差 + 位置权重"""
        my, opp = 0, 0
        my_moves, opp_moves = 0, 0
        my_corners = opp_corners = 0
        my_position_score, opp_position_score = 0, 0

        for x in range(1, 9):
            for y in range(1, 9):
                if board[x][y] == Colour:
                    my += 1
                    my_position_score += POSITION_WEIGHTS[x-1][y-1]
                elif board[x][y] == -Colour:
                    opp += 1
                    opp_position_score += POSITION_WEIGHTS[x-1][y-1]
        # mobility
        my_moves = len(PossibleMove(Colour, board))
        opp_moves = len(PossibleMove(-Colour, board))
        # corners
        for cx, cy in CORNERS:
            if board[cx][cy] == Colour:
                my_corners += 1
            elif board[cx][cy] == -Colour:
                opp_corners += 1

        score = 0
        score += WEIGHTS['piece_diff'] * (my - opp)
        score += WEIGHTS['corner']     * (my_corners - opp_corners)
        score += WEIGHTS['mobility']   * (my_moves - opp_moves)
        score += WEIGHTS['position']   * (my_position_score - opp_position_score)
        return score

    def alphabeta(board, depth, alpha, beta, player):
        """α–β 剪枝的极大极小搜索"""
        # 时间检查
        if time.perf_counter() - start_time >= 1.5:
            # 超时则快速评估当前节点
            return evaluate(board)

        moves = PossibleMove(player, board)
        if depth == 0 or not moves:
            return evaluate(board)

        if player == Colour:  # 极大节点
            value = float('-inf')
            for x, y in moves:
                nb = deepcopy(board)
                nb = PlaceMove(player, nb, x, y)
                value = max(value, alphabeta(nb, depth-1, alpha, beta, -player))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:  # 极小节点
            value = float('inf')
            for x, y in moves:
                nb = deepcopy(board)
                nb = PlaceMove(player, nb, x, y)
                value = min(value, alphabeta(nb, depth-1, alpha, beta, -player))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    # 主逻辑：在所有候选着法中运行 α-β，选取最佳
    best_move = (0, 0)
    best_val = float('-inf')
    for move in PossibleMove(Colour, Board):
        nb = deepcopy(Board)
        nb = PlaceMove(Colour, nb, move[0], move[1])
        val = alphabeta(nb, MAX_DEPTH-1, float('-inf'), float('inf'), -Colour)
        if val > best_val:
            best_val = val
            best_move = move
    return best_move

if __name__ == '__main__':
    # a demo of the game
    Board, Result, TimeUsed, ErrorMessage = PlayGame(player1, player) 
    drawBoard(Board)
    print(Result)
    print(TimeUsed)
