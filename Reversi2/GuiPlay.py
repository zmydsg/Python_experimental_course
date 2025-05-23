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
