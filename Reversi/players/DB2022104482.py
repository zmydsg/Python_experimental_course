import time
from Reversi import PossibleMove, BoardCopy, PlaceMove # 
import random

# --- 定位权重表 ---
# 这些权重用于评估棋盘上每个位置的静态价值。角点价值最高，角点旁边的X和C格价值为负。
POSITION_WEIGHTS = [
    [1000, -300, 100, 80, 80, 100, -300, 1000],
    [-300, -500, -50, -20, -20, -50, -500, -300],
    [100,  -50,  30,  10,  10,  30,  -50,  100],
    [80,   -20,  10,   5,   5,  10,  -20,   80],
    [80,   -20,  10,   5,   5,  10,  -20,   80],
    [100,  -50,  30,  10,  10,  30,  -50,  100],
    [-300, -500, -50, -20, -20, -50, -500, -300],
    [1000, -300, 100, 80, 80, 100, -300, 1000]
]

# --- 评估函数各项权重 ---
MOBILITY_WEIGHT = 90       # 行动力权重，衡量可选步数的多少
POSITIONAL_WEIGHT = 10     # 位置权重，基于POSITION_WEIGHTS表
CORNER_WEIGHT = 1500       # 角点特殊权重
# STABILITY_WEIGHT REMOVED - 角点的稳定性主要由CORNER_WEIGHT和POSITION_WEIGHTS覆盖
FRONTIER_WEIGHT = 75       # 前沿子权重，鼓励减少我方的前沿子（不易被翻的棋子）
PARITY_WEIGHT = 150        # 棋子差异权重，衡量双方棋子数量的差异

# --- 时间限制 ---
# 硬性时间限制：每一步搜索不得超过此时间（秒）
HARD_TIME_LIMIT_PER_MOVE = 0.01
# 迭代加深最大深度：一个较高的值，实际搜索深度由时间限制控制
ITERATIVE_DEEPENING_MAX_DEPTH = 15 

# --- 启发式搜索辅助数据结构 ---
# 历史表：记录在特定位置下棋导致剪枝的好坏程度，用于改进排序
HISTORY_TABLE = [[0] * 8 for _ in range(8)]
# 杀手着法表：记录在特定深度下导致beta剪枝的走法
KILLER_MOVES = {} # 格式: {depth: {1: move1, 2: move2}}

# --- 特殊位置定义 (1-indexed) ---
CORNERS = {(1, 1), (1, 8), (8, 1), (8, 8)}
# C格：角点旁边的格子（非对角线方向）
C_SQUARES = {(1, 2), (2, 1), (1, 7), (2, 8), (7, 1), (8, 2), (7, 8), (8, 7)}
# X格：角点斜向相邻的格子
X_SQUARES = {(2, 2), (2, 7), (7, 2), (7, 7)}
# 危险区域：C格和X格的并集，通常是不利的下棋位置，除非角点已被己方占据
DANGER_ZONES = C_SQUARES | X_SQUARES

# --- Zobrist Hashing for Transposition Table ---
# Zobrist表：为棋盘上每个位置的每种棋子状态（黑、白）生成一个随机哈希码
ZOBRIST_TABLE = [[[0]*3 for _ in range(8)] for _ in range(8)] # row, col, piece_type (0:empty, 1:player1, 2:player2)
# Zobrist码：用于当前轮到谁走棋
ZOBRIST_PLAYER_TURN = 0
# 置换表：存储已搜索过的棋局状态及其评估结果，避免重复计算
TRANSPOSITION_TABLE = {} # 格式: {hash_value: (score, depth, flag, best_move)}
# 置换表条目标记
TT_EXACT = 0      # 精确值
TT_LOWERBOUND = 1 # 下界值 (alpha)
TT_UPPERBOUND = 2 # 上界值 (beta)

def init_zobrist():
    """初始化Zobrist哈希码表。在程序开始时调用一次。"""
    global ZOBRIST_PLAYER_TURN
    for r in range(8): # 0-7 for ZOBRIST_TABLE
        for c in range(8): # 0-7 for ZOBRIST_TABLE
            ZOBRIST_TABLE[r][c][1] = random.getrandbits(64) # 玩家1 
            ZOBRIST_TABLE[r][c][2] = random.getrandbits(64) # 玩家2 
    ZOBRIST_PLAYER_TURN = random.getrandbits(64)

init_zobrist() # 程序启动时初始化

