from Reversi import *
def player(Colour,Board):
    thePossibleMove=PossibleMove(Colour,Board)
    if not thePossibleMove:
        return (0,0)

    corner={(1,1),(1,8),(8,1),(8,8)}
    theCornerMove=[move for move in thePossibleMove if move in corner]
    if theCornerMove:
        return random.choice(theCornerMove)

    opponent=-Colour
    record=[]

    for move in thePossibleMove:
        x,y=move
        theBoard=BoardCopy(Board)
        theNewBoard=PlaceMove(Colour,theBoard,x,y)

        theFisrtCount=sum(row.count(Colour) for row in Board)
        theFinalCount=sum(row.count(Colour) for row in theNewBoard)
        flip=theFinalCount-theFisrtCount-1

        edge=(x in (1,8) or y in (1,8))
        theMove=PossibleMove(opponent,theNewBoard)
        theCorner=[m for m in theMove if m in corner]
        danger=len(theCorner)>0
        record.append((move,flip,danger,edge))

    record.sort(key=lambda x:(x[2],-x[1],-x[3]))

    theBestMove=record[0][0]
    return theBestMove