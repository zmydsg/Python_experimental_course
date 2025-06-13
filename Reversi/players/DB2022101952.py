from Reversi import *
import random
import time
import copy

# --- 常量定义 ---
CORNERS = [(1,1), (1,8), (8,1), (8,8)]
DIRECTIONS = [(0,-1), (1,-1), (1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1)]

# 位置权重矩阵（更新后的权重）
POSITION_WEIGHTS = [
    [0,    0,    0,    0,    0,    0,    0,    0,    0, 0],
    [0,  500,  -150,  30,   10,   10,   30, -150,  500, 0],
    [0, -150,  -250,   0,    0,    0,    0, -250, -150, 0],
    [0,   30,    0,   10,    5,    5,   10,    0,   30, 0],
    [0,   10,    0,    5,    1,    1,    5,    0,   10, 0],
    [0,   10,    0,    5,    1,    1,    5,    0,   10, 0],
    [0,   30,    0,   10,    5,    5,   10,    0,   30, 0],
    [0, -150,  -250,   0,    0,    0,    0, -250, -150, 0],
    [0,  500,  -150,  30,   10,   10,   30, -150,  500, 0],
    [0,    0,    0,    0,    0,    0,    0,    0,    0, 0]
]

# --- 开局库 ---
OPENING_MOVES = {
    # 标准开局移动
    ((4,5,1), (5,4,1), (4,4,-1), (5,5,-1)): [
        (3,5), (5,3), (4,3), (3,4)  # 常见的开局选择
    ]
}

class ReversiAI:
    def __init__(self):
        self.max_depth = 4  # 初始最大深度
        self.time_limit = 0.95  # 时间限制
        self.start_time = 0
        self.nodes_evaluated = 0
        self.transposition_table = {}  # 置换表

    def is_time_left(self):
        """检查是否还有足够的时间"""
        return time.time() - self.start_time < self.time_limit

    def evaluate_position(self, board, color, phase):
        """根据游戏阶段评估局面"""
        my_moves = PossibleMove(color, board)
        opp_moves = PossibleMove(-color, board)
        move_diff = len(my_moves) - len(opp_moves)

        # 计算棋子数量
        my_pieces = sum(row.count(color) for row in board)
        opp_pieces = sum(row.count(-color) for row in board)
        piece_diff = my_pieces - opp_pieces

        # 位置价值
        position_score = 0
        for i in range(1, 9):
            for j in range(1, 9):
                if board[i][j] == color:
                    position_score += POSITION_WEIGHTS[i][j]
                elif board[i][j] == -color:
                    position_score -= POSITION_WEIGHTS[i][j]

        # 角落控制
        corner_score = 0
        for x, y in CORNERS:
            if board[x][y] == color:
                corner_score += 500
            elif board[x][y] == -color:
                corner_score -= 500

        # 根据游戏阶段调整权重
        if phase == "early":  # 开局 (<=20子)
            return (corner_score * 2.5 +
                   move_diff * 50 +
                   position_score * 1)
        elif phase == "mid":  # 中盘 (21-50子)
            return (corner_score * 2.0 +
                   move_diff * 30 +
                   position_score * 1.5 +
                   piece_diff * 10)
        else:  # 终盘 (>50子)
            return (corner_score * 1.5 +
                   piece_diff * 50 +
                   position_score * 0.5)

    def get_move_ordering(self, moves, board, color):
        """移动排序以提高剪枝效率"""
        move_scores = []
        for move in moves:
            score = 0
            x, y = move
            # 角落最优先
            if move in CORNERS:
                score += 1000
            # 根据位置权重评分
            score += POSITION_WEIGHTS[x][y]
            # 根据翻转数量评分
            temp_board = BoardCopy(board)
            PlaceMove(color, temp_board, x, y)
            score += sum(1 for i in range(1,9) for j in range(1,9) 
                        if temp_board[i][j] == color)
            move_scores.append((score, move))
        return [move for _, move in sorted(move_scores, reverse=True)]

    def alpha_beta(self, board, color, depth, alpha, beta, maximizing):
        """带置换表的Alpha-Beta剪枝搜索"""
        if not self.is_time_left() or depth <= 0:
            return self.evaluate_position(board, color, self.game_phase), None

        moves = PossibleMove(color, board)
        if not moves:
            if not PossibleMove(-color, board):
                # 游戏结束，计算最终分数
                final_score = sum(sum(1 for x in row if x == color) - 
                                sum(1 for x in row if x == -color) 
                                for row in board)
                return final_score * 10000, None
            # 无子可下，交给对手
            score, _ = self.alpha_beta(board, -color, depth-1, -beta, -alpha, not maximizing)
            return -score, None

        ordered_moves = self.get_move_ordering(moves, board, color)
        best_move = ordered_moves[0]
        
        if maximizing:
            max_eval = float('-inf')
            for move in ordered_moves:
                if not self.is_time_left():
                    break
                new_board = BoardCopy(board)
                PlaceMove(color, new_board, move[0], move[1])
                eval_score, _ = self.alpha_beta(new_board, -color, depth-1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in ordered_moves:
                if not self.is_time_left():
                    break
                new_board = BoardCopy(board)
                PlaceMove(color, new_board, move[0], move[1])
                eval_score, _ = self.alpha_beta(new_board, -color, depth-1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def determine_game_phase(self, board):
        """确定游戏阶段"""
        piece_count = sum(sum(1 for x in row if x != 0) for row in board)
        if piece_count <= 20:
            return "early"
        elif piece_count <= 50:
            return "mid"
        else:
            return "late"

    def get_opening_move(self, board):
        """查找开局库中的移动"""
        board_state = tuple((i, j, board[i][j]) 
                          for i in range(1, 9) 
                          for j in range(1, 9) 
                          if board[i][j] != 0)
        if board_state in OPENING_MOVES:
            valid_moves = set(PossibleMove(1, board))
            book_moves = set(OPENING_MOVES[board_state])
            common_moves = valid_moves & book_moves
            if common_moves:
                return random.choice(list(common_moves))
        return None

def player(color, board):
    """主函数入口"""
    ai = ReversiAI()
    ai.start_time = time.time()
    ai.game_phase = ai.determine_game_phase(board)

    # 获取所有可能的移动
    moves = PossibleMove(color, board)
    if not moves:
        return (0, 0)
    if len(moves) == 1:
        return moves[0]

    # 检查开局库
    opening_move = ai.get_opening_move(board)
    if opening_move:
        return opening_move

    # 动态调整搜索深度
    empty_count = sum(row.count(0) for row in board)
    if empty_count <= 8:  # 终局
        ai.max_depth = 6
    elif empty_count <= 16:  # 接近终局
        ai.max_depth = 5
    elif empty_count >= 50:  # 开局
        ai.max_depth = 3

    # 主搜索过程
    _, best_move = ai.alpha_beta(
        board, color, ai.max_depth,
        float('-inf'), float('inf'), True
    )

    return best_move if best_move in moves else moves[0]