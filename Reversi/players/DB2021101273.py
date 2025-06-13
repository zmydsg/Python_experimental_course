from Reversi import *

# ---------------------- 全局定义 ----------------------
CORNER_POSITIONS = {(1, 1), (1, 8), (8, 1), (8, 8)}
DANGER_ZONES = {(2, 2), (2, 7), (7, 2), (7, 7)}
EDGE_POSITIONS = {(1, i) for i in range(1, 9)} | {(8, i) for i in range(1, 9)} | \
                 {(i, 1) for i in range(2, 8)} | {(i, 8) for i in range(2, 8)}
ADJACENT_TO_CORNERS = {(1,2), (2,1), (1,7), (2,8), (7,1), (8,2), (7,8), (8,7)}

# ---------------------- 动态权重计算 ----------------------
def calculate_position_weight(x, y, total_pieces):
    # 基础权重基于位置类型计算
    if (x, y) in CORNER_POSITIONS:
        return 100  # 角落最高价值
        
    if (x, y) in DANGER_ZONES:
        return -80  # 危险区域负权重
        
    if (x, y) in EDGE_POSITIONS:
        # 边缘价值根据位置调整
        if x in (1, 8) or y in (1, 8):
            return 20 - abs(4.5 - x if x in (1,8) else 4.5 - y)
        return 15
        
    if (x, y) in ADJACENT_TO_CORNERS:
        return -60  # 角落相邻位置惩罚
    
    # 中心区域权重根据距离角落的距离计算
    distance_from_edge = min(min(x-1, 8-x), min(y-1, 8-y))
    if distance_from_edge < 3:  # 靠边位置
        return 5 + distance_from_edge * 2
    
    # 真正中心位置的价值基于游戏阶段调整
    core_value = 10 if total_pieces > 40 else 3  # 后期中心更有价值
    return core_value

# ---------------------- 核心函数 ----------------------
def evaluate_position_score(Colour, Board, move):
    """评估移动位置的综合得分"""
    x, y = move
    total_pieces = count_pieces(Board)
    
    # 动态计算位置权重
    position_score = calculate_position_weight(x, y, total_pieces)
    
    # 翻转收益计算（实际翻转棋子数）
    flip_count = calculate_real_flips(Colour, Board, x, y)
    
    # 翻转收益权重基于游戏阶段调整
    flip_weight = 1.5 if total_pieces < 20 else 3.0 if total_pieces < 40 else 4.0
    flip_score = flip_count * flip_weight
    
    # 模拟落子后的对手移动评估
    temp_board = BoardCopy(Board)
    PlaceMove(Colour, temp_board, x, y)
    opponent_moves = PossibleMove(-Colour, temp_board)
    opponent_mobility = len(opponent_moves)
    
    # 对手行动惩罚基于游戏阶段调整
    mobility_penalty = opponent_mobility * (0.8 if total_pieces < 30 else 1.2)
    
    return position_score + flip_score - mobility_penalty

def calculate_real_flips(Colour, Board, x, y):
    """精确计算实际翻转棋子数"""
    temp_board = BoardCopy(Board)
    original_count = count_player_pieces(Colour, temp_board)
    PlaceMove(Colour, temp_board, x, y)
    new_count = count_player_pieces(Colour, temp_board)
    return new_count - original_count - 1  # 减去自身落子

def count_pieces(Board):
    """统计棋盘总棋子数"""
    return sum(row.count(1) + row.count(-1) for row in Board)

def count_player_pieces(Colour, Board):
    """统计指定玩家的棋子数"""
    return sum(row.count(Colour) for row in Board)

def prevents_corner_opportunity(Colour, Board, move):
    """判断落子是否会阻止对手占据角落的机会"""
    x, y = move
    for cx, cy in CORNER_POSITIONS:
        if Board[cx][cy] == 0:  # 角落尚未被占据
            # 检查当前落子是否会阻挡通往角落的路径
            if (x == cx and abs(y - cy) < 2) or (y == cy and abs(x - cx) < 2):
                return 25  # 阻止机会加分
    
    return -10 if gives_corner_opportunity(Board, Colour, move) else 0

def gives_corner_opportunity(Board, Colour, move):
    """判断落子是否会给对手创造占角机会"""
    temp_board = BoardCopy(Board)
    PlaceMove(Colour, temp_board, move[0], move[1])
    return any(m in CORNER_POSITIONS for m in PossibleMove(-Colour, temp_board))

# ---------------------- 主策略函数 ----------------------
def player(Colour, Board):
    """优化后的AI策略主函数"""
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)
    
    # 1. 绝对占角优先
    corner_moves = [m for m in moves if m in CORNER_POSITIONS]
    if corner_moves:
        return corner_moves[0]  # 选择第一个可用的角落
    
    # 2. 高价值位置优先（避免高风险位置）
    safe_moves = [m for m in moves if m not in DANGER_ZONES]
    if not safe_moves:
        safe_moves = moves  # 如果没有更安全的，就只能选危险区域了
    
    # 3. 综合评估所有可行移动
    best_score = float('-inf')
    best_move = None
    
    for move in safe_moves:
        score = evaluate_position_score(Colour, Board, move)
        
        # 避免给对手创造占角机会
        if gives_corner_opportunity(Board, Colour, move):
            score -= 75  # 高风险惩罚
        else:
            # 阻挡对手占角奖励
            score += prevents_corner_opportunity(Colour, Board, move)
            
            # 位置安全奖励
            if move not in DANGER_ZONES:
                score += 15
        
        # 更新最佳移动
        if score > best_score or (score == best_score and not best_move):
            best_score = score
            best_move = move
    
    return best_move or safe_moves[0]

