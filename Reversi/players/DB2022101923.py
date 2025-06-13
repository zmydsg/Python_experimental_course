# player2.py
# A simple Reversi player strategy that prioritizes corner positions
from Reversi import *
def player(Colour, Board):

    # 获取所有合法移动
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)

    # 定义角落和危险区域
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    danger_zones = [(1, 2), (2, 1), (2, 2),
                    (1, 7), (2, 7), (2, 8),
                    (7, 1), (7, 2), (8, 2),
                    (7, 7), (7, 8), (8, 7)]
    edges = [(1, y) for y in range(2, 8)] + [(8, y) for y in range(2, 8)] + \
            [(x, 1) for x in range(2, 8)] + [(x, 8) for x in range(2, 8)]

    # 根据游戏阶段选择不同策略
    empty_count = sum(row.count(Empty) for row in Board)

    if empty_count > 40:  # 开局阶段
        for corner in corners:
            if corner in moves:
                return corner
        safe_moves = [move for move in moves if move not in danger_zones]
        return safe_moves[0] if safe_moves else moves[0]

    elif empty_count > 12:  # 中局阶段
        for corner in corners:
            if corner in moves:
                return corner
        safe_edge_moves = [move for move in moves if move in edges and move not in danger_zones]
        if safe_edge_moves:
            return safe_edge_moves[0]
        best_move = max(moves, key=lambda move: len(PossibleMove(Colour, PlaceMove(Colour, BoardCopy(Board), move[0], move[1]))))
        return best_move

    else:  # 终局阶段
        for corner in corners:
            if corner in moves:
                return corner
        def evaluate_move(move):
            temp_board = PlaceMove(Colour, BoardCopy(Board), move[0], move[1])
            return sum(row.count(Colour) for row in temp_board)
        best_move = max(moves, key=evaluate_move)
        return best_move

# # Importing the main system and testing the players
# if __name__ == "__main__":
#     from Reversi import  PlayGame, player1

#     winCount = 0
#     player1time = 0
#     player2time = 0
#     for i in range(100):
#         board,result, PlayTime, error = PlayGame(player1, player) 
#         if(result < 0) :
#             winCount += 1
#         player1time += PlayTime[0]
#         player2time += PlayTime[1]

#     print("result:",result)
#     print("PlayTime:",PlayTime)
#     print("winCount:",winCount)
#     print("error:",error)
#     print("winRate:",winCount/100*100,"%")
#     print("player1time:",player1time,"s")
#     print("player2time:",player2time,"s")


