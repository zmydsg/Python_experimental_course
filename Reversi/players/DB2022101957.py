import random
import time
import copy

# Error Code for Player
IllegalMove, PlayerError, PlayerSlow, NoMove = [1001, 1002, 1003, 1004]

# list for identifing the "next cell"
NeighbourDirection1 = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
NeighbourPosition = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1),
                     (-1, 1), (-1, 0), (-1, -1)]
NeighbourDirection = {'N':(0,-1), 'NE':(1,-1), 'E':(1,0), 'SE':(1,1),
                      'S':(0,1), 'SW':(-1,1), 'W':(-1,0), 'NW':(-1,-1)}

# define the player color and empty cells
Black, White, Empty = [1, -1, 0]

# to create the new game board
def BoardInit():
    """To create the new game board and to return a 10 X 10 list
    to hold the game. Only cells (1,1) to (8,8) are for the player
    to place. Row 0, Row 10, Column 0 and Column 10 are for non
    player usage (Not part of the board)."""
    Board = list(list(0 for x in range(10)) for y in range(10))
    Board[4][4] = -1
    Board[4][5] = 1
    Board[5][5] = -1
    Board[5][4] = 1
    return Board

# to copy a board
def BoardCopy(Board):
    """To duplicate a board to a new one"""
    return copy.deepcopy(Board)

# to check if the the cell (x,y) is within the board
def ValidCell(x, y):
    """To check if the the cell (x,y) is within the board (True)
    or out of the board (False) """
    return (x > 0) and (x < 9) and (y > 0) and (y < 9)

# to get all the neighbours of cell(x,y)
def Neighbour(Board, x, y):
    """To get the contents of the 8 cells around the current cell (x,y) on
    the Board. These will include the Row 0, Row 10, Column 0 and Column 10
    which are actually out of the board."""
    return [Board[x][y-1], Board[x+1][y-1], Board[x+1][y], Board[x+1][y+1],
            Board[x][y+1], Board[x-1][y+1], Board[x-1][y], Board[x-1][y-1]]

# to get the next cell acording the direction
def NeighbourCell(Board, Direction, x, y):
    '''To get what is in the next cell of the current cell(x,y) on the
    Direction of current Board''' 
    return Board[x+NeighbourDirection[Direction][0]] \
        [y+NeighbourDirection[Direction][1]]


# to find all possible move for the player
def PossibleMove(Player, Board):
    '''To get all of the possible next move for the player on the current
    Board. The return value will be a list content all the (x,y) of possible
    moves'''
    ReturnValue = []
    for x in range(1, 9):
        if Board[x].count(Empty) == 0:
            continue
        for y in range(1, 9):
            if Board[x][y] != Empty or Neighbour(Board, x, y).count(-1*Player) == 0:
                continue
            for i in range(8):
                Direction = NeighbourDirection1[i]
                cell = NeighbourCell(Board, Direction, x, y)
                if (cell != (-1)*Player):
                    continue
                xcurrent = x
                ycurrent = y
                while ValidCell(xcurrent, ycurrent):
                    xcurrent = xcurrent + NeighbourDirection[Direction][0]
                    ycurrent = ycurrent + NeighbourDirection[Direction][1]
                    cell = NeighbourCell(Board, Direction, xcurrent, ycurrent)
                    if (cell == Empty):
                        break
                    elif (cell == Player):
                        ReturnValue.append((x,y))
                        break
                if ReturnValue.count((x,y)) != 0:
                    break
    return ReturnValue

# to place the move on the board
def PlaceMove(Player, Board, x, y):
    '''To place a new piece on the cell(x,y) of the Board for the Player. Then,
    all the non-player's pieces lying on a straight line between the new piece
    and any anchoring Player's pieces.'''
    ValidPath = []
    for i in range(8):
        xcurrent = x
        ycurrent = y
        Direction = NeighbourDirection1[i]
        cell = NeighbourCell(Board, Direction, xcurrent, ycurrent)
        while ValidCell(xcurrent, ycurrent):
            if (cell == (-1)*Player):
                xcurrent = xcurrent + NeighbourDirection[Direction][0]
                ycurrent = ycurrent + NeighbourDirection[Direction][1]
                cell = NeighbourCell(Board, Direction, xcurrent, ycurrent)
                continue
            elif (cell == Player):
                ValidPath.append(i)
            break
    for i in ValidPath:
        xcurrent = x
        ycurrent = y
        Board[xcurrent][ycurrent] = Player
        Direction = NeighbourDirection1[i]
        while ValidCell(xcurrent, ycurrent):
            cell = NeighbourCell(Board, Direction, xcurrent, ycurrent)
            if (cell == (-1)*Player):
                xcurrent = xcurrent + NeighbourDirection[Direction][0]
                ycurrent = ycurrent + NeighbourDirection[Direction][1]
                Board[xcurrent][ycurrent] = Player
                cell = NeighbourCell(Board, Direction, xcurrent, ycurrent)
                if (cell == Player):
                    break
            else:
                break
    return Board
    
# draw the board on screen
def drawBoard(Board):
    Board1 = BoardCopy(Board)
    for x in range(10):
        for y in range(10):
            if Board[x][y] == Black:
                Board1[x][y] = 'X'
            elif Board[x][y] == White:
                Board1[x][y] = 'O'
            else:
                Board1[x][y] = ' '
    HLINE = '  +---+---+---+---+---+---+---+---+'
    VLINE = '  |   |   |   |   |   |   |   |   |'

    print('    1   2   3   4   5   6   7   8')
    print(HLINE)
    for y in range(8):
        print(y+1, end=' ')
        for x in range(8):
            print('| %s' % (Board1[x+1][y+1]), end=' ')
        print('|')
        print(HLINE)

