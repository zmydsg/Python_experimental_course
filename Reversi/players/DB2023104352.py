import random
from Reversi import *

def player(Colour, Board):
    # 预定义静态评估参数
    POSITION_WEIGHTS = [
        [600, -50, 30, 15, 15, 30, -50, 600],
        [-50, -80, -5, -3, -3, -5, -80, -50],
        [30, -5,  2,  1,  1,  2, -5, 30],
        [15, -3,  1,  1,  1,  1, -3, 15],
        [15, -3,  1,  1,  1,  1, -3, 15],
        [30, -5,  2,  1,  1,  2, -5, 30],
        [-50, -80, -5, -3, -3, -5, -80, -50],
        [600, -50, 30, 15, 15, 30, -50, 600]
    ]
    
    # 阶段识别：根据已落子数动态调整策略
    total_pieces = sum(row.count(Black) + row.count(White) for row in Board)
    game_phase = 'opening' if total_pieces < 20 else 'midgame' if total_pieces < 50 else 'endgame'
    
    def get_phase_weights():
        '''动态调整权重系数，基于游戏阶段优化策略'''
        return {
            'opening': {'position': 4.0, 'flip': 0.5, 'opponent': 1.5},  # 强化位置权重
            'midgame': {'position': 1.8, 'flip': 2.2, 'opponent': 1.8},  # 平衡发展与控制
            'endgame': {'position': 0.8, 'flip': 3.0, 'opponent': 2.5}   # 最大化翻转和限制
        }[game_phase]

    def evaluate_corner_control(x, y, Board, Colour):
        '''增强版角落控制评估，包含周边位置风险评估'''
        corners = [(1,1), (1,8), (8,1), (8,8)]
        c_squares = [(1,2), (2,1), (1,7), (7,1), (2,8), (8,2), (7,8), (8,7)]  # C位
        x_squares = [(2,2), (2,7), (7,2), (7,7)]  # X位
    
        # 1. 直接占领角落 - 最高优先级
        if (x, y) in corners:
            return 800  # 提高角落价值
    
        # 2. 占领安全边位置 - 高价值
        safe_edges = []
        for c in corners:
            if Board[c[0]-1][c[1]-1] == Colour:  # 角落已被己方控制
                # 添加相邻边位置
                if c == (1,1):
                    safe_edges.extend([(1,3),(1,4),(3,1),(4,1)])
                elif c == (1,8):
                    safe_edges.extend([(1,6),(1,5),(3,8),(4,8)])
                elif c == (8,1):
                    safe_edges.extend([(8,3),(8,4),(6,1),(5,1)])
                elif c == (8,8):
                    safe_edges.extend([(8,6),(8,5),(6,8),(5,8)])
    
        if (x, y) in safe_edges:
            return 120  # 安全边位置奖励
    
        # 3. 危险位置惩罚 - 避免X位和C位
        penalty = 0
        if (x, y) in x_squares:
            penalty -= 350  # X位高风险
        
        elif (x, y) in c_squares:
            # 只有当角落为空时才惩罚C位
            for cx, cy in corners:
                if Board[cx-1][cy-1] == Empty:
                    penalty -= 180  # C位中等风险
                    break
    
        # 4. 角落攻击潜力 - 通往角落的路径
        attack_bonus = 0
        for cx, cy in corners:
            if Board[cx-1][cy-1] == Empty:  # 角落尚未被占领
                # 计算当前位置到角落的路径控制
                if (abs(x - cx) <= 2 and y == cy) or (abs(y - cy) <= 2 and x == cx):
                    attack_bonus += 60  # 直线攻击路径
                elif abs(x - cx) == abs(y - cy):
                    attack_bonus += 40  # 对角线攻击路径
    
        return penalty + attack_bonus

    def evaluate_flip_potential(x, y, Board, Colour):
        '''增强版翻转潜力评估：考虑质量、稳定性和战略价值'''
        temp_board = BoardCopy(Board)
        temp_board = PlaceMove(Colour, temp_board, x, y)
    
        # 1. 基础翻转数量
        basic_flips = sum(row.count(Colour) for row in temp_board) - sum(row.count(Colour) for row in Board)
    
        # 2. 翻转质量评估矩阵（位置价值）
        FLIP_QUALITY_WEIGHTS = [
            [4.0, 0.8, 1.2, 1.0, 1.0, 1.2, 0.8, 4.0],
            [0.8, 0.6, 0.7, 0.7, 0.7, 0.7, 0.6, 0.8],
            [1.2, 0.7, 1.0, 0.9, 0.9, 1.0, 0.7, 1.2],
            [1.0, 0.7, 0.9, 1.0, 1.0, 0.9, 0.7, 1.0],
            [1.0, 0.7, 0.9, 1.0, 1.0, 0.9, 0.7, 1.0],
            [1.2, 0.7, 1.0, 0.9, 0.9, 1.0, 0.7, 1.2],
            [0.8, 0.6, 0.7, 0.7, 0.7, 0.7, 0.6, 0.8],
            [4.0, 0.8, 1.2, 1.0, 1.0, 1.2, 0.8, 4.0]
        ]
    
        # 3. 识别被翻转的棋子位置
        flipped_positions = []
        for i in range(8):
            for j in range(8):
                if Board[i][j] == -Colour and temp_board[i][j] == Colour:
                    flipped_positions.append((i, j))
    
        # 4. 计算加权翻转价值
        quality_value = 0
        for i, j in flipped_positions:
            quality_value += FLIP_QUALITY_WEIGHTS[i][j]
    
        # 5. 稳定性评估：翻转后形成稳定棋子的比例
        stable_pieces = 0
        corner_adjacent = {(0,1), (1,0), (0,6), (6,0), (1,7), (7,1), (6,7), (7,6)}
        for i, j in flipped_positions:
            # 角落位置总是稳定的
            if (i,j) in {(0,0), (0,7), (7,0), (7,7)}:
                stable_pieces += 1
            # 边缘位置且与角落相连
            elif i == 0 or i == 7 or j == 0 or j == 7:
                if (i,j) not in corner_adjacent:  # 避开C位
                    stable_pieces += 0.8
    
        stability_factor = stable_pieces / len(flipped_positions) if flipped_positions else 0
    
        # 6. 战略价值：关键位置翻转奖励
        strategic_bonus = 0
        corner_positions = {(0,0), (0,7), (7,0), (7,7)}
        edge_positions = {(i,j) for i in [0,7] for j in range(8)} | {(i,j) for j in [0,7] for i in range(8)}
    
        for pos in flipped_positions:
            if pos in corner_positions:
                strategic_bonus += 3.0  # 角落翻转价值最高
            elif pos in edge_positions:
                strategic_bonus += 1.5  # 边缘位置次之
    
        # 7. 综合翻转潜力 = 基础数量 × 质量系数 × 稳定性系数 + 战略奖励
        return (basic_flips * quality_value * (1 + stability_factor) + strategic_bonus)

    def evaluate_opponent_limit(x, y, Board, Colour):
        '''增强版对手限制评估：考虑移动质量、战略价值和潜在威胁'''
        # 1. 模拟当前落子后的棋盘
        temp_board = PlaceMove(Colour, BoardCopy(Board), x, y)
        opponent_moves = PossibleMove(-Colour, temp_board)
        opponent_mobility = len(opponent_moves)
    
        # 2. 移动质量评估矩阵（对手视角）
        OPPONENT_MOVE_QUALITY = [
            [-20, 15, 5, 3, 3, 5, 15, -20],   # 角落价值最高（负值表示限制成功）
            [15, 8, 2, 1, 1, 2, 8, 15],      # 边缘位置中等价值
            [5, 2, 1, 0, 0, 1, 2, 5],         # 次边缘位置低价值
            [3, 1, 0, 0, 0, 0, 1, 3],         # 中心位置最低价值
            [3, 1, 0, 0, 0, 0, 1, 3],
            [5, 2, 1, 0, 0, 1, 2, 5],
            [15, 8, 2, 1, 1, 2, 8, 15],
            [-20, 15, 5, 3, 3, 5, 15, -20]
        ]
    
        # 3. 计算对手移动质量总分
        opponent_quality = 0
        for move in opponent_moves:
            i, j = move[0]-1, move[1]-1  # 转换为0-based索引
            opponent_quality += OPPONENT_MOVE_QUALITY[i][j]
    
        # 4. 关键位置控制评估
        critical_threat = 0
        corner_positions = [(1,1), (1,8), (8,1), (8,8)]
        for move in opponent_moves:
            # 对手可能占领角落的威胁
            if move in corner_positions:
                critical_threat += 50  # 严重威胁
        
            # 对手可能形成边缘控制的威胁
            if move[0] in [1,8] or move[1] in [1,8]:
                critical_threat += 10
    
        # 5. 连锁反应风险评估
        chain_reaction_risk = 0
        for move in opponent_moves:
            # 模拟对手走这步棋
            next_temp = PlaceMove(-Colour, BoardCopy(temp_board), move[0], move[1])
            # 计算对手走这步后我们的行动力
            our_next_moves = len(PossibleMove(Colour, next_temp))
            # 如果对手的移动会严重限制我们下一步的行动力
            if our_next_moves <= 2:  # 极低行动力
                chain_reaction_risk += 30
            elif our_next_moves <= 4:  # 低行动力
                chain_reaction_risk += 15
    
        # 6. 动态威胁系数（基于游戏阶段）
        game_phase = 'opening' if sum(row.count(Black)+row.count(White) for row in Board) < 20 else 'midgame' if total_pieces < 50 else 'endgame'
        threat_weights = {
            'opening': {'mobility': 0.8, 'quality': 1.2, 'critical': 1.5, 'chain': 0.8},
            'midgame': {'mobility': 1.2, 'quality': 1.5, 'critical': 1.8, 'chain': 1.2},
            'endgame': {'mobility': 1.5, 'quality': 1.0, 'critical': 2.0, 'chain': 1.5}
        }[game_phase]
    
        # 7. 综合对手限制评分
        mobility_score = opponent_mobility * threat_weights['mobility']
        quality_score = opponent_quality * threat_weights['quality']
        critical_score = critical_threat * threat_weights['critical']
        chain_score = chain_reaction_risk * threat_weights['chain']
    
        return mobility_score + quality_score + critical_score + chain_score

    legal_moves = PossibleMove(Colour, Board)
    if not legal_moves:
        return (0, 0)

    scores = []
    weights = get_phase_weights()
    
    for move in legal_moves:
        x, y = move
        
        # 综合评估要素
        position_score = POSITION_WEIGHTS[x-1][y-1] * weights['position']
        flip_score = evaluate_flip_potential(x, y, Board, Colour) * weights['flip']
        corner_bonus = evaluate_corner_control(x, y, Board, Colour)
        opponent_penalty = evaluate_opponent_limit(x, y, Board, Colour) * weights['opponent']
        
        # 最终评分公式
        total_score = position_score + flip_score + corner_bonus - opponent_penalty
        scores.append(total_score)

    # 选择最优解（带随机性）
    max_score = max(scores)
    best_candidates = [move for move, score in zip(legal_moves, scores) if score == max_score]
    best_move = random.choice(best_candidates)
    
    # 最终合法性验证
    return best_move if best_move in legal_moves else (0, 0)