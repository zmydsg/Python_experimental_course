from Reversi import *

# 阶段划分阈值
EARLY_GAME = 20
MID_GAME = 36
LATE_GAME = 50

# 位置权重矩阵（强化边缘稳定性）
position_weight = [
    [3000, -800, 150, 60, 60, 150, -800, 3000],
    [-800, -1200, -80, -40, -40, -80, -1200, -800],
    [150,  -80,  50, 20, 20, 50,  -80, 150],
    [60,   -40,  20, -50, -50, 20, -40, 60],
    [60,   -40,  20, -50, -50, 20, -40, 60],
    [150,  -80,  50, 20, 20, 50,  -80, 150],
    [-800, -1200, -80, -40, -40, -80, -1200, -800],
    [3000, -800, 150, 60, 60, 150, -800, 3000]
]

# 特殊区域定义
corner = {(1,1), (1,8), (8,1), (8,8)}
edge_positions = {(x,y) for x in range(1,9) for y in range(1,9) if x in (1,8) or y in (1,8)}
danger_zone = {(1,2), (1,7), (2,1), (2,8), (7,1), (7,8), (8,2), (8,7),
               (2,2), (2,7), (7,2), (7,7), (3,3), (3,6), (6,3), (6,6)}
x_cells = {(2,2), (2,7), (7,2), (7,7)}  # X位

# 方向向量（8邻域）
DIRECTIONS = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]

# 稳定性加成系数
STABILITY_BONUS = [0, 5, 10, 20, 30]  # 不同稳定等级的奖励

def liberty_penalty(x, y, board):
    """计算棋子自由度惩罚（参考文档3）"""
    liberty = 0
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        if ValidCell(nx, ny) and board[nx][ny] == 0:
            liberty += 1
    return liberty * 8

def corner_control_score(board, colour):
    """计算角落控制分数"""
    score = 0
    corners = [(1,1), (1,8), (8,1), (8,8)]
    for (cx, cy) in corners:
        if board[cx][cy] == colour:
            score += 50  # 占据角落奖励
        elif board[cx][cy] == -colour:
            score -= 50   # 对手占据角落惩罚
            
        # 检查相邻位置
        for dx, dy in DIRECTIONS:
            nx, ny = cx + dx, cy + dy
            if ValidCell(nx, ny):
                if board[nx][ny] == colour:
                    score += 10  # 我方棋子靠近角落奖励
                elif board[nx][ny] == -colour:
                    score -= 10  # 对手棋子靠近角落惩罚
    return score

def stability_score(board, colour):
    """计算整体稳定性分数"""
    stable_score = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == colour:
                # 计算该棋子的稳定程度
                stable_count = 0
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    tx, ty = x, y
                    while ValidCell(tx, ty) and board[tx][ty] == colour:
                        tx += dx
                        ty += dy
                    if not ValidCell(tx, ty) or board[tx][ty] != 0:
                        stable_count += 1
                
                # 根据稳定程度给予奖励
                stability_level = min(stable_count, 4)
                stable_score += STABILITY_BONUS[stability_level]
                
            elif board[x][y] == -colour:
                # 对称扣除对手稳定性分数
                stable_count = 0
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    tx, ty = x, y
                    while ValidCell(tx, ty) and board[tx][ty] == -colour:
                        tx += dx
                        ty += dy
                    if not ValidCell(tx, ty) or board[tx][ty] != 0:
                        stable_count += 1
                
                stability_level = min(stable_count, 4)
                stable_score -= STABILITY_BONUS[stability_level]
    
    return stable_score