def compute_board_hash(board, player_to_move_color):
    """计算当前棋盘状态的Zobrist哈希值。"""
    h = 0
    for r_idx in range(8): # ZOBRIST_TABLE 使用0-7索引
        for c_idx in range(8): # ZOBRIST_TABLE 使用0-7索引
            piece = board[r_idx+1][c_idx+1] # 假设棋盘 board 是1-indexed
            if piece == 1: # 黑色 (映射到 ZOBRIST_TABLE 索引 1)
                h ^= ZOBRIST_TABLE[r_idx][c_idx][1]
            elif piece == -1: # 白色 (映射到 ZOBRIST_TABLE 索引 2)
                h ^= ZOBRIST_TABLE[r_idx][c_idx][2]
    
    # 将当前轮到谁走棋也加入哈希计算，区分相同棋盘但不同走棋方的情况
    if player_to_move_color == 1: # 假设玩家1 (黑棋)
        h ^= ZOBRIST_PLAYER_TURN
    # 如果 player_to_move_color == -1 (白棋)，则不异或，或者异或另一个值。
    # 当前实现：只有一方的turn会异或一个特定值。
    # 确保这种表示与游戏中player_color的表示一致。
    return h

def get_game_phase(board):
    """简单判断游戏阶段：早期、中期、晚期。用于动态调整评估权重。"""
    num_pieces = 0
    for r in range(1, 9):
        for c in range(1, 9):
            if board[r][c] != 0:
                num_pieces += 1
    
    empty_cells = 64 - num_pieces
    if empty_cells > 40: return "early"  # 例如，超过40个空格认为是早期
    if empty_cells > 12: return "mid"    # 13-40个空格认为是中期
    return "late"                       # 少于等于12个空格认为是晚期 (更强调子差)


def evaluate_board(board, player_color, player_moves, opponent_moves):
    """
    评估当前棋盘状态的分数。
    分数是正的表示对 player_color 有利，负的表示不利。
    player_moves: player_color 在当前局面下的合法走法列表
    opponent_moves: player_color的对手 在当前局面下的合法走法列表
    """
    opponent_color = -player_color
    player_pieces = 0
    opponent_pieces = 0
    player_positional = 0
    opponent_positional = 0
    player_frontier = 0
    opponent_frontier = 0
    player_corners_captured = 0 # 我方占领的角点数
    opponent_corners_captured = 0 # 对方占领的角点数
    
    # 统计棋子数量、位置价值、角点占有和前沿子数量
    for r in range(1, 9): # 棋盘是1-indexed
        for c in range(1, 9):
            piece = board[r][c]
            if piece == 0:
                continue
            
            weight = POSITION_WEIGHTS[r-1][c-1] # 权重表是0-indexed
            
            if piece == player_color:
                player_pieces += 1
                player_positional += weight
                if (r, c) in CORNERS:
                    player_corners_captured += 1
            else:
                opponent_pieces += 1
                opponent_positional += weight
                if (r, c) in CORNERS:
                    opponent_corners_captured += 1
            
            # 检测是否为前沿子 (周围有空格的棋子)
            is_frontier = False
            for dr_ in (-1, 0, 1):
                for dc_ in (-1, 0, 1):
                    if dr_ == 0 and dc_ == 0:
                        continue
                    nr, nc = r + dr_, c + dc_
                    if 1 <= nr <= 8 and 1 <= nc <= 8 and board[nr][nc] == 0:
                        is_frontier = True
                        break
                if is_frontier:
                    break
            
            if is_frontier:
                if piece == player_color:
                    player_frontier += 1
                else:
                    opponent_frontier += 1
    
    # 1. 位置价值分
    positional_score = (player_positional - opponent_positional) * POSITIONAL_WEIGHT
    
    # 2. 角点控制分
    corner_score = (player_corners_captured - opponent_corners_captured) * CORNER_WEIGHT
    
    # 3. 前沿子分 (我方前沿子越少越好)
    frontier_score = (opponent_frontier - player_frontier) * FRONTIER_WEIGHT
    
    # 4. 行动力分
    player_moves_count = len(player_moves)
    opponent_moves_count = len(opponent_moves) # 需要传入对手的合法走法
    
    mobility_score_val = 0
    # 游戏结束判断：如果双方都没有合法走法
    if player_moves_count == 0 and opponent_moves_count == 0:
        # 游戏结束，直接根据子数多少决定胜负，给予极高/极低分
        if player_pieces > opponent_pieces:
            return 1000000 + (player_pieces - opponent_pieces) * 100 # 赢棋，分数与子差相关
        elif opponent_pieces > player_pieces:
            return -1000000 + (player_pieces - opponent_pieces) * 100 # 输棋
        else:
            return 0 # 平局
    
    # 动态调整权重
    current_parity_weight = PARITY_WEIGHT
    current_mobility_weight = MOBILITY_WEIGHT
    current_positional_weight_multiplier = 1.0

    phase = get_game_phase(board)
    if phase == "early":
        current_parity_weight *= 0.3       # 开局，棋子数量不那么重要
        current_mobility_weight *= 1.5     # 开局，行动力更重要
        current_positional_weight_multiplier = 1.2 # 开局，位置更重要
    elif phase == "mid":
        current_parity_weight *= 1.0
        current_mobility_weight *= 1.0
        current_positional_weight_multiplier = 1.0
    elif phase == "late": # late game
        current_parity_weight *= 2.5       # 残局，棋子数量非常重要
        current_mobility_weight *= 0.6     # 残局，行动力相对次要，除非能限制死对方
        current_positional_weight_multiplier = 0.8 # 残局，固定位置价值略微下降，子数更关键

    # 重新计算位置分 (应用阶段性乘数)
    positional_score = (player_positional - opponent_positional) * POSITIONAL_WEIGHT * current_positional_weight_multiplier

    # 用动态权重计算行动力分
    if player_moves_count + opponent_moves_count > 0: # 避免除以零
         mobility_score_val = (player_moves_count - opponent_moves_count) * current_mobility_weight
    # (游戏结束情况已在前面处理)

    # 5. 棋子差异分 (奇偶性)
    parity_score_val = (player_pieces - opponent_pieces) * current_parity_weight
    
    total_score = (
        positional_score + 
        corner_score + 
        frontier_score + 
        mobility_score_val + 
        parity_score_val
    )
    
    return total_score


