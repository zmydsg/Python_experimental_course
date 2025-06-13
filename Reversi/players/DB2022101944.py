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

# 极大极小+α-β剪枝算法实现最优player

def player(Colour, Board):
    print("AI收到颜色：", Colour)
    print("AI收到棋盘：")
    for row in Board:
        print(row)
    import copy

    def get_opponent(colour):
        return 3 - colour

    def evaluate(board, colour):
        # 角落权重
        corners = [(1,1), (1,8), (8,1), (8,8)]
        corner_score = 25 * sum(1 for x, y in corners if board[x-1][y-1] == colour)
        # 己方棋子数
        my_count = sum(row.count(colour) for row in board)
        # 对方棋子数
        opp_count = sum(row.count(get_opponent(colour)) for row in board)
        # 行动力（可下步数）
        my_moves = len(PossibleMove(colour, board))
        opp_moves = len(PossibleMove(get_opponent(colour), board))
        # 评估分数
        return (my_count - opp_count) + corner_score + 2 * (my_moves - opp_moves)

    def minimax(board, colour, depth, alpha, beta, maximizing):
        moves = PossibleMove(colour, board)
        if depth == 0 or not moves:
            return evaluate(board, Colour), None
        best_move = None
        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                new_board = copy.deepcopy(board)
                PlaceMove(colour, new_board, move[0], move[1])
                eval_score, _ = minimax(new_board, get_opponent(colour), depth-1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                new_board = copy.deepcopy(board)
                PlaceMove(colour, new_board, move[0], move[1])
                eval_score, _ = minimax(new_board, get_opponent(colour), depth-1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    # 设定搜索深度，3~4较为平衡，越大越强但越慢
    depth = 3
    _, best_move = minimax(Board, Colour, depth, float('-inf'), float('inf'), True)
    print("AI建议落子：", best_move if best_move else (0,0))
    if best_move:
        return best_move
    else:
        return (0, 0)

if __name__ == "__main__":
    from Reversi import PlayGame, player1, drawBoard

    # 让player1执白，你的AI执黑
    Board, Result, TimeUsed, ErrorMessage = PlayGame(player1, player)
    print("最终棋盘：")
    drawBoard(Board)
    print("对局结果（正数为白胜，负数为黑胜）：", Result)
    print("用时（白,黑）：", TimeUsed)
    print("错误信息：", ErrorMessage)