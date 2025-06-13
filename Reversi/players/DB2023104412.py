from Reversi import *
def player(Colour, Board):
    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0)
    
    # 计算游戏阶段（基于已落子数）
    piece_count = sum(1 for x in range(1, 9) for y in range(1, 9) if Board[x][y] != Empty)
    game_phase = "opening" if piece_count < 20 else ("midgame" if piece_count < 50 else "endgame")
    
    # 位置权重矩阵（角落优先，避免危险边缘）
    position_weights = [
        [100, -40,  15,   5,   5,  15, -40, 100],
        [-40, -50,  -8,  -3,  -3,  -8, -50, -40],
        [ 15,  -8,   3,   1,   1,   3,  -8,  15],
        [  5,  -3,   1,   1,   1,   1,  -3,   5],
        [  5,  -3,   1,   1,   1,   1,  -3,   5],
        [ 15,  -8,   3,   1,   1,   3,  -8,  15],
        [-40, -50,  -8,  -3,  -3,  -8, -50, -40],
        [100, -40,  15,   5,   5,  15, -40, 100]
    ]
    
    # 危险边缘位置（可能导致对手占角）
    danger_positions = {(1,2), (2,1), (2,2), (1,7), (2,7), (2,8),
                       (7,1), (7,2), (8,2), (7,7), (7,8), (8,7)}
    
    # 翻转计数器（计算当前移动能翻转的棋子数）
    def count_flips(player, board, x, y):
        total = 0
        for dir_name in NeighbourDirection1:
            dx, dy = NeighbourDirection[dir_name]
            cx, cy = x + dx, y + dy
            temp = 0
            while ValidCell(cx, cy):
                if board[cx][cy] != -player:
                    break
                temp += 1
                cx += dx
                cy += dy
                if not ValidCell(cx, cy):
                    break
                if board[cx][cy] == player:
                    total += temp
                    break
        return total
    
    # 评估函数
    def evaluate_move(player, move):
        x, y = move
        score = 0
        
        # 1. 位置权重
        weight = position_weights[x-1][y-1]
        
        # 2. 角落特殊处理
        if (x, y) in [(1,1), (1,8), (8,1), (8,8)]:
            score += 200  # 直接占角最高优先级
        elif (x, y) in danger_positions:
            # 危险位置惩罚，但在后期可接受
            penalty = -80 if game_phase == "opening" else -30
            score += penalty
        
        # 3. 翻转数量
        flips = count_flips(player, Board, x, y)
        
        # 4. 潜在行动力评估
        new_board = BoardCopy(Board)
        PlaceMove(player, new_board, x, y)
        
        # 计算移动后双方行动力
        my_mobility = len(PossibleMove(player, new_board))
        opp_mobility = len(PossibleMove(-player, new_board))
        
        # 5. 角落安全性评估
        corners = [(1,1), (1,8), (8,1), (8,8)]
        corner_threat = any(corner in PossibleMove(-player, new_board) for corner in corners)
        
        # 6. 稳定性评估（简单版）
        stable_score = 0
        if x in (1, 8) or y in (1, 8):  # 边缘位置更稳定
            stable_score += 10
        
        # 根据不同游戏阶段调整权重
        if game_phase == "opening":
            # 开局：重视位置和安全性，避免过度翻转
            score += weight * 1.2 + flips * 0.7 + my_mobility * 2 - opp_mobility * 2.5
            if corner_threat:
                score -= 150  # 开局绝对避免给对手占角机会
                
        elif game_phase == "midgame":
            # 中局：平衡各种因素
            score += weight * 0.9 + flips * 1.2 + my_mobility * 3 - opp_mobility * 2.8
            if corner_threat:
                score -= 100  # 中局尽量避免给对手占角机会
            score += stable_score * 1.5
                
        else:  # endgame
            # 残局：最大化翻转数和棋子数
            score += weight * 0.4 + flips * 2.5 + my_mobility * 0.5 - opp_mobility * 0.3
            if corner_threat:
                score -= 50  # 残局可接受一定风险
            score += stable_score
        
        return score
    
    # 时间优化：如果移动很多，优先评估高权重位置
    if len(possible_moves) > 12:
        # 先筛选最有希望的候选移动（基于位置权重）
        candidates = []
        for move in possible_moves:
            x, y = move
            weight = position_weights[x-1][y-1]
            if weight >= 0:  # 只考虑非负权重的位置
                candidates.append(move)
        
        if not candidates:
            candidates = possible_moves[:8]  # 如果全是负权重，取前8个
    else:
        candidates = possible_moves
    
    # 评估候选移动并选择最佳
    scored_moves = []
    for move in candidates:
        score = evaluate_move(Colour, move)
        scored_moves.append((score, move))
    
    scored_moves.sort(reverse=True, key=lambda x: x[0])
    best_score = scored_moves[0][0]
    best_moves = [move for score, move in scored_moves if score >= best_score - 10]  # 允许小范围波动
    
    return random.choice(best_moves) if best_moves else possible_moves[0]