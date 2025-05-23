# player1.py - 实现一个简单的AI玩家
from reversi import *

def player1(player, board):
    """
    一个简单的AI玩家，使用贪心策略
    选择能够翻转最多对手棋子的位置
    """
    # 获取所有可能的移动
    possible_moves = PossibleMove(player, board)
    
    # 如果没有可行的移动，返回(-1, -1)表示跳过
    if not possible_moves:
        return (-1, -1)
    
    # 评估每个移动的得分（翻转的棋子数量）
    best_score = -1
    best_move = possible_moves[0]
    
    for move in possible_moves:
        x, y = move
        # 模拟这个移动
        new_board = PlaceMove(player, board, x, y)
        # 计算翻转后的得分差
        score = GetScore(player, new_board) - GetScore(player, board)
        
        # 更新最佳移动
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move