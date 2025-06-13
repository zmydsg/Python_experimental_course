from Reversi import *
import time

def player(Colour, Board):
    """优化后的翻转棋策略"""
    start_time = time.time()
    
    # 获取所有合法移动
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)

    # 根据游戏阶段选择不同策略
    empty_count = sum(row.count(Empty) for row in Board)
    if empty_count > 40:  # 开局阶段
        best_move = opening_move(Colour, Board, moves)
    elif empty_count > 12:  # 中局阶段
        best_move = midgame_move(Colour, Board, moves)
    else:  # 终局阶段
        best_move = endgame_move(Colour, Board, moves)
    
    # 确保不超过时间限制
    elapsed = time.time() - start_time
    if elapsed > 2.9:  # 留出安全余量
        return moves[0]  # 如果超时风险，返回第一个合法移动
    
    return best_move

def opening_move(Colour, Board, moves):
    """优化后的开局策略"""
    # 优先占据角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner

    # 动态权重矩阵
    position_weights = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 500, -150, 30, 10, 10, 30, -150, 500, 0],
        [0, -150, -200, -5, -3, -3, -5, -200, -150, 0],
        [0, 30, -5, 15, 3, 3, 15, -5, 30, 0],
        [0, 10, -3, 3, 2, 2, 3, -3, 10, 0],
        [0, 10, -3, 3, 2, 2, 3, -3, 10, 0],
        [0, 30, -5, 15, 3, 3, 15, -5, 30, 0],
        [0, -150, -200, -5, -3, -3, -5, -200, -150, 0],
        [0, 500, -150, 30, 10, 10, 30, -150, 500, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    best_score = -float('inf')
    best_move = moves[0]

    for x, y in moves:
        score = position_weights[x][y]
        
        # 计算翻转棋子数
        flipped = count_flipped(Board, Colour, x, y)
        
        # 避免给对手创造角落机会
        temp_board = BoardCopy(Board)
        temp_board = PlaceMove(Colour, temp_board, x, y)
        opponent_moves = PossibleMove(-Colour, temp_board)
        
        # 惩罚给对手角落机会的移动
        for corner in corners:
            if corner in opponent_moves:
                score -= 500  # 更严厉的惩罚
        
        # 计算行动力
        my_mobility = len(PossibleMove(Colour, temp_board))
        opponent_mobility = len(opponent_moves)
        mobility = my_mobility - opponent_mobility
        
        # 综合得分
        total_score = 0.4 * score + 0.3 * flipped + 0.3 * mobility
        
        if total_score > best_score:
            best_score = total_score
            best_move = (x, y)
    
    return best_move

def midgame_move(Colour, Board, moves):
    """优化后的中局策略"""
    # 优先占据角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner

    # 动态权重矩阵
    position_weights = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 300, -100, 25, 8, 8, 25, -100, 300, 0],
        [0, -100, -150, -4, -2, -2, -4, -150, -100, 0],
        [0, 25, -4, 12, 2, 2, 12, -4, 25, 0],
        [0, 8, -2, 2, 1, 1, 2, -2, 8, 0],
        [0, 8, -2, 2, 1, 1, 2, -2, 8, 0],
        [0, 25, -4, 12, 2, 2, 12, -4, 25, 0],
        [0, -100, -150, -4, -2, -2, -4, -150, -100, 0],
        [0, 300, -100, 25, 8, 8, 25, -100, 300, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    best_score = -float('inf')
    best_move = moves[0]

    for x, y in moves:
        score = position_weights[x][y]
        
        # 计算翻转棋子数
        flipped = count_flipped(Board, Colour, x, y)
        
        # 避免给对手创造角落机会
        temp_board = BoardCopy(Board)
        temp_board = PlaceMove(Colour, temp_board, x, y)
        opponent_moves = PossibleMove(-Colour, temp_board)
        
        # 惩罚给对手角落机会的移动
        for corner in corners:
            if corner in opponent_moves:
                score -= 400
        
        # 避免危险边缘位置
        if (x, y) in [(1, 2), (1, 7), (2, 1), (2, 8), (7, 1), (7, 8), (8, 2), (8, 7)]:
            score -= 50
        
        # 计算行动力
        my_mobility = len(PossibleMove(Colour, temp_board))
        opponent_mobility = len(opponent_moves)
        
        # 使用相对行动力计算
        if my_mobility + opponent_mobility > 0:
            mobility = (my_mobility - opponent_mobility) / (my_mobility + opponent_mobility) * 100
        else:
            mobility = 0
        
        # 计算稳定子
        stability = calculate_stability(temp_board, Colour)
        
        # 综合得分
        total_score = 0.3 * score + 0.3 * flipped + 0.2 * mobility + 0.2 * stability
        
        if total_score > best_score:
            best_score = total_score
            best_move = (x, y)
    
    return best_move

def endgame_move(Colour, Board, moves):
    """优化后的终局策略"""
    # 优先占据角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner
    
    best_score = -float('inf')
    best_move = moves[0]
    
    for x, y in moves:
        temp_board = BoardCopy(Board)
        temp_board = PlaceMove(Colour, temp_board, x, y)
        
        # 计算当前得分
        current_score = evaluate_board(temp_board, Colour)
        
        # 考虑对手的最佳回应
        opponent_moves = PossibleMove(-Colour, temp_board)
        if opponent_moves:
            min_score = float('inf')
            for ox, oy in opponent_moves:
                opp_temp_board = BoardCopy(temp_board)
                opp_temp_board = PlaceMove(-Colour, opp_temp_board, ox, oy)
                opp_score = evaluate_board(opp_temp_board, Colour)
                if opp_score < min_score:
                    min_score = opp_score
            score = min_score
        else:
            score = current_score * 1.5  # 对手无步可走的奖励
        
        # 角落奖励和边缘惩罚
        if (x, y) in corners:
            score += 200
        elif (x, y) in [(1, 2), (1, 7), (2, 1), (2, 8), (7, 1), (7, 8), (8, 2), (8, 7)]:
            score -= 100
        
        # 考虑稳定子
        stability = calculate_stability(temp_board, Colour)
        score += stability * 2
        
        if score > best_score:
            best_score = score
            best_move = (x, y)
    
    return best_move

def calculate_stability(Board, Colour):
    """计算稳定子数量"""
    stable = 0
    # 角落稳定子
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for x, y in corners:
        if Board[x][y] == Colour:
            stable += 1
    
    # 边缘稳定子
    edges = [(1, j) for j in range(2, 8)] + [(8, j) for j in range(2, 8)] + \
            [(i, 1) for i in range(2, 8)] + [(i, 8) for i in range(2, 8)]
    
    for x, y in edges:
        if Board[x][y] == Colour:
            # 检查是否被对手棋子包围
            if not is_unstable(Board, Colour, x, y):
                stable += 0.5
    
    return stable

def is_unstable(Board, Colour, x, y):
    """检查棋子是否不稳定"""
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 1 <= nx <= 8 and 1 <= ny <= 8 and Board[nx][ny] == -Colour:
            return True
    return False

def count_flipped(Board, Colour, x, y):
    """优化后的翻转棋子计算"""
    total = 0
    directions = [(-1, -1), (-1, 0), (-1, 1),
                 (0, -1),           (0, 1),
                 (1, -1),  (1, 0),  (1, 1)]
    
    for dx, dy in directions:
        tx, ty = x + dx, y + dy
        count = 0
        while 1 <= tx <= 8 and 1 <= ty <= 8 and Board[tx][ty] == -Colour:
            count += 1
            tx += dx
            ty += dy
        if 1 <= tx <= 8 and 1 <= ty <= 8 and Board[tx][ty] == Colour:
            total += count
    return total

def evaluate_board(Board, Colour):
    """优化后的棋盘评估函数"""
    my_count = 0
    opp_count = 0
    corner_value = 50  # 提高角落价值
    edge_value = 10
    
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    edges = [(1, j) for j in range(2, 8)] + [(8, j) for j in range(2, 8)] + \
            [(i, 1) for i in range(2, 8)] + [(i, 8) for i in range(2, 8)]
    
    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Colour:
                my_count += 1
                if (x, y) in corners:
                    my_count += corner_value
                elif (x, y) in edges:
                    my_count += edge_value
            elif Board[x][y] == -Colour:
                opp_count += 1
                if (x, y) in corners:
                    opp_count += corner_value
                elif (x, y) in edges:
                    opp_count += edge_value
    
    # 计算行动力
    my_mobility = len(PossibleMove(Colour, Board))
    opp_mobility = len(PossibleMove(-Colour, Board))
    mobility_factor = (my_mobility - opp_mobility) * 3  # 增加行动力权重
    
    # 计算稳定子
    my_stability = calculate_stability(Board, Colour)
    opp_stability = calculate_stability(Board, -Colour)
    stability_factor = (my_stability - opp_stability) * 5
    
    return (my_count - opp_count) + mobility_factor + stability_factor