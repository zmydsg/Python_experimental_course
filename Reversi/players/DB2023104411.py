from Reversi import *

def player(Colour, Board):
    """主函数：根据当前棋盘状态和玩家颜色，返回最佳落子位置"""
    a = PossibleMove(Colour, Board)  # 获取所有合法移动
    l = len(a)  # 合法移动数量
    if l > 0:
        best_move = select_best_move(a, Colour, Board)  # 调用核心策略子程序
        return best_move
    else:
        return (0, 0)  # 无合法移动时返回默认值

def select_best_move(moves, player, board):
    """核心策略子程序：综合多维度评估，选择最佳落子方案"""
    # ---------------------- 分阶段位置价值评估 ----------------------
    # 早期阶段（总棋子数 < 20）：中间区域价值较低，侧重边角控制
    POSITION_VALUES_EARLY = {
        # 四角（最高优先级，控制四角可大幅限制对手翻转）
        (1, 1): 100, (1, 8): 100, (8, 1): 100, (8, 8): 100,
        # 三边安全边缘（连接四角的边缘，次优先级，形成连续链后强化控制）
        (1, 3): 40, (1, 4): 40, (1, 5): 40, (1, 6): 40,
        (8, 3): 40, (8, 4): 40, (8, 5): 40, (8, 6): 40,
        (3, 1): 40, (4, 1): 40, (5, 1): 40, (6, 1): 40,
        (3, 8): 40, (4, 8): 40, (5, 8): 40, (6, 8): 40,
        # 危险位置（易被对手利用翻转四角，负分抑制落子）
        (2, 2): -50, (2, 7): -50, (7, 2): -50, (7, 7): -50,
        (1, 2): -30, (1, 7): -30, (2, 1): -30, (2, 8): -30,
        (7, 1): -30, (7, 8): -30, (8, 2): -30, (8, 7): -30,
        # 中间区域（早期相对重要，但优先级低于边缘，分值适中）
        (3, 3): 20, (3, 4): 20, (3, 5): 20, (3, 6): 20,
        (4, 3): 20, (4, 4): 20, (4, 5): 20, (4, 6): 20,
        (5, 3): 20, (5, 4): 20, (5, 5): 20, (5, 6): 20,
        (6, 3): 20, (6, 4): 20, (6, 5): 20, (6, 6): 20
    }
    
    # 中期阶段（20 ≤ 总棋子数 < 50）：中间区域价值提升，鼓励中心扩张
    POSITION_VALUES_MID = {
        **POSITION_VALUES_EARLY,  # 继承早期阶段的非中间区域配置
        # 中间区域分值提升，反映中期对中心控制的需求
        (3, 3): 30, (3, 4): 30, (3, 5): 30, (3, 6): 30,
        (4, 3): 30, (4, 4): 30, (4, 5): 30, (4, 6): 30,
        (5, 3): 30, (5, 4): 30, (5, 5): 30, (5, 6): 30,
        (6, 3): 30, (6, 4): 30, (6, 5): 30, (6, 6): 30
    }
    
    # 晚期阶段（总棋子数 ≥ 50）：中间区域价值降低，侧重稳定现有优势
    POSITION_VALUES_LATE = {
        **POSITION_VALUES_EARLY,  # 继承早期阶段的非中间区域配置
        # 中间区域分值降低，策略转向维持边缘控制
        (3, 3): 10, (3, 4): 10, (3, 5): 10, (3, 6): 10,
        (4, 3): 10, (4, 4): 10, (4, 5): 10, (4, 6): 10,
        (5, 3): 10, (5, 4): 10, (5, 5): 10, (5, 6): 10,
        (6, 3): 10, (6, 4): 10, (6, 5): 10, (6, 6): 10
    }
    
    # 根据总棋子数判断游戏阶段，选择对应的位置价值表
    total_pieces = sum([sum([abs(cell) for cell in row]) for row in board])
    if total_pieces < 20:
        position_values = POSITION_VALUES_EARLY
    elif total_pieces < 50:
        position_values = POSITION_VALUES_MID
    else:
        position_values = POSITION_VALUES_LATE
    
    # ---------------------- 综合得分计算 ----------------------
    move_scores = []
    for (x, y) in moves:
        score = 0
        
        # 1. 位置价值分（四角 > 三边边缘 > 中间 > 危险位置）
        score = position_values.get((x, y), 10)  # 未定义位置默认10分
        
        # 2. 三边连续占领加分（连接四角的边缘链，增强布局稳定性）
        if is_edge_chain(x, y, player, board):
            score += 15  # 连续三边位置加15分
        
        # 3. 限制对手行动力（模拟落子后对手的合法移动数越少，加分越高）
        temp_board = BoardCopy(board)
        temp_board = PlaceMove(player, temp_board, x, y)  # 模拟落子
        opponent_moves = len(PossibleMove(-player, temp_board))  # 计算对手合法移动数
        score += max(0, 20 - opponent_moves)  # 最多加20分，最低0分
        
        # 4. 稳定子评估（稳定子越多，后期优势越明显）
        stable_pieces = count_stable_pieces(temp_board, player)
        score += stable_pieces * 5  # 每个稳定子加5分
        
        move_scores.append((score, x, y))
    
    # ---------------------- 排序与选择最佳移动 ----------------------
    # 按得分降序排序，得分相同则按坐标升序排列（确保决策一致性）
    move_scores.sort(key=lambda x: (-x[0], x[1], x[2]))
    return (move_scores[0][1], move_scores[0][2])  # 返回最高分移动坐标

def is_edge_chain(x, y, player, board):
    """判断当前位置是否属于连续的三边链（连接两个角落的边缘）"""
    # 定义四边的中间段位置（三边链区域，非角落和边缘端点）
    is_top_edge = (x == 1) and (3 <= y <= 6)  # 上边中间段（y=3-6）
    is_bottom_edge = (x == 8) and (3 <= y <= 6)  # 下边中间段
    is_left_edge = (y == 1) and (3 <= x <= 6)  # 左边中间段（x=3-6）
    is_right_edge = (y == 8) and (3 <= x <= 6)  # 右边中间段
    
    if not (is_top_edge or is_bottom_edge or is_left_edge or is_right_edge):
        return False  # 非三边链位置，直接返回
    
    # 获取相邻的三边链位置（上下左右相邻的边缘中间段）
    adjacent_positions = []
    if is_top_edge or is_bottom_edge:
        # 上下边的相邻位置为左右两侧（y±1）
        adjacent_positions = [(x, y - 1), (x, y + 1)]
    else:
        # 左右边的相邻位置为上下两侧（x±1）
        adjacent_positions = [(x - 1, y), (x + 1, y)]
    
    # 统计相邻位置中己方棋子的数量（至少1个即视为连续链）
    chain_count = 0
    for (px, py) in adjacent_positions:
        if ValidCell(px, py) and board[px][py] == player:
            chain_count += 1
    return chain_count >= 1

def count_stable_pieces(board, player):
    """计算当前棋盘中玩家的稳定子数量"""
    stable_count = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == player and is_stable(board, player, x, y):
                stable_count += 1
    return stable_count

def is_stable(board, player, x, y):
    """判断单个棋子是否为稳定子（四周均为己方棋子或棋盘边界）"""
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # 上下左右四个方向
    for dx, dy in directions:
        px, py = x, y
        while True:
            px += dx
            py += dy
            if not ValidCell(px, py):  # 超出棋盘范围，视为边界保护
                break
            if board[px][py] != player:  # 遇到非己方棋子，判定不稳定
                return False
    return True  # 所有方向均为己方棋子或边界，判定为稳定子