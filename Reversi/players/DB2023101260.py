import random
from Reversi import *

def player(Colour, Board):
    """
    智能策略：
    - 早期：优先角落，避免边缘陷阱
    - 中期：平衡行动力与稳定性
    - 后期：最大化稳定棋子数量
    """
    a = PossibleMove(Colour, Board)
    if not a:
        return (0, 0)
    
    # 计算当前游戏阶段
    total_pieces = sum(1 for row in Board for cell in row if cell != 0)
    if total_pieces < 20:
        game_phase = "early"
    elif total_pieces < 48:
        game_phase = "mid"
    else:
        game_phase = "late"
    
    # 定义关键位置
    corners = [(1,1), (1,8), (8,1), (8,8)]
    x_squares = [(2,2), (2,7), (7,2), (7,7)]  # 角落附近的危险位置
    c_squares = [(1,2), (2,1), (1,7), (2,8), (7,1), (8,2), (7,8), (8,7)]  # 边缘危险位置
    
    # 评估每个移动
    best_score = -float('inf')
    best_move = None
    
    for move in a:
        score = 0
        x, y = move
        
        # 基础位置评分
        if (x, y) in corners:
            score += 1000  # 角落最高优先级
        elif (x, y) in x_squares:
            score -= 500   # X位置非常危险
        elif (x, y) in c_squares:
            score -= 200   # C位置较危险
        
        # 阶段特定评估
        if game_phase == "early":
            # 早期：避免边缘陷阱
            if x in (1, 8) or y in (1, 8):
                # 边缘安全性检查
                if (x == 1 or x == 8) and (y == 1 or y == 8):
                    score -= 100  # 角落附近边缘扣分
        elif game_phase == "mid":
            # 中期：平衡行动力与稳定性
            new_board = PlaceMove(Colour, BoardCopy(Board), x, y)
            
            # 行动力平衡
            self_mobility = len(PossibleMove(Colour, new_board))
            opponent_mobility = len(PossibleMove(-Colour, new_board))
            score += 10 * (self_mobility - opponent_mobility)
            
            # 稳定性评估（仅检查边缘）
            if x in (1, 8) or y in (1, 8):
                stable = True
                for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                    nx, ny = x + dx, y + dy
                    if 1 <= nx <= 8 and 1 <= ny <= 8 and new_board[nx-1][ny-1] == -Colour:
                        stable = False
                        break
                if stable:
                    score += 200
        elif game_phase == "late":
            # 后期：最大化稳定棋子数量
            new_board = PlaceMove(Colour, BoardCopy(Board), x, y)
            
            # 仅计算角落和边缘稳定棋子
            stable_count = 0
            for corner in corners:
                if new_board[corner[0]-1][corner[1]-1] == Colour:
                    stable_count += 1
            
            # 检查边缘连续性
            for i in [0, 7]:
                if all(new_board[i][j] == Colour for j in range(8)):
                    stable_count += 4
            for j in [0, 7]:
                if all(new_board[i][j] == Colour for i in range(8)):
                    stable_count += 4
            
            score += 50 * stable_count
        
        # 潜在行动力评估（只考虑直接对手移动）
        new_board = PlaceMove(Colour, BoardCopy(Board), x, y)
        opponent_moves = PossibleMove(-Colour, new_board)
        if len(opponent_moves) == 0:
            score += 300  # 完全限制对手移动
        elif len(opponent_moves) > 5:
            score -= 100  # 给对手太多机会
        
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move or a[0]  # 默认返回第一个合法移动
