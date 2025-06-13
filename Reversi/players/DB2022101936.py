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

# 优化权重模型（不同阶段）
opening_weights = [
    [150, -30, 15, 5, 5, 15, -30, 150],
    [-30, -50, -3, -3, -3, -3, -50, -30],
    [15, -3, 10, 3, 3, 10, -3, 15],
    [5, -3, 3, 1, 1, 3, -3, 5],
    [5, -3, 3, 1, 1, 3, -3, 5],
    [15, -3, 10, 3, 3, 10, -3, 15],
    [-30, -50, -3, -3, -3, -3, -50, -30],
    [150, -30, 15, 5, 5, 15, -30, 150]
]

midgame_weights = [
    [180, -25, 10, 5, 5, 10, -25, 180],
    [-25, -45, -2, -2, -2, -2, -45, -25],
    [10, -2, 8, 2, 2, 8, -2, 10],
    [5, -2, 2, 1, 1, 2, -2, 5],
    [5, -2, 2, 1, 1, 2, -2, 5],
    [10, -2, 8, 2, 2, 8, -2, 10],
    [-25, -45, -2, -2, -2, -2, -45, -25],
    [180, -25, 10, 5, 5, 10, -25, 180]
]

endgame_weights = [
    [220, -15, 0, 0, 0, 0, -15, 220],
    [-15, -40, 0, 0, 0, 0, -40, -15],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [-15, -40, 0, 0, 0, 0, -40, -15],
    [220, -15, 0, 0, 0, 0, -15, 220]
]

def evaluate_position(Colour, board):
    """优化评估函数，增加更多战略要素"""
    empty_count = sum(row.count(Empty) for row in board)
    if empty_count > 44:
        position_weights = opening_weights
    elif empty_count > 12:
        position_weights = midgame_weights
    else:
        position_weights = endgame_weights

    my_score = 0
    opp_score = 0
    opponent = -Colour

    # 1. 棋子位置权重
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == Colour:
                my_score += position_weights[x - 1][y - 1]
            elif board[x][y] == opponent:
                opp_score += position_weights[x - 1][y - 1]

    # 2. 行动力（移动性）评估
    my_moves = PossibleMove(Colour, board)
    opp_moves = PossibleMove(opponent, board)
    my_mobility = len(my_moves)
    opp_mobility = len(opp_moves)
    
    # 增加移动性的权重，特别是在中局
    mobility_weight = 8 if empty_count > 12 else 5
    my_score += my_mobility * mobility_weight
    opp_score += opp_mobility * mobility_weight

    # 3. 角落控制
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    corner_weight = 50  # 增加角落价值
    for (x, y) in corners:
        if board[x][y] == Colour:
            my_score += corner_weight
        elif board[x][y] == opponent:
            opp_score += corner_weight

    # 4. 稳定子评估（仅在终局阶段使用）
    if empty_count <= 20:
        my_stable = count_stable_discs(Colour, board)
        opp_stable = count_stable_discs(opponent, board)
        stable_weight = 20  # 稳定子在终局价值更高
        my_score += my_stable * stable_weight
        opp_score += opp_stable * stable_weight

    # 5. 潜在行动力（看对手的移动性）
    # 当对手行动力低时，惩罚减少
    if opp_mobility == 0 and my_mobility > 0:
        my_score += 30  # 额外奖励压制对手

    # 6. 棋子数量（主要在终局重要）
    if empty_count <= 12:
        my_discs = sum(1 for row in board for cell in row if cell == Colour)
        opp_discs = sum(1 for row in board for cell in row if cell == opponent)
        disc_diff = my_discs - opp_discs
        my_score += disc_diff * 5

    return my_score - opp_score

def count_stable_discs(Colour, board):
    """改进稳定子计算，使用方向搜索法"""
    stable = 0
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    # 稳定子必须至少从两个方向被固定
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] != Colour:
                continue
                
            # 检查是否在边界上
            if x == 1 or x == 8 or y == 1 or y == 8:
                stable += 1
                continue
                
            # 检查是否被同色棋子从两个方向包围
            stable_directions = 0
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx <= 8 and 1 <= ny <= 8 and board[nx][ny] == Colour:
                    stable_directions += 1
                    if stable_directions >= 2:
                        stable += 1
                        break
    return stable

def gives_opponent_corner(Colour, Board, move):
    """优化角落风险检测"""
    (x, y) = move
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    adjacent_corners = {
        (1, 1): [(1, 2), (2, 1), (2, 2)],
        (1, 8): [(1, 7), (2, 8), (2, 7)],
        (8, 1): [(7, 1), (8, 2), (7, 2)],
        (8, 8): [(7, 8), (8, 7), (7, 7)]
    }
    opponent = -Colour
    
    for corner in corners:
        if Board[corner[0]][corner[1]] != Empty:
            continue
        if (x, y) in adjacent_corners[corner]:
            # 快速检查而不实际落子
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                nx, ny = corner[0] + dx, corner[1] + dy
                if (nx, ny) == (x, y):
                    return True
    return False

