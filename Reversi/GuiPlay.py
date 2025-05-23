from reversi import *
import PySimpleGUI as sg

def find_xy(button):
    return (int(button[1]), int(button[2]))

def find_key(cell):
    return str('b' + str(cell[0]) + str(cell[1]))

def CountPlayer(Board):
    whiteCount = 0
    blackCount = 0
    for i in range(10):
        whiteCount = whiteCount + Board[i].count(white)
        blackCount = blackCount + Board[i].count(black)
    return (whiteCount, blackCount)
    
def BoardUpdate(Board):
    for x in range(1, 9):
        for y in range(1, 9): 
            if Board[x][y] == black:
                window[find_key((x,y))].Update(image_filename='black.png')
            elif Board[x][y] == white:
                window[find_key((x,y))].Update(image_filename='white.png')
            else:
                window[find_key((x,y))].Update(image_filename='empty.png')
    (W, B) = CountPlayer(Board)
    window['count'].Update(value='white: ' + str(W) + ' black: ' + str(B))

def imagefile(x,y):
    if (x,y) == (4,4) or (x,y) == (5,5):
        return 'white.png'
    elif (x,y) == (4,5) or (x,y) == (5,4):
        return 'black.png'
    else:
        return 'empty.png'

def master(computer_player):
    global window
    Board = BoardInit()
    CurrentPlayer = white
    CellSize = (59,59)
    CellBorderWidth = 1
    layout = [[sg.Text('white: 2, black: 2', justification='center',
                       font=("Helvetica", 13), key='count')]]
    for y in range(1,9):
        layout_x = []
        for x in range(1,9):
            layout_x.append(sg.Button(image_filename=imagefile(x,y), image_size=CellSize,
                        pad=(0,0), border_width=CellBorderWidth, key=find_key((x,y))))
        layout.append(layout_x)
    layout.append([sg.Button(image_filename='white.png', image_size=(30,30),
                             image_subsample=2, border_width=CellBorderWidth, key='white'),
                   sg.Button(image_filename='black.png', image_size=(30,30),
                             image_subsample=2, border_width=CellBorderWidth, key='black'),
                   sg.Button('Exit')])

    window = sg.Window('reversi', auto_size_buttons=True, grab_anywhere=False).Layout(layout)

    while True:                 
        event, values = window.Read()  
        if event is None or event == 'Exit':
            break
        elif event == 'white':
            CurrentPlayer = white
            Board = BoardInit()
        elif event == 'black':
            CurrentPlayer = black
            Board = BoardInit()
            (x,y) = computer_player((-1)*CurrentPlayer, Board)
            Board = PlaceMove((-1)*CurrentPlayer, Board, x, y)
        else:
            a = PossibleMove(CurrentPlayer, Board)
            (x,y) = find_xy(event)
            if (len(a) > 0):
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

if __name__ == "__master__":
    master(computer_player = player1)