def get_sorted_moves(board, possible_moves, player_color, depth, tt_best_move=None):
    """
    改进的移动排序：结合多种启发式方法。
    depth: 当前搜索树的深度，用于访问杀手着法。
    tt_best_move: 从置换表中获取的最佳走法（如果有）。
    """
    move_scores = []
    
    killer1, killer2 = None, None
    if depth in KILLER_MOVES:
        killers_at_depth = KILLER_MOVES[depth]
        killer1 = killers_at_depth.get(1)
        killer2 = killers_at_depth.get(2)

    for move in possible_moves:
        r, c = move # move是 (row, col) 形式，1-indexed
        score = 0
        
        if move == tt_best_move: # 置换表找到的最好走法优先
            score = 2000000
        elif move in CORNERS: # 占角是最好的
            score = 1000000
        elif move == killer1: # 杀手着法1
            score = 500000 
        elif move == killer2: # 杀手着法2
            score = 490000
        elif move in DANGER_ZONES:
            penalty = 0
            # C格和X格的基础惩罚值
            temp_penalty_val = 20000 
            if move in C_SQUARES: temp_penalty_val = 15000
            if move in X_SQUARES: temp_penalty_val = 25000

            gives_up_corner_easily = False
            # 检查此C/X点是否会导致对方轻易占领相邻的空角
            # (r,c) 是当前考虑的C/X格走法
            for corner_r, corner_c in CORNERS:
                # 检查move是否是这个corner的C/X格
                is_adjacent_c_or_x = (abs(r - corner_r) <= 1 and abs(c - corner_c) <= 1 and not (r==corner_r and c==corner_c))
                
                if is_adjacent_c_or_x: # 是这个角旁边的C/X点
                    if board[corner_r][corner_c] == 0: # 如果这个角是空的
                        gives_up_corner_easily = True # 那么走这个C/X点就很危险
                        break 
                    elif board[corner_r][corner_c] == player_color: # 如果这个角已经是我们的
                        temp_penalty_val /= 4 # 危险性大大降低
                        gives_up_corner_easily = False # 不算轻易送角了
                        break
                    # 如果角是对方的，那么旁边的C/X点可能仍然危险，但主要惩罚来自POSITION_WEIGHTS
                    # 这里主要关注是否“轻易送出”一个原本是空的角

            if gives_up_corner_easily:
                penalty = temp_penalty_val
            
            score = POSITION_WEIGHTS[r-1][c-1] - penalty
        else: # 普通位置
            score = POSITION_WEIGHTS[r-1][c-1]
        
        # 加上历史表的分数，历史表分数越高，说明这个位置过去表现越好
        score += HISTORY_TABLE[r-1][c-1] # 调整历史表权重，这里直接加
        move_scores.append((score, move))
    
    move_scores.sort(key=lambda x: x[0], reverse=True)
    return [move for _, move in move_scores]