def player(Colour, Board):
    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves: 
        return (0, 0)
    
    empty_count = sum(row.count(0) for row in Board)
    game_phase = 64 - empty_count
    is_late = empty_count <= 12
    is_early = empty_count >= 40

    # ========== 终局强化策略 ==========
    if is_late:
        # 尝试寻找必胜落子
        for move in possible_moves:
            if move in corner:
                temp_board = BoardCopy(Board)
                PlaceMove(Colour, temp_board, *move)
                if not PossibleMove(-Colour, temp_board):
                    return move
        
        # 深度2搜索（当前落子+对手响应）
        best_endgame_score = -10**9
        best_endgame_move = possible_moves[0]
        
        for move in possible_moves:
            # 模拟当前落子
            temp_board = BoardCopy(Board)
            PlaceMove(Colour, temp_board, *move)
            
            # 评估对手最佳响应
            opp_moves = PossibleMove(-Colour, temp_board)
            if not opp_moves:
                # 无对手响应，直接评估局面
                score = board_evaluation(Colour, temp_board)
            else:
                min_opp_score = 10**9
                for opp_move in opp_moves:
                    opp_board = BoardCopy(temp_board)
                    PlaceMove(-Colour, opp_board, *opp_move)
                    opp_score = board_evaluation(Colour, opp_board)
                    if opp_score < min_opp_score:
                        min_opp_score = opp_score
                score = min_opp_score
            
            # 更新最佳落子
            if score > best_endgame_score:
                best_endgame_score = score
                best_endgame_move = move
        
        return best_endgame_move

    # ========== 中早期策略（优化多因素评分） ==========
    
    # 动态威胁矩阵
    threat_matrix = [[0]*9 for _ in range(9)]
    for x in range(1,9):
        for y in range(1,9):
            if Board[x][y] == 0:
                temp_board = BoardCopy(Board)
                PlaceMove(Colour, temp_board, x, y)
                for dx, dy in NeighbourPosition:
                    nx, ny = x+dx, y+dy
                    if ValidCell(nx, ny) and temp_board[nx][ny] == -Colour:
                        threat_matrix[x][y] += 1
    
    # 动态权重系统
    weight_factors = [
        (position_weight[x-1][y-1], 1.0),          # 基础位置权重
        (threat_matrix[x-1][y-1], 0.8 if game_phase>32 else 1.2),  # 动态威胁系数
        (liberty_penalty(x, y, Board), -0.5),       # 新增：自由度惩罚
        (len(PossibleMove(Colour, Board)), 0.4),    # 自身移动性
        (len(PossibleMove(-Colour, Board)), -0.3),  # 对手移动性
        (corner_control_score(Board, Colour), 0.2), # 新增：角落控制
        (stability_score(Board, Colour), 0.3)       # 新增：稳定性评估
    ]
    
    best_score = -10**9
    best_move = possible_moves[0]
    
    for move in possible_moves:
        x, y = move
        score = 0
        
        # 多因素综合评分
        for (factor, coeff) in weight_factors:
            score += factor * coeff
        
        # 特殊位置处理
        if (x,y) in corner:
            score += 1000  # 角落奖励
        elif (x,y) in x_cells:
            score -= 300   # X位惩罚（文档3关键策略）
        elif (x,y) in danger_zone:
            score -= 150 * (1 + game_phase//20)  # 危险区域惩罚
        
        # 早期策略调整
        if is_early:
            # 随机性策略
            if 2 <= x <= 7 and 2 <= y <= 7 and random.random() < 0.3:
                score *= 1.5
        
        # 更新最佳落子
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move

def board_evaluation(Colour, Board):
    """综合局面评估函数"""
    # 1. 棋子数量差
    my_count = 0
    opp_count = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Colour:
                my_count += 1
            elif Board[x][y] == -Colour:
                opp_count += 1
    piece_diff = my_count - opp_count
    
    # 2. 位置权重总分
    position_score = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Colour:
                position_score += position_weight[x-1][y-1]
            elif Board[x][y] == -Colour:
                position_score -= position_weight[x-1][y-1]
    
    # 3. 移动性
    mobility = len(PossibleMove(Colour, Board)) - len(PossibleMove(-Colour, Board))
    
    # 4. 稳定性和控制
    stability = stability_score(Board, Colour)
    corner_control = corner_control_score(Board, Colour)
    
    # 综合评分
    return piece_diff * 5 + position_score + mobility * 20 + stability + corner_control