# Module for Python course project V3.0 2025
# This module provide a GUI for human vs. computer_player
# The human player default in white  

from Reversi import *
import PySimpleGUI as sg
#from test1 import *

def findxy(button):
    return (int(button[1]),int(button[2]))

def findkey(cell):
    return str('b'+str(cell[0])+str(cell[1]))

def CountPlayer(Board):
    WhiteCount = 0
    BlackCount = 0
    for i in range(10):
        WhiteCount = WhiteCount+Board[i].count(White)
        BlackCount = BlackCount+Board[i].count(Black)
    return (WhiteCount, BlackCount)
    
def BoardUpdate(Board):
    for x in range(1,9):
        for y in range(1,9):
            if Board[x][y] == Black:
                window[findkey((x,y))].Update(image_filename='Black.png')
            elif Board[x][y] == White:
                window[findkey((x,y))].Update(image_filename='White.png')
            else:
                window[findkey((x,y))].Update(image_filename='Empty.png')
    (W, B) = CountPlayer(Board)
    window['count'].Update(value='White: '+str(W)+' Black: '+str(B))

def imagefile(x,y):
    if (x,y)==(4,4) or (x,y)==(5,5):
        return 'White.png'
    elif (x,y)==(4,5) or (x,y)==(5,4):
        return 'Black.png'
    else:
        return 'Empty.png'

def main(computer_player):
    global window
    Board = BoardInit()
    CurrentPlayer = White
    CellSize = (59,59)
    CellBorderWidth = 1
    layout = [[sg.Text('White: 2, Black: 2', justification='center',
                       font=("Helvetica", 13), key='count')]]
    for y in range(1,9):
        layoutx = []
        for x in range(1,9):
            layoutx.append(sg.Button(image_filename=imagefile(x,y), image_size=CellSize,
                        pad=(0,0), border_width=CellBorderWidth, key=findkey((x,y))))
        layout.append(layoutx)
    layout.append([sg.Button(image_filename='White.png', image_size=(30,30),
                             image_subsample=2, border_width=CellBorderWidth, key='White'),
                   sg.Button(image_filename='Black.png', image_size=(30,30),
                             image_subsample=2, border_width=CellBorderWidth, key='Black'),
                   sg.Button('Exit')])

    window = sg.Window('Reversi', auto_size_buttons=True, grab_anywhere=False).Layout(layout)

    # Event Loop
    while True:                 
        event, values = window.Read()  
        if event is None or event == 'Exit':
            break
        elif event == 'White':
            CurrentPlayer = White
            Board = BoardInit()

        elif event == 'Black':
            CurrentPlayer = Black
            Board = BoardInit()
            (x,y) = computer_player((-1)*CurrentPlayer, Board)
            Board = PlaceMove((-1)*CurrentPlayer, Board, x, y)
        else:
            a = PossibleMove(CurrentPlayer, Board)
            (x,y)=findxy(event)
            if (len(a)>0):
                if ((x,y) in a):
                    Board = PlaceMove(CurrentPlayer, Board, x, y)
                    BoardUpdate(Board)
                    (x,y) = computer_player((-1)*CurrentPlayer, Board)
                    Board = PlaceMove((-1)*CurrentPlayer, Board, x, y)
            else:
                (x,y) = computer_player((-1)*CurrentPlayer, Board)
                Board = PlaceMove((-1)*CurrentPlayer, Board, x, y)
        BoardUpdate(Board)
    window.Close()

if __name__ == "__main__":
    main(computer_player = player1)
    
# [filename] Reversi.py
# [file content begin]
White = 1
Black = -1
Empty = 0

def BoardInit():
    """初始化10x10棋盘（包含边框）"""
    board = [[Empty]*10 for _ in range(10)]
    for i in range(1, 9):
        board[0][i] = board[9][i] = board[i][0] = board[i][9] = -2  # 边界标记
    board[4][4] = board[5][5] = White
    board[4][5] = board[5][4] = Black
    return board

def GetValidMoves(player, board):
    """获取当前玩家的合法移动位置"""
    moves = set()
    directions = [(-1,-1), (-1,0), (-1,1),
                  (0,-1),         (0,1),
                  (1,-1),  (1,0),  (1,1)]
    
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] != Empty:
                continue
                
            for dx, dy in directions:
                nx, ny = x+dx, y+dy
                temp_flips = []
                found_opponent = False
                
                while 1 <= nx <= 8 and 1 <= ny <= 8:
                    if board[nx][ny] == -player:
                        temp_flips.append((nx, ny))
                        nx += dx
                        ny += dy
                        found_opponent = True
                    elif board[nx][ny] == player and found_opponent:
                        moves.add((x, y))
                        break
                    else:
                        break
    return list(moves)

def PlaceMove(player, board, x, y):
    """执行落子并翻转对方棋子"""
    if x < 1 or x > 8 or y < 1 or y > 8:
        return board
    
    directions = [(-1,-1), (-1,0), (-1,1),
                  (0,-1),         (0,1),
                  (1,-1),  (1,0),  (1,1)]
    
    board[x][y] = player
    flipped = []
    
    for dx, dy in directions:
        temp_flip = []
        nx, ny = x+dx, y+dy
        
        while 1 <= nx <= 8 and 1 <= ny <= 8:
            if board[nx][ny] == -player:
                temp_flip.append((nx, ny))
                nx += dx
                ny += dy
            elif board[nx][ny] == player:
                flipped += temp_flip
                break
            else:
                break
    
    for fx, fy in flipped:
        board[fx][fy] = player
    
    return board

def player(Colour, Board):
    """标准玩家接口：接收颜色和棋盘，返回落子坐标"""
    valid_moves = GetValidMoves(Colour, Board)
    if valid_moves:
        return random.choice(valid_moves)
    return (0, 0)  # 无有效移动时返回(0,0)

def CheckGameOver(board):
    """检查游戏是否结束"""
    return not GetValidMoves(White, board) and not GetValidMoves(Black, board)

import random
# [file content end]

# [filename] GuiPlay.py
# [file content begin]（保持用户原始内容，仅修改函数调用）
# ...（保持用户提供的原始内容不变）...
if __name__ == "__main__":
    main(computer_player=player)  # 关键修改：使用标准player接口
# [file content end]