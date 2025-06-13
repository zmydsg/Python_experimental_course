from Reversi import *
import time

# 位置子算法玩家函数
def player(Colour, Board):
    # 定义棋盘各位置的权重
    POSITION_WEIGHTS = [
    [1, 9, 2, 4, 4, 2, 9, 1],
    [9, 10, 8, 7, 7, 8, 10, 9],
    [2, 8, 3, 5, 5, 3, 8, 2],
    [4, 7, 5, 6, 6, 5, 7, 4],
    [4, 7, 5, 6, 6, 5, 7, 4],
    [2, 8, 3, 5, 5, 3, 8, 2],
    [9, 10, 8, 7, 7, 8, 10, 9],
    [1, 9, 2, 4, 4, 2, 9, 1]
]
    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0)

    best_move = None
    max_score = -float('inf')

    for move in possible_moves:
        new_board = PlaceMove(Colour, BoardCopy(Board), *move)
        score = 0
        for x in range(1, 9):
            for y in range(1, 9):
                if new_board[x][y] == Colour:
                    score += POSITION_WEIGHTS[x-1][y-1]  # 注意索引调整
        if score > max_score:
            max_score = score
            best_move = move

    return best_move

# 对战函数
def play_match(computer_player):
    position_wins = 0
    computer_wins = 0
    draws = 0
    total_time = 0

    for i in range(10):
        start_time = time.time()
        Board, result, PlayTime, error = PlayGame(player, computer_player)
        end_time = time.time()
        match_time = end_time - start_time
        total_time += match_time

        # 统计胜负结果
        if result > 0:
            position_wins += 1
        elif result < 0:
            computer_wins += 1
        else:
            draws += 1

        print(f"第 {i+1} 局：位置子算法 {'胜' if result > 0 else '负' if result < 0 else '平'}")

    print("\n===== 十局对战总结果 =====")
    print(f"位置子算法玩家胜场：{position_wins}")
    print(f"电脑玩家胜场：{computer_wins}")
    print(f"平局：{draws}")
    
    if position_wins > computer_wins:
        print("位置子算法玩家获胜次数更多！")
    elif position_wins < computer_wins:
        print("电脑玩家获胜次数更多！")
    else:
        print("双方获胜次数相同，平局！")

    print(f"十次对战总计算用时: {total_time:.2f} 秒")

    return position_wins, computer_wins, draws, total_time

if __name__ == "__main__":
    from Reversi import player1
    play_match(player1)