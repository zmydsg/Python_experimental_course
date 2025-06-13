from Reversi import *
def player(Colour, Board):
    """Minimax策略玩家，带Alpha-Beta剪枝"""

    # 位置权重矩阵（经典翻转棋位置估值）
    WEIGHT_MATRIX = [
        [500, -100, 100, 50, 50, 100, -100, 500],
        [-100, -200, -50, -10, -10, -50, -200, -100],
        [100, -50, 30, 15, 15, 30, -50, 100],
        [50, -10, 15, 5, 5, 15, -10, 50],
        [50, -10, 15, 5, 5, 15, -10, 50],
        [100, -50, 30, 15, 15, 30, -50, 100],
        [-100, -200, -50, -10, -10, -50, -200, -100],
        [500, -100, 100, 50, 50, 100, -100, 500]
    ]

    # 评估函数
    def evaluate(board, player):
        score = 0
        mobility = 0
        for x in range(1, 9):
            for y in range(1, 9):
                if board[x][y] == player:
                    score += WEIGHT_MATRIX[x - 1][y - 1]
                elif board[x][y] == -player:
                    score -= WEIGHT_MATRIX[x - 1][y - 1]
        # 加入行动力因素
        mobility = len(PossibleMove(player, board))
        return score + mobility * 10

    # Minimax with Alpha-Beta
    def alphabeta(board, depth, alpha, beta, maximizing_player):
        current_player = Colour if maximizing_player else -Colour

        if depth == 0 or len(PossibleMove(current_player, board)) == 0:
            return evaluate(board, Colour)

        if maximizing_player:
            max_val = -float('inf')
            moves = PossibleMove(current_player, board)
            if not moves: return evaluate(board, Colour)
            for (x, y) in moves:
                new_board = BoardCopy(board)
                PlaceMove(current_player, new_board, x, y)
                val = alphabeta(new_board, depth - 1, alpha, beta, False)
                max_val = max(max_val, val)
                alpha = max(alpha, val)
                if beta <= alpha:
                    break  # Beta剪枝
            return max_val
        else:
            min_val = float('inf')
            moves = PossibleMove(current_player, board)
            if not moves: return evaluate(board, Colour)
            for (x, y) in moves:
                new_board = BoardCopy(board)
                PlaceMove(current_player, new_board, x, y)
                val = alphabeta(new_board, depth - 1, alpha, beta, True)
                min_val = min(min_val, val)
                beta = min(beta, val)
                if beta <= alpha:
                    break  # Alpha剪枝
            return min_val

    # 主决策逻辑
    legal_moves = PossibleMove(Colour, Board)
    if not legal_moves:
        return (0, 0)

    best_move = None
    best_value = -float('inf')
    depth = 2  # 根据测试调整搜索深度

    # 遍历所有合法移动
    for (x, y) in legal_moves:
        # 创建新棋盘模拟走棋
        new_board = BoardCopy(Board)
        PlaceMove(Colour, new_board, x, y)

        # 调用Alpha-Beta搜索
        move_value = alphabeta(new_board, depth - 1, -float('inf'), float('inf'), False)

        # 更新最佳走法
        if move_value > best_value or best_move is None:
            best_value = move_value
            best_move = (x, y)

    return best_move if best_move else legal_moves[0]

# Board, result, PlayTime, error = PlayGame(player, player)
# drawBoard(Board)
# print(result, PlayTime)