def opening_strategy(Colour, Board, moves):
    """增强开局策略，考虑更多模式"""
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    adjacent_to_corners = [(1, 2), (2, 1), (1, 7), (2, 8), (7, 1), (8, 2), (7, 8), (8, 7)]
    
    # 1. 优先占据角落
    for move in moves:
        if move in corners:
            return move
    
    # 2. 避免危险位置
    safe_moves = [move for move in moves if not gives_opponent_corner(Colour, Board, move)]
    
    # 3. 如果没有安全位置，选择风险最小的
    if not safe_moves:
        safe_moves = moves
    
    # 4. 使用浅层搜索评估最佳移动
    return search_best_move(Colour, Board, safe_moves, depth=2)

def midgame_strategy(Colour, Board, moves):
    """中局策略使用更深的搜索"""
    return search_best_move(Colour, Board, moves, depth=3)

def endgame_strategy(Colour, Board, moves, depth):
    """优化终局搜索，动态调整深度"""
    empty_count = sum(row.count(Empty) for row in Board)
    
    # 根据剩余空格动态调整深度
    if empty_count <= 4:
        current_depth = 8  # 深度搜索
    elif empty_count <= 8:
        current_depth = 6
    elif empty_count <= 12:
        current_depth = 4
    else:
        current_depth = depth
    
    return search_best_move(Colour, Board, moves, depth=current_depth)

def search_best_move(Colour, Board, moves, depth):
    """统一搜索函数，优化Alpha-Beta剪枝"""
    if not moves:
        return (0, 0)
    
    # 快速处理只有一个选择的情况
    if len(moves) == 1:
        return moves[0]
    
    opponent = -Colour
    best_move = moves[0]
    best_score = -float('inf')
    alpha = -float('inf')
    beta = float('inf')
    
    # 根据启发式预排序
    moves_sorted = sorted(
        moves,
        key=lambda m: evaluate_position(Colour, PlaceMove(Colour, BoardCopy(Board), *m)),
        reverse=True
    )
    
    # 限制搜索分支数量
    max_branches = 15 if depth > 3 else 20
    moves_to_search = moves_sorted[:max_branches]
    
    for (x, y) in moves_to_search:
        new_board = PlaceMove(Colour, BoardCopy(Board), x, y)
        
        # 使用Alpha-Beta搜索
        score = alphabeta(
            opponent, new_board, depth - 1, alpha, beta, False, Colour
        )
        
        if score > best_score:
            best_score = score
            best_move = (x, y)
        
        # 更新alpha值
        alpha = max(alpha, best_score)
        
        # Alpha剪枝
        if alpha >= beta:
            break
    
    return best_move

def alphabeta(player, board, depth, alpha, beta, is_maximizing, Colour):
    """优化Alpha-Beta剪枝，增加移动排序和终止条件"""
    # 检查游戏是否结束
    moves = PossibleMove(player, board)
    opponent = -player
    
    # 终止条件
    if depth == 0 or not moves:
        return evaluate_position(Colour, board)
    
    # 快速评估
    if depth <= 2:
        quick_eval = evaluate_position(Colour, board)
        if is_maximizing and quick_eval > beta:
            return beta
        if not is_maximizing and quick_eval < alpha:
            return alpha
    
    # 移动排序
    moves_sorted = sorted(
        moves,
        key=lambda m: evaluate_position(player, PlaceMove(player, BoardCopy(board), *m)),
        reverse=is_maximizing
    )
    
    # 限制分支数量
    max_branches = 10 if depth > 3 else 15
    moves_to_search = moves_sorted[:max_branches]
    
    if is_maximizing:
        value = -float('inf')
        for (x, y) in moves_to_search:
            new_board = PlaceMove(player, BoardCopy(board), x, y)
            value = max(value, alphabeta(
                opponent, new_board, depth - 1, alpha, beta, False, Colour
            ))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = float('inf')
        for (x, y) in moves_to_search:
            new_board = PlaceMove(player, BoardCopy(board), x, y)
            value = min(value, alphabeta(
                opponent, new_board, depth - 1, alpha, beta, True, Colour
            ))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

def player(Colour, Board):
    """优化主策略，增加缓存和快速通道"""
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)

    empty_count = sum(row.count(Empty) for row in Board)
    
    # 快速处理终局
    if empty_count <= 4:
        # 尝试立即获胜
        for move in moves:
            new_board = PlaceMove(Colour, BoardCopy(Board), *move)
            if not PossibleMove(-Colour, new_board):
                return move
    
    if empty_count > 44:
        return opening_strategy(Colour, Board, moves)
    elif empty_count > 12:
        return midgame_strategy(Colour, Board, moves)
    else:
        return endgame_strategy(Colour, Board, moves, depth=4)