def minimax_alphabeta(board, depth, alpha, beta, maximizing_player, player_color, overall_start_time):
    """
    Minimax搜索算法，带有Alpha-Beta剪枝、置换表、PVS。
    player_color: 始终是最初调用AI的那个玩家的颜色，评估函数基于此视角。
    maximizing_player: 布尔值，指明当前节点是为player_color最大化分数还是为对手最小化分数。
    overall_start_time: 本次决策的总起始时间，用于硬性时间限制。
    """
    current_time = time.perf_counter()
    if current_time - overall_start_time > HARD_TIME_LIMIT_PER_MOVE:
        return None, None # 硬性超时

    # --- 置换表查询 ---
    # 当前节点的玩家颜色 (是轮到谁走棋)
    current_node_player_color = player_color if maximizing_player else -player_color
    board_hash = compute_board_hash(board, current_node_player_color)
    
    tt_entry = TRANSPOSITION_TABLE.get(board_hash)
    tt_best_move_for_ordering = None
    if tt_entry:
        tt_score, tt_depth, tt_flag, tt_retrieved_move = tt_entry
        if tt_depth >= depth: # 确保存储的结果来自等于或更深的搜索
            if tt_flag == TT_EXACT:
                return tt_score, tt_retrieved_move
            elif tt_flag == TT_LOWERBOUND:
                alpha = max(alpha, tt_score)
            elif tt_flag == TT_UPPERBOUND:
                beta = min(beta, tt_score)
            if alpha >= beta:
                return tt_score, tt_retrieved_move # 可以返回这个分数和走法
        tt_best_move_for_ordering = tt_retrieved_move # 即使深度不够，也可以用于排序

    # --- 确定当前玩家和获取合法移动 ---
    # current_node_player_color 已在上面计算
    opponent_node_player_color = -current_node_player_color
    
    current_moves = PossibleMove(current_node_player_color, board)
    opponent_moves_for_eval_at_leaf = PossibleMove(opponent_node_player_color, board) # 用于叶子节点评估

    # --- 终局检查或深度为0 ---
    # 如果当前玩家无棋可走，且对方玩家也无棋可走，则游戏结束
    if depth == 0 or (not current_moves and not opponent_moves_for_eval_at_leaf):
        # 在叶子节点，评估函数需要知道双方的合法走法
        # 注意：PossibleMove的第一个参数是“谁的视角”，board是当前棋盘
        # 评估函数始终从 player_color (AI本身)的视角评估
        # 所以，获取 player_color 和 -player_color 在当前 board 上的合法走法
        player_actual_moves_at_leaf = PossibleMove(player_color, board)
        opponent_actual_moves_at_leaf = PossibleMove(-player_color, board)
        
        eval_score = evaluate_board(board, player_color, player_actual_moves_at_leaf, opponent_actual_moves_at_leaf)
        return eval_score, None

    # --- 当前玩家无合法移动 (Pass) ---
    if not current_moves:
        # 轮到我方走，但我方无棋可走，则轮到对方走 (maximizing_player状态反转)
        # 深度减1，alpha, beta不变，player_color (评估视角)不变
        score, _ = minimax_alphabeta(
            board, depth - 1, alpha, beta, 
            not maximizing_player, # 轮到对方
            player_color,          # 评估视角不变
            overall_start_time
        )
        # 如果对方也pass，游戏会结束，这个逻辑由上面的终局检查处理。
        return score, None # 当前玩家没有走棋

    # --- 移动排序 ---
    # 将TT中找到的best_move传入用于优先排序
    sorted_moves = get_sorted_moves(board, current_moves, current_node_player_color, depth, tt_best_move_for_ordering)
    
    best_move_for_this_node = None
    
    if maximizing_player:
        best_score = -float('inf')
        original_alpha = alpha # 用于后续判断TT条目类型
        for idx, move in enumerate(sorted_moves):
            new_board = BoardCopy(board)
            PlaceMove(current_node_player_color, new_board, move[0], move[1])
            
            val = None
            # Principal Variation Search (PVS) / Null Window Search
            if idx == 0: # 第一个子节点用完整窗口搜索
                val, _ = minimax_alphabeta(new_board, depth - 1, alpha, beta, False, player_color, overall_start_time)
            else: # 其他子节点先用空窗搜索 (alpha, alpha+1)
                val, _ = minimax_alphabeta(new_board, depth - 1, alpha, alpha + 1, False, player_color, overall_start_time)
                if val is not None and val > alpha and val < beta: # 如果空窗搜索结果在 (alpha, beta) 之间，说明可能是一个更好的走法
                    # 需要用完整窗口重新搜索
                    val, _ = minimax_alphabeta(new_board, depth - 1, alpha, beta, False, player_color, overall_start_time)

            if val is None: return None, None # 超时，向上传播

            if val > best_score:
                best_score = val
                best_move_for_this_node = move
            
            alpha = max(alpha, best_score)
            
            if alpha >= beta: # Beta 剪枝
                if best_move_for_this_node: # 即当前move导致了剪枝
                    # 更新杀手着法表
                    if depth not in KILLER_MOVES: KILLER_MOVES[depth] = {}
                    current_killer1 = KILLER_MOVES[depth].get(1)
                    if current_killer1 != best_move_for_this_node:
                        KILLER_MOVES[depth][2] = current_killer1
                        KILLER_MOVES[depth][1] = best_move_for_this_node
                    # 更新历史表 (被剪枝的走法是好走法)
                    HISTORY_TABLE[best_move_for_this_node[0]-1][best_move_for_this_node[1]-1] += depth * depth
                break 
        
        # --- 存储到置换表 ---
        tt_flag_to_store = TT_EXACT
        if best_score <= original_alpha: # 如果所有走法都比alpha差，这是一个上界值
            tt_flag_to_store = TT_UPPERBOUND
        elif best_score >= beta: # 如果发生了beta剪枝，这是一个下界值
            tt_flag_to_store = TT_LOWERBOUND
        # 只有当 best_move_for_this_node 非 None 时才存储，否则可能意味着没有合法走法或超时
        if best_move_for_this_node is not None or tt_flag_to_store == TT_UPPERBOUND : # 对于upperbound，即使没有best_move也存score
             TRANSPOSITION_TABLE[board_hash] = (best_score, depth, tt_flag_to_store, best_move_for_this_node)
        return best_score, best_move_for_this_node

    else: # Minimizing player
        best_score = float('inf')
        original_beta = beta # 用于后续判断TT条目类型
        for idx, move in enumerate(sorted_moves):
            new_board = BoardCopy(board)
            PlaceMove(current_node_player_color, new_board, move[0], move[1])

            val = None
            if idx == 0:
                val, _ = minimax_alphabeta(new_board, depth - 1, alpha, beta, True, player_color, overall_start_time)
            else:
                val, _ = minimax_alphabeta(new_board, depth - 1, beta - 1, beta, True, player_color, overall_start_time) # 注意这里是 (beta-1, beta)
                if val is not None and val < beta and val > alpha: 
                    val, _ = minimax_alphabeta(new_board, depth - 1, alpha, beta, True, player_color, overall_start_time)

            if val is None: return None, None # 超时

            if val < best_score:
                best_score = val
                best_move_for_this_node = move
            
            beta = min(beta, best_score)

            if alpha >= beta: # Alpha 剪枝
                if best_move_for_this_node:
                    if depth not in KILLER_MOVES: KILLER_MOVES[depth] = {}
                    current_killer1 = KILLER_MOVES[depth].get(1)
                    if current_killer1 != best_move_for_this_node:
                        KILLER_MOVES[depth][2] = current_killer1
                        KILLER_MOVES[depth][1] = best_move_for_this_node
                    HISTORY_TABLE[best_move_for_this_node[0]-1][best_move_for_this_node[1]-1] += depth * depth
                break
        
        tt_flag_to_store = TT_EXACT
        if best_score >= original_beta: # 如果所有走法都比beta好（即值更大），这是一个下界值
            tt_flag_to_store = TT_LOWERBOUND
        elif best_score <= alpha: # 如果发生了alpha剪枝，这是一个上界值
            tt_flag_to_store = TT_UPPERBOUND
        if best_move_for_this_node is not None or tt_flag_to_store == TT_LOWERBOUND:
            TRANSPOSITION_TABLE[board_hash] = (best_score, depth, tt_flag_to_store, best_move_for_this_node)
        return best_score, best_move_for_this_node


