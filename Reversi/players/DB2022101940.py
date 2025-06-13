from Reversi import *
import time
import math

# The given global variables are not to be touched.
# These global variables are for the original template and not directly used by the improved player1
# The improved player1 defines its own internal weights and constants.
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


def player(Colour, Board):

    # -----------------------------------------------
    # 1. 核心数据结构与辅助函数
    # -----------------------------------------------

    start_time = time.time()
    # 根据游戏速度调整，留出0.05秒的余量以防超时
    TIME_LIMIT = 1.95 

    # --- 置换表 (Transposition Table) ---
    # 存储格式: {board_hash: [score, depth, flag, best_move]}
    # flag: 0 for EXACT, 1 for LOWERBOUND (alpha), 2 for UPPERBOUND (beta)
    transposition_table = {}

    # --- 静态数据 ---
    # 棋盘权重，更细致地考虑了角落、X-方格（角落旁边）、C-方格（更内层的角落旁边）和中心区域
    # 重点：大幅增加X-方格和C-方格的負面權重，使其在搜索中更具懲罰性。
    BOARD_WEIGHTS = [
        [0,   0,   0,   0,   0,   0,   0,   0,   0, 0], # 填充行
        [0, 120, -60,  20,   5,   5,  20, -60, 120, 0], # -20 改為 -60
        [0, -60, -90,  -5,  -5,  -5,  -5, -90, -60, 0], # -20 改為 -60, -40 改為 -90
        [0,  20,  -5,  15,   3,   3,  15,  -5,  20, 0],
        [0,   5,  -5,   3,   3,   3,   3,  -5,   5, 0],
        [0,   5,  -5,   3,   3,   3,   3,  -5,   5, 0],
        [0,  20,  -5,  15,   3,   3,  15,  -5,  20, 0],
        [0, -60, -90,  -5,  -5,  -5,  -5, -90, -60, 0], # -20 改為 -60, -40 改為 -90
        [0, 120, -60,  20,   5,   5,  20, -60, 120, 0], # -20 改為 -60
        [0,   0,   0,   0,   0,   0,   0,   0,   0, 0], # 填充行
    ]
    CORNERS = {(1, 1), (1, 8), (8, 1), (8, 8)}

    # --- 走法排序 ---
    def order_moves(board, moves, player_color, tt_best_move):
        """
        根据启发式评估对走法进行排序，优先考虑置换表中的最佳走法，其次是高权重的棋盘位置。
        这有助于Alpha-Beta剪枝更早地剪枝，提高搜索效率。
        """
        # 如果置换表中存在最佳走法，则将其放在moves列表的最前面，优先搜索
        if tt_best_move and tt_best_move in moves: 
            moves.remove(tt_best_move)
            moves.insert(0, tt_best_move)
            
        def move_score(move):
            # 将高权重的棋盘位置映射到更小的负值，使其在升序排序中排在前面
            # 角落是最好的位置，给予最高的负分
            if move in CORNERS: return -1000 # 极高優先級
            return -BOARD_WEIGHTS[move[0]][move[1]] # 根據BOARD_WEIGHTS的負值來排序
        
        # 使用自定义的key函数进行排序
        moves.sort(key=move_score)
        return moves
        
    # --- 棋盘哈希 (Zobrist Hashing 简化版) ---
    def get_board_hash(board, player_color):
        """
        为棋盘状态生成一个哈希值，用于置换表。
        """
        return hash((tuple(map(tuple, board)), player_color))

    # --- 高级评估函数 (改进版) ---
    evaluation_cache = {} # 缓存评估结果，避免重复计算
    def advanced_evaluate(board, ai_player_color):
        """
        根据棋盘状态和游戏阶段，计算当前棋盘的启发式评估分数。
        分数越高表示棋盘状态对ai_player_color越有利。
        考虑因素：棋子数量、棋子位置权重、移动性、边界子、稳定子、角落控制。
        """
        board_tuple = tuple(map(tuple, board))
        # 尝试从缓存中获取评估结果
        if (board_tuple, ai_player_color) in evaluation_cache: 
            return evaluation_cache[(board_tuple, ai_player_color)]
        
        opponent_color = -ai_player_color
        score = 0

        # 1. 棋子数量差异 (Piece Difference)
        my_pieces = 0
        opponent_pieces = 0
        for r in range(1, 9):
            for c in range(1, 9):
                if board[r][c] == ai_player_color:
                    my_pieces += 1
                elif board[r][c] == opponent_color:
                    opponent_pieces += 1

        # 2. 棋子位置加权得分 (Positional Score)
        positional_score = 0
        for r in range(1, 9):
            for c in range(1, 9):
                if board[r][c] == ai_player_color:
                    positional_score += BOARD_WEIGHTS[r][c]
                elif board[r][c] == opponent_color:
                    positional_score -= BOARD_WEIGHTS[r][c]

        # 3. 移动性 (Mobility) - 可行走法数量差异
        my_mobility = len(PossibleMove(ai_player_color, board))
        opponent_mobility = len(PossibleMove(opponent_color, board))
        mobility_score = my_mobility - opponent_mobility

        # 4. 边界棋子 (Frontier Discs) - 棋子旁边有空位的数量
        # 边界子越多意味着棋子越暴露，更容易被翻转，所以希望这个分数越小越好（负值）
        my_frontier_discs = 0
        opp_frontier_discs = 0
        for r in range(1, 9):
            for c in range(1, 9):
                if board[r][c] == Empty: # 找到空位
                    # 检查空位的所有邻居，看是哪个玩家的棋子
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0: continue # 跳过自身
                            nr, nc = r + dr, c + dc
                            # 确保邻居在棋盘范围内 (1-8)
                            if 1 <= nr <= 8 and 1 <= nc <= 8:
                                if board[nr][nc] == ai_player_color:
                                    my_frontier_discs += 1
                                elif board[nr][nc] == opponent_color:
                                    opp_frontier_discs += 1
        frontier_score = -(my_frontier_discs - opp_frontier_discs) # 负值，鼓励减少边界子

        # --- 稳定子 (Stable Discs) ---
        # 稳定子是那些无法被翻转的棋子，价值极高。
        # 这里的实现是简化的，主要检测角落和形成实心线的邊緣棋子。
        def is_stable(r, c, color, current_board):
            # 角落棋子总是稳定的
            if (r, c) in CORNERS:
                return True

            # 检查边缘棋子是否稳定
            # 一个边缘棋子稳定，如果它在某个方向上（水平、垂直或对角）形成一条连续的同色棋子線，
            # 並且這條線一直延伸到棋盤的邊緣（沒有空位或異色棋子阻擋）。
            if r == 1 or r == 8 or c == 1 or c == 8: # 这是一个边缘棋子
                # 检查水平稳定性
                stable_h = True
                for x_dir in [-1, 1]:
                    curr_c = c + x_dir
                    while 0 < curr_c <= 8 and current_board[r][curr_c] == color:
                        curr_c += x_dir
                    if not (curr_c == 0 or curr_c == 9): # 如果没有碰到棋盘边缘，则不稳定
                        stable_h = False
                        break
                if stable_h: return True

                # 检查垂直稳定性
                stable_v = True
                for y_dir in [-1, 1]:
                    curr_r = r + y_dir
                    while 0 < curr_r <= 8 and current_board[curr_r][c] == color:
                        curr_r += y_dir
                    if not (curr_r == 0 or curr_r == 9): # 如果没有碰到棋盘边缘，则不稳定
                        stable_v = False
                        break
                if stable_v: return True

                # 检查对角线稳定性 (左上到右下)
                stable_diag1 = True
                for d_dir in [-1, 1]: # (-1,-1) 和 (1,1) 方向
                    curr_r, curr_c = r + d_dir, c + d_dir
                    while 0 < curr_r <= 8 and 0 < curr_c <= 8 and current_board[curr_r][curr_c] == color:
                        curr_r += d_dir
                        curr_c += d_dir
                    if not ((curr_r == 0 or curr_r == 9) or (curr_c == 0 or curr_c == 9)): # 如果没有碰到棋盘边缘，则不稳定
                        stable_diag1 = False
                        break
                if stable_diag1: return True

                # 检查对角线稳定性 (右上到左下)
                stable_diag2 = True
                for d_r_dir, d_c_dir in [(-1, 1), (1, -1)]: # (-1,1) 和 (1,-1) 方向
                    curr_r, curr_c = r + d_r_dir, c + d_c_dir
                    while 0 < curr_r <= 8 and 0 < curr_c <= 8 and current_board[curr_r][curr_c] == color:
                        curr_r += d_r_dir
                        curr_c += d_c_dir
                    if not ((curr_r == 0 or curr_r == 9) or (curr_c == 0 or curr_c == 9)): # 如果没有碰到棋盘边缘，则不稳定
                        stable_diag2 = False
                        break
                if stable_diag2: return True
            
            return False # 不是角落，也不是上述简单的边缘稳定子

        my_stable_discs = 0
        opp_stable_discs = 0
        for r in range(1, 9):
            for c in range(1, 9):
                if board[r][c] == ai_player_color:
                    if is_stable(r, c, ai_player_color, board):
                        my_stable_discs += 1
                elif board[r][c] == opponent_color:
                    if is_stable(r, c, opponent_color, board):
                        opp_stable_discs += 1
        
        stable_disc_score = (my_stable_discs - opp_stable_discs) * 1000 # 稳定子权重非常高

        # 5. 角落控制 (Corner Control) - 占据角落的数量
        # 角落的分数部分地体现在稳定子中，但作为战略要地，仍单独给予高分
        my_corners = 0
        opp_corners = 0
        for corner in CORNERS:
            if board[corner[0]][corner[1]] == ai_player_color:
                my_corners += 1
            elif board[corner[0]][corner[1]] == opponent_color:
                opp_corners += 1
        corner_strategic_score = (my_corners - opp_corners) * 500 # 较高的战略权重

        # 游戏阶段调整权重 (Dynamic Weighting based on game stage)
        # 根据棋盘上的空位数量判断游戏阶段
        empty_cells = sum(row.count(Empty) for row in board if isinstance(row, list))
        
        # 权重系数，这些值可以根据测试和经验进行微调
        # 目标是：早期注重开局布局和移动性，中期平衡，晚期注重棋子数量和稳定棋子
        # 重点：角落和稳定子在各階段的權重都顯著提升
        if empty_cells >= 40: # 早期游戏 (开局)
            score = positional_score * 0.5 + mobility_score * 50 + frontier_score * 10 + stable_disc_score * 2.0 + corner_strategic_score * 3.0 # 角落/穩定子權重更高
        elif empty_cells >= 30: # 中期游戏
            score = positional_score * 0.8 + mobility_score * 40 + frontier_score * 20 + stable_disc_score * 3.0 + corner_strategic_score * 4.0 # 角落/穩定子權重更高
        elif empty_cells >= 15: # 晚期游戏 (终局前)
            score = positional_score * 1.0 + mobility_score * 20 + frontier_score * 30 + stable_disc_score * 4.0 + corner_strategic_score * 5.0 # 角落/穩定子權重更高
        else: # 终局阶段 (空位很少)
            # 终局时棋子数量差异和稳定性至关重要，移动性优先级降低
            # 棋子数量差异的权重应非常高，因为它直接决定胜负
            score = (my_pieces - opponent_pieces) * 1000 + stable_disc_score * 5.0 + corner_strategic_score * 6.0 + positional_score * 0.1 # 角落/穩定子權重達到最高

        evaluation_cache[(board_tuple, ai_player_color)] = score
        return score

    # --- 终局精确求解器 (改进：增加Alpha-Beta剪枝) ---
    def endgame_solver(board, player_color, alpha, beta):
        """
        递归地计算终局结果，使用NegaMax和Alpha-Beta剪枝。
        返回最终的棋子数量差异。
        """
        # 检查游戏是否结束 (双方都无子可下)
        game_is_over = not PossibleMove(Black, board) and not PossibleMove(White, board)
        if game_is_over:
            my_tiles = sum(row.count(player_color) for row in board)
            opp_tiles = sum(row.count(-player_color) for row in board)
            return my_tiles - opp_tiles # 返回最终棋子数量差异

        possible_moves = PossibleMove(player_color, board)

        # 如果当前玩家无子可下，则跳过当前回合，轮到对手
        if not possible_moves:
            # 分数是对手从当前棋盘状态中能获得的最大分数的负值
            return -endgame_solver(board, -player_color, -beta, -alpha) # Alpha和Beta需要翻转

        best_score = -math.inf

        # 遍历所有可能的走法
        for move in possible_moves:
            new_board = PlaceMove(player_color, board, move[0], move[1])
            # 递归调用终局求解器，并取负值 (NegaMax)
            score = -endgame_solver(new_board, -player_color, -beta, -alpha)
            best_score = max(best_score, score) # 更新当前最佳分数
            alpha = max(alpha, best_score) # 更新alpha
            if alpha >= beta: # Alpha-Beta剪枝
                break
                
        return best_score

    # --- Alpha-Beta NegaMax with Transposition Table and PVS ---
    def pvs_search(board, depth, alpha, beta, player_color, ai_player_color, is_endgame):
        """
        使用迭代加深、Alpha-Beta剪枝、置换表和主变例搜索(PVS)进行深度搜索。
        """
        if time.time() - start_time > TIME_LIMIT:
            raise TimeoutError # 如果时间超出限制，抛出异常

        # --- 1. 置换表查询 ---
        original_alpha = alpha
        board_hash = get_board_hash(board, player_color)
        if board_hash in transposition_table:
            entry = transposition_table[board_hash]
            if entry[1] >= depth: # 缓存的深度足够
                if entry[2] == 0: # EXACT (精确值)
                    return entry[0]
                elif entry[2] == 1: # LOWERBOUND (下界)
                    alpha = max(alpha, entry[0])
                elif entry[2] == 2: # UPPERBOUND (上界)
                    beta = min(beta, entry[0])
                if alpha >= beta: # 如果发生剪枝，直接返回缓存的值
                    return entry[0]
                    
        # --- 2. 到达叶子节点或游戏结束 ---
        game_is_over = not PossibleMove(Black, board) and not PossibleMove(White, board)
        if depth == 0 or game_is_over:
            if is_endgame:
                # 在终局模式下，调用带Alpha-Beta的终局求解器
                # 注意：player_color和ai_player_color的关系，以及alpha/beta的翻转
                return endgame_solver(board, player_color, alpha, beta) if player_color == ai_player_color else -endgame_solver(board, -player_color, -beta, -alpha)
            else:
                # 非终局，使用启发式评估函数
                # 评估函数返回的是ai_player_color视角的得分，需要根据当前player_color调整正负
                return advanced_evaluate(board, ai_player_color) * (1 if player_color == ai_player_color else -1)

        # --- 3. 生成并排序走法 ---
        possible_moves = PossibleMove(player_color, board)
        if not possible_moves:
            # 如果当前玩家没有合法走法，跳过这一回合
            # 分数是对手从当前棋盘状态中能获得的最大分数的负值
            return -pvs_search(board, depth, -beta, -alpha, -player_color, ai_player_color, is_endgame)
        
        # 从置换表中获取上一次的最佳走法，用于走法排序
        tt_best_move = transposition_table.get(board_hash, [None, None, None, None])[3]
        order_moves(board, possible_moves, player_color, tt_best_move)

        # --- 4. 循环搜索 (Principal Variation Search 思想) ---
        best_score = -math.inf
        best_move_for_tt = possible_moves[0] # 初始化为第一个走法
        for i, move in enumerate(possible_moves):
            new_board = PlaceMove(player_color, board, move[0], move[1])
            if i == 0: # 第一个节点（主变例）用完整的[alpha, beta]窗口搜索
                score = -pvs_search(new_board, depth - 1, -beta, -alpha, -player_color, ai_player_color, is_endgame)
            else: # 其他节点用零窗口搜索(Zero-Window Search)，期望快速失败
                score = -pvs_search(new_board, depth - 1, -alpha - 1, -alpha, -player_color, ai_player_color, is_endgame)
                if alpha < score < beta: # 如果ZWS失败，说明找到了更好的走法，需要重新全窗口搜索
                    score = -pvs_search(new_board, depth - 1, -beta, -alpha, -player_color, ai_player_color, is_endgame)
            
            if score > best_score:
                best_score = score
                best_move_for_tt = move

            alpha = max(alpha, best_score) # 更新alpha
            if alpha >= beta: # Alpha-Beta剪枝
                break # 剪枝，不再搜索后续走法
                
        # --- 5. 存储到置换表 ---
        flag = 0 # 默认为 EXACT
        if best_score <= original_alpha:
            flag = 2 # UPPERBOUND (分数低于或等于原始alpha，表示当前节点的分数是上限)
        elif best_score >= beta:
            flag = 1 # LOWERBOUND (分数高于或等于beta，表示当前节点的分数是下限)
        transposition_table[board_hash] = [best_score, depth, flag, best_move_for_tt]
        
        return best_score


    # -----------------------------------------------
    # 2. AI决策主逻辑 (迭代加深)
    # -----------------------------------------------
    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0) # 如果没有合法走法，返回(0,0)表示跳过

    if len(possible_moves) == 1:
        return possible_moves[0] # 只有一个合法走法时直接走

    # 计算空位数量
    empty_tiles = sum(row.count(Empty) for row in Board if isinstance(row, list))

    # --- 新增：开局库 (Opening Book) ---
    # 检查是否是游戏的初始棋盘状态
    initial_board_state = [[Empty for _ in range(10)] for _ in range(10)]
    initial_board_state[4][4] = White
    initial_board_state[5][5] = White
    initial_board_state[4][5] = Black
    initial_board_state[5][4] = Black
    
    is_initial_board = True
    # 忽略棋盤邊界（0行0列9行9列）
    for r in range(1,9):
        for c in range(1,9):
            if Board[r][c] != initial_board_state[r][c]:
                is_initial_board = False
                break
        if not is_initial_board:
            break

    # 如果是初始棋盘，且AI是黑子（标准先手方），则从开局库中选择第一步
    if is_initial_board and Colour == Black:
        # 針對Reversi的經典開局走法 (通常是黑子第一步)
        # 這些走法通常都能讓黑子在開局取得不錯的控制
        opening_moves_for_black = [(3, 4), (4, 3), (5, 6), (6, 5)]
        for move in opening_moves_for_black:
            if move in possible_moves:
                return move # 返回預設的最佳開局走法

    # 确定是否进入终局模式
    # 终局求解阈值：当空位数量低于或等于此值时，启用终局求解器进行精确计算。
    # 适当提高此阈值可以使AI更早地进行精确计算，但会增加计算量。
    ENDGAME_THRESHOLD = 18 # 终局求解阈值，從16調整為18，以期更早地進入終局求解

    best_move = possible_moves[0] # 初始化最佳走法
    best_move_this_iter = possible_moves[0]

    try:
        max_depth = 64 - empty_tiles # 理论最大搜索深度 (棋盘总格子数 - 已下棋子数)
        # 迭代加深，从浅层搜索到深层搜索
        for depth in range(1, max_depth + 1):
            best_score_this_iter = -math.inf
            
            # 顶层循环也需要对走法进行排序，提高第一次全搜索的效率
            tt_best_move = transposition_table.get(get_board_hash(Board, Colour), [None, None, None, None])[3]
            # 这里复制一份 possible_moves 列表，避免在排序时修改原始列表
            ordered_moves = order_moves(Board, list(possible_moves), Colour, tt_best_move)

            for move in ordered_moves:
                new_board = PlaceMove(Colour, Board, move[0], move[1])
                # 调用PVS搜索，注意：第一个子节点的分数是对手的分数，所以需要取负
                # 初始alpha和beta为负无穷和正无穷
                score = -pvs_search(new_board, depth - 1, -math.inf, math.inf, -Colour, Colour, empty_tiles <= ENDGAME_THRESHOLD)
                
                # 在顶层检查时间，确保至少完成一次迭代后才可能超时
                if time.time() - start_time > TIME_LIMIT and depth > 1:
                     raise TimeoutError # 超时，终止搜索

                if score > best_score_this_iter:
                    best_score_this_iter = score
                    best_move_this_iter = move
            
            # 如果一轮完整的深度搜索完成，更新全局最佳走法
            best_move = best_move_this_iter

    except TimeoutError:
        # 如果搜索超时，返回上一次完整迭代找到的最佳走法
        return best_move

    # 正常完成所有深度的搜索（通常只在游戏很短或终局时发生）
    return best_move
