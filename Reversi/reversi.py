# from GuiPlay import main
# from player1 import player1
# from player2 import player2
# # main.py - 黑白棋游戏主程序

# #rev - 黑白棋游戏核心逻辑
# 定义常量
empty = 0
white = 1
black = -1

def BoardInit():
    """初始化棋盘"""
    # 创建一个10x10的棋盘（外围一圈用于边界检查）
    Board = [[empty for _ in range(10)] for _ in range(10)]
    # 设置初始的四个棋子
    Board[4][4] = white
    Board[5][5] = white
    Board[4][5] = black
    Board[5][4] = black
    return Board

def IsOnBoard(x, y):
    """检查坐标是否在棋盘上"""
    return 1 <= x <= 8 and 1 <= y <= 8

def IsValidMove(player, board, x, y):
    """检查玩家在(x,y)位置下棋是否合法"""
    # 如果该位置已经有棋子，则不合法
    if board[x][y] != empty:
        return False
    
    # 对手的棋子颜色
    opponent = -player
    
    # 检查八个方向
    directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    
    # 至少要有一个方向可以翻转对手的棋子
    can_flip = False
    
    for dx, dy in directions:
        # 沿着当前方向移动一步
        nx, ny = x + dx, y + dy
        
        # 检查是否有对手的棋子
        if IsOnBoard(nx, ny) and board[nx][ny] == opponent:
            # 继续沿着这个方向移动
            nx += dx
            ny += dy
            
            # 继续检查直到找到自己的棋子或者出界
            while IsOnBoard(nx, ny):
                if board[nx][ny] == empty:
                    break
                if board[nx][ny] == player:
                    can_flip = True
                    break
                nx += dx
                ny += dy
            
            if can_flip:
                return True
    
    return False

def PossibleMove(player, board):
    """返回玩家所有可能的落子位置"""
    moves = []
    
    for x in range(1, 9):
        for y in range(1, 9):
            if IsValidMove(player, board, x, y):
                moves.append((x, y))
    
    return moves

def PlaceMove(player, board, x, y):
    """在(x,y)位置放置玩家的棋子，并翻转对手的棋子"""
    # 创建棋盘的副本
    new_board = [row[:] for row in board]
    
    # 如果不是有效的移动，直接返回原棋盘
    if not IsValidMove(player, board, x, y):
        return board
    
    # 放置棋子
    new_board[x][y] = player
    
    # 对手的棋子颜色
    opponent = -player
    
    # 检查八个方向
    directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    
    for dx, dy in directions:
        # 沿着当前方向移动一步
        nx, ny = x + dx, y + dy
        
        # 检查是否有对手的棋子
        if IsOnBoard(nx, ny) and new_board[nx][ny] == opponent:
            # 继续沿着这个方向移动
            nx += dx
            ny += dy
            
            # 继续检查直到找到自己的棋子或者出界
            found_player = False
            while IsOnBoard(nx, ny):
                if new_board[nx][ny] == empty:
                    break
                if new_board[nx][ny] == player:
                    found_player = True
                    break
                nx += dx
                ny += dy
            
            # 如果找到了自己的棋子，翻转中间的对手棋子
            if found_player:
                nx, ny = x + dx, y + dy
                while new_board[nx][ny] == opponent:
                    new_board[nx][ny] = player
                    nx += dx
                    ny += dy
    
    return new_board

def GetScore(player, board):
    """计算玩家在当前棋盘上的得分"""
    score = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == player:
                score += 1
    return score

def GameOver(board):
    """检查游戏是否结束"""
    # 如果黑白双方都没有可行的移动，游戏结束
    return len(PossibleMove(white, board)) == 0 and len(PossibleMove(black, board)) == 0

def GetWinner(board):
    """获取游戏的赢家"""
    white_score = GetScore(white, board)
    black_score = GetScore(black, board)
    
    if white_score > black_score:
        return white
    elif black_score > white_score:
        return black
    else:
        return empty  # 平局