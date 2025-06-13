from Reversi import *
import random
def player(Colour, Board):
    _WEIGHT_TABLE = (
        (0,   0,   0,   0,   0,   0,   0,   0,   0,   0),
        (0, 100, -20,  10,   5,   5,  10, -20, 100,   0),
        (0, -20, -50,  -2,  -2,  -2,  -2, -50, -20,   0),
        (0,  10,  -2,  -1,  -1,  -1,  -1,  -2,  10,   0),
        (0,   5,  -2,  -1,  -1,  -1,  -1,  -2,   5,   0),
        (0,   5,  -2,  -1,  -1,  -1,  -1,  -2,   5,   0),
        (0,  10,  -2,  -1,  -1,  -1,  -1,  -2,  10,   0),
        (0, -20, -50,  -2,  -2,  -2,  -2, -50, -20,   0),
        (0, 100, -20,  10,   5,   5,  10, -20, 100,   0),
        (0,   0,   0,   0,   0,   0,   0,   0,   0,   0)
    )
    def _count_flipped(x, y):
        flipped = 0
        for dx, dy in NeighbourPosition:
            cx, cy = x + dx, y + dy
            temp_flip = 0
            
            while ValidCell(cx, cy) and Board[cx][cy] == -Colour:
                temp_flip += 1
                cx += dx
                cy += dy

            if ValidCell(cx, cy) and Board[cx][cy] == Colour:
                flipped += temp_flip
                
        return flipped

    def _evaluate(x, y):
        """计算移动的综合得分"""
        return _WEIGHT_TABLE[x][y] * 100 + _count_flipped(x, y)


    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)


    max_score = -float('inf')
    candidates = []
    
    for (x, y) in moves:
        score = _evaluate(x, y)
        
        if score > max_score:
            max_score = score
            candidates = [(x, y)]
        elif score == max_score:
            candidates.append((x, y))
    return random.choice(candidates) if candidates else (0, 0)