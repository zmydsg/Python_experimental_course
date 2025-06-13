from Reversi import *

def player(player, Board):
    """使用改进策略的AI玩家：结合位置价值、行动力和稳定性，使用Alpha-Beta剪枝搜索"""

    # 位置价值表 - 角的价值最高，边缘其次，内部非边缘位置价值较低
    position_weights = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 100, -20, 10, 5, 5, 10, -20, 100, 0],
        [0, -20, -50, -2, -2, -2, -2, -50, -20, 0],
        [0, 10, -2, -1, -1, -1, -1, -2, 10, 0],
        [0, 5, -2, -1, -1, -1, -1, -2, 5, 0],
        [0, 5, -2, -1, -1, -1, -1, -2, 5, 0],
        [0, 10, -2, -1, -1, -1, -1, -2, 10, 0],
        [0, -20, -50, -2, -2, -2, -2, -50, -20, 0],
        [0, 100, -20, 10, 5, 5, 10, -20, 100, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    # 深度限制
    DEPTH = 3

    # 历史启发表
    history_table = [[0] * 9 for _ in range(9)]

    def evaluate_position(board):
        """评估当前棋盘状态的价值"""
        player_score = 0
        opponent = -player

        # 1. 位置价值评估
        for x in range(1, 9):
            for y in range(1, 9):
                if board[x][y] == player:
                    player_score += position_weights[x][y]
                elif board[x][y] == opponent:
                    player_score -= position_weights[x][y]

        # 2. 行动力评估（当前可落子数）
        player_moves = len(PossibleMove(player, board))
        opponent_moves = len(PossibleMove(opponent, board))
        if player_moves + opponent_moves > 0:
            mobility_score = 100 * (player_moves - opponent_moves) / (player_moves + opponent_moves)
            player_score += mobility_score

        # 3. 稳定性评估（已占据的稳定棋子数）
        def is_stable(x, y, piece, board_state):
            if x < 1 or x > 8 or y < 1 or y > 8:
                return False
            if board_state[x][y] != piece:
                return False
            # 检查是否在角落
            if (x == 1 and y == 1) or (x == 1 and y == 8) or (x == 8 and y == 1) or (x == 8 and y == 8):
                return True
            return False

        player_stable = 0
        opponent_stable = 0
        for x in range(1, 9):
            for y in range(1, 9):
                if board[x][y] == player:
                    if is_stable(x, y, player, board):
                        player_stable += 1
                elif board[x][y] == opponent:
                    if is_stable(x, y, opponent, board):
                        opponent_stable += 1

        if player_stable + opponent_stable > 0:
            stability_score = 100 * (player_stable - opponent_stable) / (player_stable + opponent_stable)
            player_score += stability_score

        return player_score

    def sort_moves(moves):
        """根据历史启发表对移动进行排序"""
        return sorted(moves, key=lambda move: history_table[move[0]][move[1]], reverse=True)

    def alphabeta(board, depth, alpha, beta, maximizing_player):
        """Alpha-Beta剪枝算法"""
        if depth == 0:
            return evaluate_position(board), None

        moves = PossibleMove(player if maximizing_player else -player, board)
        if not moves:
            # 无法移动，检查对手是否可以移动
            opponent_moves = PossibleMove(-player if maximizing_player else player, board)
            if not opponent_moves:
                # 双方都无法移动，游戏结束
                return evaluate_position(board), (0, 0)
            else:
                # 只能跳过，继续搜索
                return alphabeta(board, depth - 1, alpha, beta, not maximizing_player)

        moves = sort_moves(moves)
        best_move = moves[0]
        if maximizing_player:
            max_eval = float('-inf')
            for move in moves:
                temp_board = [row[:] for row in board]
                temp_board = PlaceMove(player, temp_board, move[0], move[1])
                eval_score, _ = alphabeta(temp_board, depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                    history_table[move[0]][move[1]] += 2 ** depth  # 更新历史启发表
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta剪枝
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                temp_board = [row[:] for row in board]
                temp_board = PlaceMove(-player, temp_board, move[0], move[1])
                eval_score, _ = alphabeta(temp_board, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                    history_table[move[0]][move[1]] += 2 ** depth  # 更新历史启发表
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha剪枝
            return min_eval, best_move

    # 开始Alpha-Beta搜索
    _, best_move = alphabeta(Board, DEPTH, float('-inf'), float('inf'), True)
    return best_move