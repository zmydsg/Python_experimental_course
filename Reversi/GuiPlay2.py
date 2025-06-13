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
                window[findkey((x,y))].Update(button_color=('white', 'black'))
            elif Board[x][y] == White:
                window[findkey((x,y))].Update(button_color=('black', 'white'))
            else:
                window[findkey((x,y))].Update(button_color=('black', '#007500'))  # Dark green
    (W, B) = CountPlayer(Board)
    window['count'].Update(value='White: '+str(W)+' Black: '+str(B))

def button_color(x,y):
    if (x,y)==(4,4) or (x,y)==(5,5):
        return ('black', 'white')  # White piece (black text on white)
    elif (x,y)==(4,5) or (x,y)==(5,4):
        return ('white', 'black')  # Black piece (white text on black)
    else:
        return ('black', '#007500')  # Empty cell (black text on dark green)

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
            layoutx.append(sg.Button('', size=(3,1), button_color=button_color(x,y),
                        pad=(0,0), border_width=CellBorderWidth, key=findkey((x,y))))
        layout.append(layoutx)
    layout.append([sg.Button('White', button_color=('black', 'white')),
                   sg.Button('Black', button_color=('white', 'black')),
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