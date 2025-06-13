
from Reversi import *
import random
import time

#位置权重表，考虑边缘稳定性
position_weights = [
    [200, -50, 30, 5, 5, 30, -50, 200],  # 角落价值最高，避免角落旁位置
    [-50, -80, -5, -5, -5, -5, -80, -50],  # 第二行/列权重较低
    [30, -5, 10, 3, 3, 10, -5, 30],  # 内部位置权重适中
    [5, -5, 3, 3, 3, 3, -5, 5],  # 中心位置权重最低
    [5, -5, 3, 3, 3, 3, -5, 5],  # 中心位置权重最低
    [30, -5, 10, 3, 3, 10, -5, 30],  # 内部位置权重适中
    [-50, -80, -5, -5, -5, -5, -80, -50],  # 第七行/列权重较低
    [200, -50, 30, 5, 5, 30, -50, 200]  # 角落价值最高
]

# 角落位置及其相邻位置定义
corners = [(1, 1), (1, 8), (8, 1), (8, 8)]  # 四个角落位置
corner_adjacent = [(1, 2), (2, 1), (1, 7), (2, 8),
                   (7, 1), (8, 2), (7, 8), (8, 7)]  # 角落旁的危险位置


def count_color(board, color):
    """统计棋盘上指定颜色的棋子数量"""
    count = 0
    for i in range(1, 9):  # 遍历棋盘所有位置
        for j in range(1, 9):
            if board[i][j] == color:  # 找到指定颜色棋子
                count += 1  # 计数器增加
    return count


def evaluate_board(player, board):
    """从当前玩家视角评估棋盘状态"""
    opponent = -player  # 对手颜色
    my_score = 0  # 当前玩家得分
    opp_score = 0  # 对手得分
    # 计算双方行动力（可行走法数量）
    my_mobility = len(PossibleMove(player, board))
    opp_mobility = len(PossibleMove(opponent, board))

    # 基于位置权重评估
    for i in range(1, 9):  # 遍历所有棋盘位置
        for j in range(1, 9):
            if board[i][j] == player:  # 当前玩家的棋子
                my_score += position_weights[i - 1][j - 1]  # 加上位置权重
            elif board[i][j] == opponent:  # 对手的棋子
                opp_score += position_weights[i - 1][j - 1]  # 对手得分增加

    # 行动力优势（在中前期更为重要）
    mobility_factor = 0
    if my_mobility + opp_mobility > 0:  # 避免除零错误
        # 计算相对行动力优势（比例形式）
        mobility_factor = 30 * (my_mobility - opp_mobility) / (my_mobility + opp_mobility)

    # 角落控制评估
    corner_value = 0
    for corner in corners:  # 检查每个角落
        if board[corner[0]][corner[1]] == player:  # 当前玩家控制角落
            corner_value += 100  # 加分
        elif board[corner[0]][corner[1]] == opponent:  # 对手控制角落
            corner_value -= 100  # 减分

    # 避免角落旁位置（除非必要）
    corner_penalty = 0
    for square in corner_adjacent:  # 检查每个危险位置
        if board[square[0]][square[1]] == player:  # 当前玩家占据危险位置
            corner_penalty -= 30  # 惩罚分

    # 棋子数量差（在残局更重要）
    piece_count = count_color(board, player) + count_color(board, opponent)  # 总棋子数
    piece_factor = 0
    if piece_count > 50:  # 残局阶段（超过50个棋子）
        # 计算棋子数量差并加权
        piece_factor = 2 * (count_color(board, player) - count_color(board, opponent))

    # 综合所有因素计算总分
    total_score = (my_score - opp_score) + mobility_factor + corner_value + corner_penalty + piece_factor
    return total_score


def minimax(player, board, depth, alpha, beta, maximizing_player):
    """带α-β剪枝的Minimax算法"""
    if depth == 0:  # 达到搜索深度
        return evaluate_board(player, board), None  # 返回评估值和空移动

    moves = PossibleMove(player, board)  # 获取所有可行走法

    if not moves:  # 如果没有可行走法
        if depth > 1:  # 如果还有深度
            # 评估对手回合（传递回合）
            value, _ = minimax(-player, board, depth - 1, alpha, beta, not maximizing_player)
            return value, None
        return evaluate_board(player, board), None  # 直接返回评估值

    best_move = None  # 最佳走法初始化

    if maximizing_player:  # 最大化玩家（当前玩家）
        max_eval = -float('inf')  # 初始化为负无穷
        for move in moves:  # 遍历所有走法
            new_board = BoardCopy(board)  # 复制棋盘
            PlaceMove(player, new_board, move[0], move[1])  # 模拟走法
            # 递归搜索
            eval, _ = minimax(-player, new_board, depth - 1, alpha, beta, False)

            if eval > max_eval:  # 找到更好评估值
                max_eval = eval
                best_move = move  # 更新最佳走法

            alpha = max(alpha, eval)  # 更新α值
            if beta <= alpha:  # α-β剪枝条件
                break  # 剪枝

        return max_eval, best_move
    else:  # 最小化玩家（对手）
        min_eval = float('inf')  # 初始化为正无穷
        for move in moves:  # 遍历所有走法
            new_board = BoardCopy(board)  # 复制棋盘
            PlaceMove(player, new_board, move[0], move[1])  # 模拟走法
            # 递归搜索
            eval, _ = minimax(-player, new_board, depth - 1, alpha, beta, True)

            if eval < min_eval:  # 找到更好（对对手更好）评估值
                min_eval = eval
                best_move = move  # 更新最佳走法

            beta = min(beta, eval)  # 更新β值
            if beta <= alpha:  # α-β剪枝条件
                break  # 剪枝

        return min_eval, best_move


def player(Colour, Board):
    """带自适应搜索深度的黑白棋AI策略"""
    # 确定游戏阶段
    total_pieces = count_color(Board, Black) + count_color(Board, White)

    # 根据游戏阶段调整搜索深度
    if total_pieces < 20:  # 开局阶段
        depth = 3
    elif total_pieces < 50:  # 中局阶段
        depth = 4
    else:  # 残局阶段
        depth = 6

    # 获取可行走法并检查是否有角落可占
    moves = PossibleMove(Colour, Board)
    if not moves:  # 无可行走法
        return (0, 0)

    # 总是优先占据可用角落
    for corner in corners:
        if corner in moves:
            return corner

    # 对其他走法使用Minimax搜索
    _, best_move = minimax(Colour, Board, depth, -float('inf'), float('inf'), True)

    # 如果Minimax未能返回走法，使用备用策略
    if best_move is None:
        # 选择翻转棋子最多的走法
        max_flips = -1
        for move in moves:
            new_board = BoardCopy(Board)
            PlaceMove(Colour, new_board, move[0], move[1])
            # 计算翻转的棋子数
            flips = count_color(new_board, Colour) - count_color(Board, Colour) - 1
            if flips > max_flips:
                max_flips = flips
                best_move = move

    return best_move