# to launch a game
def PlayGame(PlayerWhite, PlayerBlack):
    '''
    Board, Result, TimeUsed, ErrorMessage = PlayGame(PlayerWhite, PlayerBlack)

    To launch a game between PlayerWhite and PlayerBlack.  PlayerWhite
    will be assigned the White pieces and PlayerBlack wil be assigned the
    Black pieces.  The White one move first. The result will return as how
    many cells the PlayerBlack occupied is more than that occupied by White.

    Both Players are functions with two inputs (Colour, Board) which Colour
    is the "White" or "Black".  Everytime called should return the next move
    in (x,y). In case there is no possible move available, (0,0) should be
    returned.

    In case an error happens, the return value "Result" will carry the error
    code which |Result| > 1000 according to the following coding.
    1001: Illegal Move, 1002: Player Function Error (Error message in "ErrorMessage"),
    1003: A Slow Player, 1004: No Legal Move
    the positive error codes are for PlayerWhite and the negative codes are
    for PlayerBlack'''

    InternalBoard = BoardInit()
    end = False
    PlayTime = [0, 0]
    error = ''
    def play(Colour, InternalBoard):
        ErrMessage = ''
        ErrCode = 0
        a = PossibleMove(Colour, InternalBoard)
        if len(a) != 0:
            try:
                StartTime = time.perf_counter()
                if Colour == White:
                    (x, y) = PlayerWhite(Colour, copy.deepcopy(InternalBoard))
                    time_used = time.perf_counter()-StartTime
                    PlayTime[0] = PlayTime[0]+time_used
                else:
                    (x, y) = PlayerBlack(Colour, copy.deepcopy(InternalBoard))
                    time_used = time.perf_counter()-StartTime
                    PlayTime[1] = PlayTime[1]+time_used
                if time_used > 1.5:
                    print(time_used)
                    ErrCode = PlayerSlow
                if (x,y) in a:
                    InternalBoard = PlaceMove(Colour, InternalBoard, x, y)
                else:
                    ErrCode = IllegalMove
            except Exception as e:
                ErrMessage = str(e).replace('\x1b', '  ')
                ErrCode = PlayerError
                (x, y) = (0, 0)
                print(ErrMessage, ErrCode, Colour)
        else:
            ErrCode = NoMove
            (x, y) = (0, 0)
        return (x, y), ErrCode, ErrMessage, InternalBoard

    while not(end):
        (x, y), ErrCode, ErrMessage, InternalBoard = play(White, InternalBoard)
        #drawBoard(InternalBoard)
        if ErrCode != NoMove:
            if ErrCode != 0:
                return copy.deepcopy(InternalBoard), ErrCode, PlayTime, ErrMessage
        else:
            end = True
        (x, y), ErrCode, ErrMessage, InternalBoard = play(Black, InternalBoard)
        if ErrCode != NoMove:
            if ErrCode != 0:
                return copy.deepcopy(InternalBoard), -1*ErrCode, PlayTime, ErrMessage
            end = False
            
    result = 0
    for x in range(1, 9):
        result = result + sum(InternalBoard[x])
    return copy.deepcopy(InternalBoard), result, PlayTime, error

# a demo player function with new strategy
def player(Colour, Board):
    '''An improved player function with edge-priority strategy.
    It will play as the Colour (Black or White) on the Board.
    Everytime called will return the next move in (x,y). In
    case there is no possible move available, (0,0) will be returned.'''
    
    # Define priority areas
    corners = {(1,1), (1,8), (8,1), (8,8)}
    edges = {(x,1) for x in range(2,8)} | {(x,8) for x in range(2,8)} | \
            {(1,y) for y in range(2,8)} | {(8,y) for y in range(2,8)}
    inner = {(x,y) for x in range(2,8) for y in range(2,8)}
    
    a = PossibleMove(Colour, Board)
    if not a:
        return (0,0)
    
    # Try to take corners first
    available_corners = [move for move in a if move in corners]
    if available_corners:
        return random.choice(available_corners)
    
    # Then try to take edges
    available_edges = [move for move in a if move in edges]
    if available_edges:
        # Among edges, prefer those that don't give opponent corner opportunities
        safe_edges = []
        for move in available_edges:
            # Check if this move would give opponent a corner
            temp_board = BoardCopy(Board)
            temp_board = PlaceMove(Colour, temp_board, move[0], move[1])
            opponent_moves = PossibleMove(-Colour, temp_board)
            gives_corner = any(m in corners for m in opponent_moves)
            if not gives_corner:
                safe_edges.append(move)
        
        if safe_edges:
            return random.choice(safe_edges)
        return random.choice(available_edges)
    
    # For inner moves, prefer those that flip the most pieces
    max_flips = -1
    best_moves = []
    for move in a:
        flip_count = 0
        for direction in NeighbourDirection1:
            x, y = move
            dx, dy = NeighbourDirection[direction]
            x += dx
            y += dy
            temp_flips = 0
            while ValidCell(x, y) and Board[x][y] == -Colour:
                temp_flips += 1
                x += dx
                y += dy
            if ValidCell(x, y) and Board[x][y] == Colour:
                flip_count += temp_flips
        if flip_count > max_flips:
            max_flips = flip_count
            best_moves = [move]
        elif flip_count == max_flips:
            best_moves.append(move)
    
    if best_moves:
        # Among best moves, avoid moves adjacent to corners
        safe_moves = []
        for move in best_moves:
            near_corner = False
            for corner in corners:
                if abs(move[0]-corner[0]) <= 1 and abs(move[1]-corner[1]) <= 1:
                    near_corner = True
                    break
            if not near_corner:
                safe_moves.append(move)
        
        if safe_moves:
            return random.choice(safe_moves)
        return random.choice(best_moves)
    
    return random.choice(a)