def player(colour, board):
    """
    AI决策函数。
    colour: 当前AI玩家的颜色 (1 for black, -1 for white)
    board: 当前棋盘状态 (1-indexed list of lists)
    Returns: (row, col) tuple for the chosen move, or (0,0) if no valid moves (pass).
    """
    overall_start_time = time.perf_counter()
    
    possible_moves = PossibleMove(colour, board)
    if not possible_moves:
        return (0, 0) # 没有合法走法，Pass

    if len(possible_moves) == 1:
        return possible_moves[0] # 只有一个可选走法，直接返回

    # 为本次决策重置杀手表 (因为杀手依赖于特定根节点的搜索)
    # 置换表通常在整个游戏或应用生命周期内持续存在，除非有特定原因要清除。
    # 如果选择清除TT，应该在迭代加深开始前。这里我们不清除TT，让它跨步数保持。
    global KILLER_MOVES, HISTORY_TABLE # 声明要修改全局变量
    KILLER_MOVES = {}  # 重置杀手表
    # HISTORY_TABLE 不在这里重置，它会逐渐衰减

    # 初始最佳走法：使用浅层排序选一个（例如，排序深度为0，只看静态启发）
    # 或者直接取第一个可能的走法作为迭代加深未完成时的备用
    best_move_overall = get_sorted_moves(board, possible_moves, colour, 0)[0] 
    best_score_overall = -float('inf')

    # 迭代加深搜索
    for depth in range(1, ITERATIVE_DEEPENING_MAX_DEPTH + 1):
        # iteration_specific_start_time = time.perf_counter() # 用于调试单层深度用时

        # minimax_alphabeta的第一个 'maximizing_player' 参数是 True，因为我们希望为 'colour' 找到最佳走法
        # 'player_color' 参数传递 'colour' 以便评估函数始终从 'colour' 的视角进行评估
        current_search_best_score, current_search_best_move = minimax_alphabeta(
            board, depth, -float('inf'), float('inf'), 
            True, colour, # True for maximizing for 'colour', 'colour' is the AI's perspective
            overall_start_time
        )
        
        elapsed_total_time = time.perf_counter() - overall_start_time
        
        if current_search_best_move is not None: # 当前深度的搜索在时间内完成
            best_move_overall = current_search_best_move
            best_score_overall = current_search_best_score
            # print(f"Depth {depth}: best_move={best_move_overall}, score={best_score_overall:.0f}, time_iter={time.perf_counter()-iteration_specific_start_time:.3f}s, time_total={elapsed_total_time:.3f}s")
        else: # 搜索超时
            # print(f"Depth {depth} timed out. Using results from depth {depth-1}. Total time: {elapsed_total_time:.3f}s")
            break # 超时，使用上一层搜索的结果

        # 启发式提前退出：如果剩余时间不足以完成下一轮更深的搜索（预估）
        # 或者时间已用大半，可以考虑提前结束
        # 例如：如果总时间已用超过70%，并且当前深度大于某个值（比如3或4），就退出
        if elapsed_total_time > HARD_TIME_LIMIT_PER_MOVE * 0.75 and depth >= 3 : 
            # print(f"Time budget nearing limit ({elapsed_total_time:.3f}s / {HARD_TIME_LIMIT_PER_MOVE:.2f}s). Stopping IDS at depth {depth}.")
            break
        # 如果下一轮预估时间超过总限制，也退出 (更复杂的预估)
        # time_this_iteration = time.perf_counter() - iteration_specific_start_time
        # if elapsed_total_time + time_this_iteration * 2 > HARD_TIME_LIMIT_PER_MOVE and depth >=2: # 粗略估计下一层耗时为当前层2-3倍
            # print(f"Predicting next depth will exceed time limit. Stopping IDS at depth {depth}.")
            # break


    # 历史表衰减：每次决策后，历史表中的值会按一定比例衰减，使得新的信息更重要
    for i in range(8):
        for j in range(8):
            HISTORY_TABLE[i][j] = int(HISTORY_TABLE[i][j] * 0.85) # 衰减率可调，例如0.85或0.9
            
    # print(f"Final best move: {best_move_overall} with score {best_score_overall:.0f} found in {time.perf_counter() - overall_start_time:.4f}s")
    return best_move_overall

