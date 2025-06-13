# Module for Python course project V3.0 2025
# This module is an example of player function to be submitted

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

# consider rings, coners and neighbour player's cells
# Place the chess-pieces at the outer corners/rings as much as possible
def player(Colour, Board):
    # 计算当前步数（用于阶段判断）
    total_moves = 64 - sum(row.count(0) for row in Board)
    empty_count = sum(row.count(0) for row in Board)
    
    # 微调的位置权重表（基于实战优化）
    position_weights = [
        [2000, -500, 300, 150, 150, 300, -500, 2000],
        [-500, -600, -100, -50, -50, -100, -600, -500],
        [300,  -100,  50,  20,  20,  50,  -100,  300],
        [150,   -50,  20,  10,  10,  20,  -50,  150],
        [150,   -50,  20,  10,  10,  20,  -50,  150],
        [300,   -100,  50,  20,  20,  50,  -100,  300],
        [-500, -600, -100, -50, -50, -100, -600, -500],
        [2000, -500, 300, 150, 150, 300, -500, 2000]
    ]
    
    # 定义关键位置
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    danger_positions = [(2, 2), (2, 7), (7, 2), (7, 7)]
    edge_positions = [(1,3),(1,4),(1,5),(1,6),
                     (3,1),(4,1),(5,1),(6,1),
                     (3,8),(4,8),(5,8),(6,8),
                     (8,3),(8,4),(8,5),(8,6)]
    
    # 获取所有可行移动
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)
    
    # 1. 绝对优先占据角落
    for move in moves:
        if move in corners:
            return move
    
    # 2. 开局库优化（前10步）
    if total_moves < 10:
        # 处理常见的开局模式
        if (4, 3) in moves and Board[4][3] == Empty:
            return (4, 3)
        if (3, 4) in moves and Board[3][4] == Empty:
            return (3, 4)
        if (5, 4) in moves and Board[5][4] == Empty:
            return (5, 4)
        if (4, 5) in moves and Board[4][5] == Empty:
            return (4, 5)
    
    # 3. 如果剩余步数少（少于15步），使用终局优化
    if empty_count < 15:
        return endgame_optimization(Colour, Board)
    
    # 4. 避免让对手占据角落的危险位置
    safe_moves = []
    for move in moves:
        # 检查是否会为对手创造角落机会
        new_board = BoardCopy(Board)
        PlaceMove(Colour, new_board, move[0], move[1])
        opp_moves = PossibleMove(-Colour, new_board)
        
        creates_corner = False
        for opp_move in opp_moves:
            if opp_move in corners:
                creates_corner = True
                break
                
        if not creates_corner and move not in danger_positions:
            safe_moves.append(move)
    
    # 如果有安全移动，优先从中选择
    moves_to_consider = safe_moves if safe_moves else moves
    
    # 5. 动态深度搜索（根据剩余步数调整搜索深度）
    search_depth = 1
    if empty_count < 30:  # 中后期增加搜索深度
        search_depth = 2
    if empty_count < 20:  # 残局阶段更深搜索
        search_depth = 3
    
    best_score = -10000000
    best_move = None
    
    for move in moves_to_consider:
        # 创建新棋盘并执行当前移动
        new_board = BoardCopy(Board)
        PlaceMove(Colour, new_board, move[0], move[1])
        
        # 评估当前局面
        score = evaluate_position(Colour, new_board, position_weights, total_moves, empty_count)
        
        # 根据搜索深度进行多层搜索
        if search_depth > 0:
            opp_moves = PossibleMove(-Colour, new_board)
            if opp_moves:
                best_opp_score = -10000000
                for opp_move in opp_moves:
                    opp_board = BoardCopy(new_board)
                    PlaceMove(-Colour, opp_board, opp_move[0], opp_move[1])
                    
                    # 一层搜索
                    opp_score = evaluate_position(-Colour, opp_board, position_weights, total_moves + 1, empty_count - 1)
                    
                    # 二层搜索（如果启用）
                    if search_depth > 1:
                        my_counter_moves = PossibleMove(Colour, opp_board)
                        if my_counter_moves:
                            best_counter_score = -10000000
                            for counter_move in my_counter_moves:
                                counter_board = BoardCopy(opp_board)
                                PlaceMove(Colour, counter_board, counter_move[0], counter_move[1])
                                counter_score = evaluate_position(Colour, counter_board, position_weights, total_moves + 2, empty_count - 2)
                                if counter_score > best_counter_score:
                                    best_counter_score = counter_score
                            # 减去我方最佳回应得分
                            opp_score -= best_counter_score * 0.3
                    
                    if opp_score > best_opp_score:
                        best_opp_score = opp_score
                
                # 减去对手的最佳得分
                score -= best_opp_score * 0.6
        
        # 加上位置权重和边缘奖励
        x, y = move
        position_score = position_weights[y-1][x-1]
        if move in edge_positions:
            position_score += 100  # 边缘位置奖励
        
        total_score = score + position_score
        
        # 更新最佳移动
        if total_score > best_score or best_move is None:
            best_score = total_score
            best_move = move
    
    return best_move

