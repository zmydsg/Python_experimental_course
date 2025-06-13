#coding=gb2312

# Python课程项目V3.0 2025专用模块
# 优化版黑白棋AI模块

import random
import copy

# 错误代码定义
IllegalMove, PlayerError, PlayerSlow, NoMove = (1001, 1002, 1003, 1004)

# 方向向量字典（8个方向）
NeighbourDirection = {
    'N': (0, -1),   # 北
    'NE': (1, -1),  # 东北
    'E': (1, 0),    # 东
    'SE': (1, 1),   # 东南
    'S': (0, 1),    # 南
    'SW': (-1, 1),  # 西南
    'W': (-1, 0),   # 西
    'NW': (-1, -1)  # 西北
}

# 棋子颜色常量
Black, White, Empty = 1, -1, 0  # 黑色棋子，白色棋子，空位

# 战略权重矩阵（10x10）
WEIGHT_MATRIX = [
    # 外围辅助行/列（不可落子区域）
    [0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
    # 第1行（实际游戏行）
    [0, 200, -50, 100,  50,  50, 100, -50, 200,   0],  # 角落价值200，危险区域-50
    # 第2行
    [0, -50, -75,  10,  10,  10,  10, -75, -50,   0],  # 次危险区域-75
    # 第3行
    [0, 100,  10,  30,  15,  15,  30,  10, 100,   0],  # 边缘区域高价值
    # 第4-5行（中心区域）
    [0,  50,  10,  15,   5,   5,  15,  10,  50,   0],  # 中心低价值
    [0,  50,  10,  15,   5,   5,  15,  10,  50,   0],  # 对称设计
    # 第6-8行（镜像对称）
    [0, 100,  10,  30,  15,  15,  30,  10, 100,   0],
    [0, -50, -75,  10,  10,  10,  10, -75, -50,   0],
    [0, 200, -50, 100,  50,  50, 100, -50, 200,   0],
    # 外围辅助行
    [0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
]

def BoardInit():
    """初始化10x10棋盘及初始布局"""
    board = [[Empty]*10 for _ in range(10)]  # 创建全空棋盘
    # 设置初始棋子
    board[4][4] = White  # d4
    board[5][5] = White  # e5
    board[4][5] = Black  # e4
    board[5][4] = Black  # d5
    return board

def BoardCopy(board):
    """创建棋盘状态的深拷贝副本"""
    return copy.deepcopy(board)

def ValidCell(x, y):
    """验证坐标是否在可落子区域(1-8)"""
    return 1 <= x <= 8 and 1 <= y <= 8

def Neighbour(board, x, y):
    """获取当前坐标8个方向的相邻单元格状态"""
    return {dir: board[x+dx][y+dy] if (0<=x+dx<10 and 0<=y+dy<10) else None
            for dir, (dx, dy) in NeighbourDirection.items()}

def NeighbourCell(board, direction, x, y):
    """沿指定方向连续检测单元格"""
    dx, dy = NeighbourDirection[direction]
    cells = []
    nx, ny = x+dx, y+dy  # 起始位置
    while 0 <= nx < 10 and 0 <= ny < 10:  # 包含边界检测
        cells.append(board[nx][ny])
        nx += dx
        ny += dy
    return cells

def PossibleMove(player, board):
    """生成当前玩家的所有合法走法（优化验证版）"""
    legal_moves = set()  # 使用集合避免重复
    # 遍历所有可落子位置
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] != Empty:
                continue  # 跳过已有棋子的位置
            
            # 检查8个方向
            for dx, dy in NeighbourDirection.values():
                nx, ny = x+dx, y+dy  # 相邻位置
                # 初步验证：必须是对方棋子
                if not ValidCell(nx, ny) or board[nx][ny] != -player:
                    continue
                
                # 延伸检测：寻找本方棋子封口
                while ValidCell(nx+dx, ny+dy):
                    nx += dx
                    ny += dy
                    # 找到本方棋子则记录为合法移动
                    if board[nx][ny] == player:
                        legal_moves.add((x, y))
                        break
                    # 遇到空位则终止检测
                    elif board[nx][ny] == Empty:
                        break
    return list(legal_moves)

def PlaceMove(player, board, x, y):
    """执行落子并翻转对方棋子"""
    if not ValidCell(x, y) or board[x][y] != Empty:
        return board  # 无效移动直接返回
    
    flip_list = []  # 需要翻转的棋子坐标
    # 检测8个方向的可翻转序列
    for dx, dy in NeighbourDirection.values():
        temp_flips = []  # 临时存储当前方向的翻转棋子
        nx, ny = x+dx, y+dy  # 起始检测位置
        
        # 收集连续对方棋子
        while ValidCell(nx, ny) and board[nx][ny] == -player:
            temp_flips.append((nx, ny))
            nx += dx
            ny += dy
        
        # 验证终止条件：遇到本方棋子
        if ValidCell(nx, ny) and board[nx][ny] == player:
            flip_list.extend(temp_flips)  # 确认可翻转
    
    # 创建新棋盘状态
    new_board = BoardCopy(board)
    new_board[x][y] = player  # 放置当前玩家棋子
    # 翻转所有被包围的棋子
    for fx, fy in flip_list:
        new_board[fx][fy] = player
    return new_board

def drawBoard(board):
    """文本模式棋盘可视化"""
    print("  1 2 3 4 5 6 7 8")  # 列标
    for y in range(1, 9):
        row = [f'{y}|']  # 行标
        for x in range(1, 9):
            piece = board[x][y]
            # 符号化表示
            row.append('W' if piece == White else 'B' if piece == Black else '.')
        print(' '.join(row))  # 输出行

def PlayGame(player_white, player_black):
    """游戏流程控制器（含终局判断）"""
    board = BoardInit()  # 初始化棋盘
    current = White       # 白方先手
    consecutive_passes = 0  # 连续弃权计数
    
    while consecutive_passes < 2:  # 双方连续弃权时结束
        try:
            # 获取当前玩家走法
            if current == White:
                move = player_white(current, BoardCopy(board))
            else:
                move = player_black(current, BoardCopy(board))
            
            # 处理弃权情况
            if move == (0, 0):
                consecutive_passes += 1
                current = -current  # 切换玩家
                continue
                
            # 验证走法合法性
            if move not in PossibleMove(current, board):
                raise IllegalMove  # 触发异常
            
            # 执行走法并重置弃权计数
            board = PlaceMove(current, board, *move)
            consecutive_passes = 0
            current = -current  # 切换玩家
            
        except Exception as e:
            # 处理非法移动
            if isinstance(e, IllegalMove):
                current = -current
                consecutive_passes += 1
                continue
    
    # 计算最终得分
    white_score = sum(row.count(White) for row in board)
    black_score = sum(row.count(Black) for row in board)
    return board, black_score - white_score  # 返回分差

# 增强型AI策略
def player(colour, board):
    """三级策略AI决策函数"""
    corners = [(1,1), (1,8), (8,1), (8,8)]  # 四角坐标
    legal_moves = PossibleMove(colour, board)
    if not legal_moves:
        return (0, 0)  # 无合法移动时弃权
    
    # 第一级策略：角落优先
    corner_moves = [m for m in legal_moves if m in corners]
    if corner_moves:
        return strategic_choice(corner_moves, colour, board)
    
    # 第二级策略：边缘安全检测
    edge_moves = [m for m in legal_moves 
                 if m[0] in (1,8) or m[1] in (1,8)]  # 边缘位置
    safe_edges = []
    for move in edge_moves:
        # 模拟走法后检测对手能否获得角落
        simulated = PlaceMove(colour, board, *move)
        opp_moves = PossibleMove(-colour, simulated)
        if not any(c in opp_moves for c in corners):
            safe_edges.append(move)  # 安全边缘位置
    
    if safe_edges:
        return strategic_choice(safe_edges, colour, board)
    elif edge_moves:
        return strategic_choice(edge_moves, colour, board)
    
    # 第三级策略：综合位置优化
    return strategic_choice(legal_moves, colour, board)

def strategic_choice(candidates, colour, board):
    """多因素决策算法"""
    corners = [(1,1), (1,8), (8,1), (8,8)]  # 内部定义确保可用
    best_score = -float('inf')  # 初始最低分
    best_moves = []
    
    for move in candidates:
        # 因素1：位置价值（权重矩阵）
        position_value = WEIGHT_MATRIX[move[0]][move[1]]
        
        # 因素2：即时机动性（对手可移动数）
        simulated = PlaceMove(colour, board, *move)
        opp_mobility = len(PossibleMove(-colour, simulated))
        
        # 因素3：潜在稳定性加成
        edge_bonus = 20 if (move[0] in (1,8) or move[1] in (1,8)) else 0
        corner_bonus = 100 if move in corners else 0
        
        # 综合评分公式
        total_score = position_value * 1.5 - opp_mobility * 3 + edge_bonus + corner_bonus           
        
        # 更新最佳选择
        if total_score > best_score:
            best_score = total_score
            best_moves = [move]
        elif total_score == best_score:
            best_moves.append(move)
    
    # 随机选择最佳候选（避免固定模式）
    return random.choice(best_moves) if best_moves else (0,0)

# GUI兼容性适配
player1 = player  # 保持接口一致

# 测试代码
if __name__ == "__main__":
    # 自对战测试
    final_board, score = PlayGame(player1, player1)
    print(f"最终分差: {score}")
    drawBoard(final_board)