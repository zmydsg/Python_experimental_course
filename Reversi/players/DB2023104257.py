import random
from Reversi import *

def player(Colour, Board):
    
    def monte_carlo_simulation(board, player, move):
        '''进行蒙特卡洛模拟，返回走法的胜率'''
        temp_board = BoardCopy(board)
        x, y = move
        PlaceMove(player, temp_board, x, y)
        
        # 随机模拟游戏直到结束
        current_player = -1 * player
        while True:
            possible_moves = PossibleMove(current_player, temp_board)
            if not possible_moves:
                current_player = -1 * current_player
                possible_moves = PossibleMove(current_player, temp_board)
                if not possible_moves:
                    break
            if possible_moves:
                random_move = random.choice(possible_moves)
                x, y = random_move
                PlaceMove(current_player, temp_board, x, y)
            current_player = -1 * current_player
        
        # 计算最终结果
        white_count = sum(row.count(White) for row in temp_board)
        black_count = sum(row.count(Black) for row in temp_board)
        if white_count > black_count:
            return 1 if player == White else 0
        elif black_count > white_count:
            return 1 if player == Black else 0
        else:
            return 0.5  # 平局
    
    a = PossibleMove(Colour, Board)
    l = len(a)
    if l > 0:
        # 如果有多个可能的走法，评估每个走法并选择最佳的
        best_win_rate = -1
        best_move = a[0]
        for move in a:
            win_rate = 0
            num_simulations = 15  # 模拟次数
            for _ in range(num_simulations):
                win_rate += monte_carlo_simulation(Board, Colour, move)
            win_rate /= num_simulations
            if win_rate > best_win_rate:
                best_win_rate = win_rate
                best_move = move
        return best_move
    else:
        return (0, 0)