def endgame_optimization(Colour, Board):
    """终局优化：专注于最大化最终得分"""
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)
    
    best_score = -10000000
    best_move = None
    
    for move in moves:
        # 创建新棋盘并执行当前移动
        new_board = BoardCopy(Board)
        PlaceMove(Colour, new_board, move[0], move[1])
        
        # 计算最终得分潜力
        score = calculate_endgame_potential(Colour, new_board)
        
        # 更新最佳移动
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move

def calculate_endgame_potential(Colour, Board):
    """计算终局得分潜力"""
    # 1. 计算当前棋子差
    my_discs = 0
    opp_discs = 0
    for i in range(1, 9):
        for j in range(1, 9):
            if Board[i][j] == Colour:
                my_discs += 1
            elif Board[i][j] == -Colour:
                opp_discs += 1
    disc_diff = my_discs - opp_discs
    
    # 2. 计算移动性优势
    my_mobility = len(PossibleMove(Colour, Board))
    opp_mobility = len(PossibleMove(-Colour, Board))
    mobility_advantage = my_mobility - opp_mobility
    
    # 3. 计算角落控制
    corners = [(1,1), (1,8), (8,1), (8,8)]
    corner_control = 0
    for corner in corners:
        if Board[corner[0]][corner[1]] == Colour:
            corner_control += 1
        elif Board[corner[0]][corner[1]] == -Colour:
            corner_control -= 1
    
    # 4. 计算边缘控制
    edge_control = 0
    for i in range(1, 9):
        if Board[i][1] == Colour: edge_control += 1
        elif Board[i][1] == -Colour: edge_control -= 1
        if Board[i][8] == Colour: edge_control += 1
        elif Board[i][8] == -Colour: edge_control -= 1
        if Board[1][i] == Colour: edge_control += 1
        elif Board[1][i] == -Colour: edge_control -= 1
        if Board[8][i] == Colour: edge_control += 1
        elif Board[8][i] == -Colour: edge_control -= 1
    
    # 综合评分
    return disc_diff * 5 + mobility_advantage * 20 + corner_control * 200 + edge_control * 50

def evaluate_position(Colour, Board, position_weights, total_moves, empty_count):
    """
    优化评估函数：考虑更多因素
    """
    # 位置得分
    position_score = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Colour:
                position_score += position_weights[y-1][x-1]
            elif Board[x][y] == -Colour:
                position_score -= position_weights[y-1][x-1]
    
    # 移动性得分（更精确的计算）
    my_mobility = len(PossibleMove(Colour, Board))
    opp_mobility = len(PossibleMove(-Colour, Board))
    mobility_score = (my_mobility - opp_mobility) * 60
    
    # 稳定子识别（角落和边缘稳定子）
    stable_score = 0
    corners = [(1,1), (1,8), (8,1), (8,8)]
    for corner in corners:
        if Board[corner[0]][corner[1]] == Colour:
            stable_score += 500  # 占据角落非常有利
        elif Board[corner[0]][corner[1]] == -Colour:
            stable_score -= 500
    
    # 潜在移动性（可能成为移动的位置）
    potential_mobility = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Empty:
                neighbours = Neighbour(Board, x, y)
                if -Colour in neighbours:
                    potential_mobility += 1
    
    # 棋子差（考虑稳定子）
    my_discs = sum(row.count(Colour) for row in Board)
    opp_discs = sum(row.count(-Colour) for row in Board)
    disc_score = my_discs - opp_discs
    
    # 阶段调整的权重
    if total_moves < 15:  # 开局阶段
        return stable_score * 5 + mobility_score * 6 + potential_mobility * 25 + position_score * 0.8
    elif total_moves < 50:  # 中局阶段
        return stable_score * 3 + mobility_score * 7 + potential_mobility * 18 + disc_score * 2 + position_score * 1.2
    else:  # 残局阶段
        return stable_score * 1.5 + mobility_score * 4 + disc_score * 12 + position_score * 1.5