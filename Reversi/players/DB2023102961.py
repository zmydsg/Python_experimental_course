from Reversi import *

def player(color, board):
    # 定义棋盘关键位置
    CORNERS = [(1, 1), (1, 8), (8, 1), (8, 8)]
    X_SQUARES = [(2, 2), (2, 7), (7, 2), (7, 7)]
    C_SQUARES = [(1, 2), (1, 7), (2, 1), (2, 8), (7, 1), (7, 8), (8, 2), (8, 7)]
    EDGES = [(x, 1) for x in range(3, 7)] + [(x, 8) for x in range(3, 7)] + \
            [(1, y) for y in range(3, 7)] + [(8, y) for y in range(3, 7)]
    CENTER = [(4, 4), (4, 5), (5, 4), (5, 5)]
    
    # 动态调整的评估权重
    def get_weights(total_discs):
        if total_discs < 20:    # 开局
            return {
                'corner': 1000,  # 极高角落权重
                'edge': 40,
                'mobility': 35,  # 更高行动力权重
                'stability': 15,
                'disc': 1,      # 极低棋子数量权重
                'x_penalty': -80,
                'c_penalty': -50,
                'frontier': -20, # 前沿惩罚
                'potential': 25, # 潜在行动力
                'parity': 0,    # 奇偶性
                'center': 5      # 中心控制
            }
        elif total_discs < 50:  # 中局
            return {
                'corner': 350,
                'edge': 35,
                'mobility': 25,
                'stability': 20,
                'disc': 8,
                'x_penalty': -50,
                'c_penalty': -30,
                'frontier': -15,
                'potential': 20,
                'parity': 10,
                'center': 3
            }
        else:                   # 终局
            return {
                'corner': 250,
                'edge': 25,
                'mobility': 15,
                'stability': 10,
                'disc': 20,     # 更高棋子数量权重
                'x_penalty': 0,
                'c_penalty': 0,
                'frontier': 0,
                'potential': 5,
                'parity': 20,
                'center': 0
            }
    
    # 优化的评估函数 - 减少计算量
    def heuristic_evaluation(board, color):
        total_discs = sum(1 for row in board for cell in row if cell in (1, -1))
        weights = get_weights(total_discs)
        score = 0
        
        # 1. 角落控制 (最高优先级)
        for x, y in CORNERS:
            if board[x][y] == color:
                score += weights['corner']
            elif board[x][y] == -color:
                score -= weights['corner']
        
        # 2. 危险位置惩罚 (X位和C位)
        for x, y in X_SQUARES + C_SQUARES:
            if board[x][y] == color:
                if (x, y) in X_SQUARES:
                    score += weights['x_penalty']
                else:
                    score += weights['c_penalty']
            elif board[x][y] == -color:
                if (x, y) in X_SQUARES:
                    score -= weights['x_penalty']
                else:
                    score -= weights['c_penalty']
        
        # 3. 边缘控制
        for x, y in EDGES:
            if board[x][y] == color:
                score += weights['edge']
            elif board[x][y] == -color:
                score -= weights['edge']
        
        # 4. 中心控制 (仅开局使用)
        if total_discs < 20:
            for x, y in CENTER:
                if board[x][y] == color:
                    score += weights['center']
                elif board[x][y] == -color:
                    score -= weights['center']
        
        # 5. 行动力 (移动选择权)
        my_moves = len(PossibleMove(color, board))
        opp_moves = len(PossibleMove(-color, board))
        
        # 终局特殊处理：无移动选择时评估棋子差
        if my_moves == 0 and opp_moves == 0:
            my_discs = sum(row.count(color) for row in board)
            opp_discs = sum(row.count(-color) for row in board)
            return (my_discs - opp_discs) * 1000  # 巨大权重
        
        # 6. 潜在行动力预测 (仅当棋子少于40时计算)
        if total_discs < 40:
            my_potential = 0
            opp_potential = 0
            for x in range(1, 9):
                for y in range(1, 9):
                    if board[x][y] == 0:  # 空位
                        # 检查是否有相邻的对手棋子
                        for dx in (-1, 0, 1):
                            for dy in (-1, 0, 1):
                                if dx == 0 and dy == 0:
                                    continue
                                nx, ny = x + dx, y + dy
                                if 1 <= nx <= 8 and 1 <= ny <= 8:
                                    if board[nx][ny] == -color:
                                        my_potential += 1
                                        break
                                    elif board[nx][ny] == color:
                                        opp_potential += 1
                                        break
            score += weights['potential'] * (my_potential - opp_potential)
        
        # 7. 奇偶性策略 (仅终局使用)
        if total_discs >= 50:
            key_squares = CORNERS + X_SQUARES + C_SQUARES + EDGES
            key_empty = sum(1 for (x, y) in key_squares if board[x][y] == 0)
            
            # 如果关键区域空位为奇数，优先控制这些位置
            if key_empty % 2 == 1:
                # 检查当前玩家是否能控制这些位置
                if color == 1:  # 黑棋
                    score += weights['parity']
                else:  # 白棋
                    score -= weights['parity']
        
        # 8. 行动力差计算
        mobility = my_moves - opp_moves
        if my_moves + opp_moves > 0:
            score += weights['mobility'] * mobility / (my_moves + opp_moves)
        
        # 9. 稳定性评估 (优化版)
        stable_discs = 0
        frontier_discs = 0  # 前沿棋子计数器
        
        # 仅评估关键区域以节省时间
        key_positions = CORNERS + EDGES
        for x, y in key_positions:
            if board[x][y] == 0:  # 空格
                continue
                
            disc_color = board[x][y]
            # 检查是否是前沿棋子（与空位相邻）
            is_frontier = False
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 1 <= nx <= 8 and 1 <= ny <= 8 and board[nx][ny] == 0:
                        is_frontier = True
                        break
                if is_frontier:
                    break
            
            # 更新前沿计数
            if is_frontier:
                if disc_color == color:
                    frontier_discs += 1
                else:
                    frontier_discs -= 1
            
            # 角落永远稳定
            if (x, y) in CORNERS:
                if disc_color == color:
                    stable_discs += 1
                else:
                    stable_discs -= 1
                continue
            
            # 边缘稳定性预测 (简化)
            if (x, y) in EDGES:
                # 检查是否被固定
                fixed = False
                if x == 1:
                    if all(board[1][k] == disc_color for k in range(1, 9)):
                        fixed = True
                elif x == 8:
                    if all(board[8][k] == disc_color for k in range(1, 9)):
                        fixed = True
                elif y == 1:
                    if all(board[k][1] == disc_color for k in range(1, 9)):
                        fixed = True
                elif y == 8:
                    if all(board[k][8] == disc_color for k in range(1, 9)):
                        fixed = True
                
                if fixed:
                    if disc_color == color:
                        stable_discs += 1
                    else:
                        stable_discs -= 1
        
        # 应用前沿惩罚（前沿棋子越多越不利）
        score += weights['frontier'] * frontier_discs
        score += weights['stability'] * stable_discs
        
        # 10. 棋子数量差 (权重最低)
        my_discs = sum(row.count(color) for row in board)
        opp_discs = sum(row.count(-color) for row in board)
        if my_discs + opp_discs > 0:
            score += weights['disc'] * (my_discs - opp_discs) / (my_discs + opp_discs)
        
        return score
    
    # 优化的极小极大算法 - 带alpha-beta剪枝和移动排序
    def minimax(board, color, depth, alpha, beta, maximizing_player, start_time):
        # 检查时间限制
        if time.time() - start_time > 1.4:  # 保留0.1秒缓冲
            return None  # 超时信号
        
        # 深度为0或游戏结束时进行评估
        if depth == 0:
            return heuristic_evaluation(board, color)
        
        current_moves = PossibleMove(color, board)
        
        # 终局处理：无合法移动时直接评估
        if not current_moves:
            opp_moves = PossibleMove(-color, board)
            if not opp_moves:  # 双方都无移动，游戏结束
                return heuristic_evaluation(board, color)
            # 只有对手能移动，跳过本方回合
            return minimax(board, -color, depth-1, alpha, beta, not maximizing_player, start_time)
        
        # 移动排序：角落 > 安全边缘 > 其他 > 危险位置
        current_moves.sort(key=lambda move: 
                            (3 if move in CORNERS else 
                             2 if move in EDGES and move not in C_SQUARES and move not in X_SQUARES else
                             1 if move not in X_SQUARES and move not in C_SQUARES else
                             0))
        
        if maximizing_player:
            max_eval = -float('inf')
            for move in current_moves:
                x, y = move
                new_board = BoardCopy(board)
                PlaceMove(color, new_board, x, y)
                
                # 递归搜索
                eval = minimax(new_board, -color, depth-1, alpha, beta, False, start_time)
                
                # 检查超时
                if eval is None:
                    return None
                
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in current_moves:
                x, y = move
                new_board = BoardCopy(board)
                PlaceMove(color, new_board, x, y)
                
                # 递归搜索
                eval = minimax(new_board, -color, depth-1, alpha, beta, True, start_time)
                
                # 检查超时
                if eval is None:
                    return None
                
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
    
    # 优化的迭代深化搜索 - 确保1.5秒内完成
    def iterative_deepening(board, color, max_depth):
        import time
        start_time = time.time()
        best_move = None
        best_score = -float('inf')
        
        # 初始深度搜索
        depth = 1
        while depth <= max_depth:
            current_best_move = None
            current_best_score = -float('inf')
            
            possible_moves = PossibleMove(color, board)
            if not possible_moves:
                return (0, 0)
            
            # 移动排序
            possible_moves.sort(key=lambda move: 
                                (3 if move in CORNERS else 
                                 2 if move in EDGES and move not in C_SQUARES and move not in X_SQUARES else
                                 1 if move not in X_SQUARES and move not in C_SQUARES else
                                 0))
            
            # 检查是否有直接占角的机会 - 立即返回
            corner_moves = [m for m in possible_moves if m in CORNERS]
            if corner_moves:
                return corner_moves[0]  # 有角先占角
            
            for move in possible_moves:
                # 检查时间
                if time.time() - start_time > 1.4:
                    if best_move is not None:
                        return best_move
                    return possible_moves[0]  # 超时返回第一个合法移动
                
                x, y = move
                new_board = BoardCopy(board)
                PlaceMove(color, new_board, x, y)
                
                # 执行搜索
                score = minimax(new_board, -color, depth-1, -float('inf'), float('inf'), False, start_time)
                
                # 检查超时
                if score is None:
                    # 返回当前最佳结果
                    if best_move is not None:
                        return best_move
                    return possible_moves[0]  # 超时返回第一个合法移动
                
                if score > current_best_score:
                    current_best_score = score
                    current_best_move = move
            
            # 更新最佳结果
            if current_best_score > best_score or best_move is None:
                best_score = current_best_score
                best_move = current_best_move
            
            # 检查时间
            elapsed = time.time() - start_time
            if elapsed > 1.0:  # 如果已用1秒，提前退出
                break
                
            # 深度增加策略
            depth += 1
        
        return best_move
    
    # 主决策逻辑 - 确保在1.5秒内完成
    import time
    start_time = time.time()
    
    possible_moves = PossibleMove(color, board)
    if not possible_moves:
        return (0, 0)  # 无合法移动
    
    total_discs = sum(row.count(1) + row.count(-1) for row in board)
    empty_squares = 64 - total_discs
    
    # 1. 开局策略 (前20步) - 快速决策
    if total_discs < 20:
        # 优先占角
        for move in possible_moves:
            if move in CORNERS:
                return move
        
        # 避免危险位置（X位和C位）
        safe_moves = [m for m in possible_moves if m not in X_SQUARES and m not in C_SQUARES]
        
        # 优先选择安全的边缘位置
        for move in safe_moves:
            if move in EDGES:
                return move
        
        # 次选：安全的非边缘位置
        if safe_moves:
            return safe_moves[0]
        
        # 最后选择：危险位置（必须移动时）
        return possible_moves[0]
    
    # 2. 中局策略 (20-50步) - 动态深度控制
    elif total_discs < 50:
        # 根据空位数量设置最大深度
        if empty_squares > 40:
            max_depth = 6
        elif empty_squares > 30:
            max_depth = 8
        elif empty_squares > 20:
            max_depth = 10
        elif empty_squares > 15:
            max_depth = 12
        else:
            max_depth = 14
        
        # 使用优化的迭代深化搜索
        return iterative_deepening(board, color, max_depth)
    
    # 3. 终局策略 (50+步) - 精确但高效搜索
    else:
        # 深度根据剩余空格动态调整
        if empty_squares <= 8:
            max_depth = empty_squares  # 完全搜索
        elif empty_squares <= 15:
            max_depth = 8
        else:
            max_depth = 10
        
        # 使用优化的迭代深化搜索
        return iterative_deepening(board, color, max_depth)