# ReversiStrategy.py - 黑白棋智能策略实现

from Reversi import *
import random
from typing import Tuple, List, Set

# 棋盘位置评估权重表 - 用于评估每个位置的价值
POSITION_WEIGHTS = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 120, -20, 20, 5, 5, 20, -20, 120],
    [0, -20, -40, -5, -5, -5, -5, -40, -20],
    [0, 20, -5, 15, 3, 3, 15, -5, 20],
    [0, 5, -5, 3, 3, 3, 3, -5, 5],
    [0, 5, -5, 3, 3, 3, 3, -5, 5],
    [0, 20, -5, 15, 3, 3, 15, -5, 20],
    [0, -20, -40, -5, -5, -5, -5, -40, -20],
    [0, 120, -20, 20, 5, 5, 20, -20, 120]
]

# 定义角落、边缘和危险位置
CORNERS = {(1, 1), (1, 8), (8, 1), (8, 8)}
EDGES = {(1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
         (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1),
         (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8),
         (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7)}
DANGER_ZONES = {(2, 2), (2, 7), (7, 2), (7, 7)}


def player(Colour: int, Board: List[List[int]]) -> Tuple[int, int]:
    """
    黑白棋智能策略玩家函数

    参数:
    - Colour: 当前玩家的颜色 (1为黑，-1为白)
    - Board: 当前棋盘状态

    返回:
    - 最佳落子位置的坐标 (x, y)
    """
    # 获取所有可能的移动
    possible_moves = list(PossibleMove(Colour, Board))

    # 如果没有可能的移动，返回无效位置
    if not possible_moves:
        return (0, 0)

    # 获取对手颜色
    opponent_colour = -Colour  # 1->-1, -1->1

    # 计算当前游戏阶段
    game_progress = get_game_progress(Board)

    # 根据游戏阶段选择策略
    if game_progress < 0.3:  # 开局阶段
        best_move = opening_strategy(Colour, Board, possible_moves)
    elif game_progress < 0.7:  # 中局阶段
        best_move = midgame_strategy(Colour, Board, possible_moves)
    else:  # 残局阶段
        best_move = endgame_strategy(Colour, Board, possible_moves)

    return best_move


def get_game_progress(Board: List[List[int]]) -> float:
    """计算游戏进度 (0.0到1.0之间的值)"""
    empty_cells = sum(row.count(0) for row in Board)
    total_cells = 64
    return (total_cells - empty_cells) / total_cells


def opening_strategy(Colour: int, Board: List[List[int]], possible_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
    """开局阶段策略 - 优先考虑角落和边缘位置"""
    best_score = -float('inf')
    best_move = possible_moves[0]

    for move in possible_moves:
        x, y = move

        # 角落位置优先级最高
        if (x, y) in CORNERS:
            return move

        # 避开危险区域
        if (x, y) in DANGER_ZONES:
            continue

        # 计算移动后的稳定度
        stability = calculate_stability(Colour, Board, x, y)

        # 计算移动后的行动力
        mobility = calculate_mobility(Colour, Board, x, y)

        # 计算位置价值
        position_value = POSITION_WEIGHTS[x][y]

        # 综合评分
        score = 0.4 * stability + 0.4 * position_value + 0.2 * mobility

        if score > best_score:
            best_score = score
            best_move = move

    return best_move


def midgame_strategy(Colour: int, Board: List[List[int]], possible_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
    """中局阶段策略 - 平衡稳定度和行动力"""
    best_score = -float('inf')
    best_move = possible_moves[0]

    for move in possible_moves:
        x, y = move

        # 角落位置优先级最高
        if (x, y) in CORNERS:
            return move

        # 避开危险区域
        if (x, y) in DANGER_ZONES:
            continue

        # 计算移动后的稳定度
        stability = calculate_stability(Colour, Board, x, y)

        # 计算移动后的行动力
        mobility = calculate_mobility(Colour, Board, x, y)

        # 计算位置价值
        position_value = POSITION_WEIGHTS[x][y]

        # 计算翻转棋子数 (中局阶段适当考虑)
        flipped_count = count_flipped_pieces(Colour, Board, x, y)

        # 综合评分
        score = 0.35 * stability + 0.3 * position_value + 0.25 * mobility + 0.1 * flipped_count

        if score > best_score:
            best_score = score
            best_move = move

    return best_move


def endgame_strategy(Colour: int, Board: List[List[int]], possible_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
    """残局阶段策略 - 最大化棋子数量"""
    best_score = -float('inf')
    best_move = possible_moves[0]

    for move in possible_moves:
        x, y = move

        # 角落位置优先级最高
        if (x, y) in CORNERS:
            return move

        # 计算翻转棋子数 (残局阶段最重要)
        flipped_count = count_flipped_pieces(Colour, Board, x, y)

        # 计算移动后的稳定度
        stability = calculate_stability(Colour, Board, x, y)

        # 计算位置价值
        position_value = POSITION_WEIGHTS[x][y]

        # 综合评分
        score = 0.5 * flipped_count + 0.3 * stability + 0.2 * position_value

        if score > best_score:
            best_score = score
            best_move = move

    return best_move


def calculate_stability(Colour: int, Board: List[List[int]], x: int, y: int) -> int:
    """计算在位置(x,y)落子后的稳定度"""
    temp_board = [row.copy() for row in Board]
    PlaceMove(Colour, temp_board, x, y)

    stability = 0
    for i in range(1, 9):
        for j in range(1, 9):
            if temp_board[i][j] == Colour:
                if (i, j) in CORNERS:
                    stability += 4
                elif (i, j) in EDGES:
                    stability += 2
                else:
                    stability += 1
    return stability


def calculate_mobility(Colour: int, Board: List[List[int]], x: int, y: int) -> int:
    """计算在位置(x,y)落子后对手的可能移动数 (行动力压制)"""
    temp_board = [row.copy() for row in Board]
    PlaceMove(Colour, temp_board, x, y)

    opponent_colour = -Colour
    opponent_moves = PossibleMove(opponent_colour, temp_board)

    return -len(list(opponent_moves))


def count_flipped_pieces(Colour: int, Board: List[List[int]], x: int, y: int) -> int:
    """计算在位置(x,y)落子后翻转的棋子数"""
    temp_board = [row.copy() for row in Board]
    before_count = sum(row.count(Colour) for row in Board)
    PlaceMove(Colour, temp_board, x, y)
    after_count = sum(row.count(Colour) for row in temp_board)
    return after_count - before_count


def print_game_result(Board: List[List[int]], result: int) -> None:
    """打印游戏结果"""
    black_count = sum(row.count(1) for row in Board)
    white_count = sum(row.count(-1) for row in Board)

    # 判断胜负
    if result > 0:
        winner = "黑方(智能策略)"
        loser = "白方(随机策略)"
        diff = result
    elif result < 0:
        winner = "白方(随机策略)"
        loser = "黑方(智能策略)"
        diff = -result
    else:
        print("\n===== 游戏结束 =====")
        print(f"黑方: {black_count} 枚")
        print(f"白方: {white_count} 枚")
        print("结果: 平局！")
        return

    print("\n===== 游戏结束 =====")
    print(f"黑方: {black_count} 枚")
    print(f"白方: {white_count} 枚")
    print(f"胜者: {winner}")
    print(f"差值: {diff} 枚")


if __name__ == "__main__":
    # 使用智能策略(黑方)对战原始随机策略(白方)
    Board, result, PlayTime, error = PlayGame(player1, player)

    # 打印结果
    print_game_result(Board, result)

    # 打印用时
    print(f"黑方(智能策略)用时: {PlayTime[1]:.2f} 秒")
    print(f"白方(随机策略)用时: {PlayTime[0]:.2f} 秒")