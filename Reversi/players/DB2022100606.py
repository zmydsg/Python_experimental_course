from Reversi import *

ring1 = {(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
         (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8),
         (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (2, 8), (3, 8),
         (4, 8), (5, 8), (6, 8), (7, 8)}
coner1 = {(1,1), (1,8), (8,1), (8,8)}
ring2 = {(2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (7, 2), (7, 3),
         (7, 4), (7, 5), (7, 6), (7, 7), (3, 2), (4, 2), (5, 2), (6, 2),
         (3, 7), (4, 7), (5, 7), (6, 7)}
coner2 = {(2,2), (2,7), (7,2), (7,7)}
ring3 = {(3, 3), (3, 4), (3, 5), (3, 6), (6, 3), (6, 4), (6, 5), (6, 6),
         (4, 3), (5, 3), (4, 6), (5, 6)}
coner3 = {(3,3), (3,6), (6,3), (6,6)}
weight = {0: coner1, 1: ring1, 2: coner3, 3: ring3, 4: ring2-coner2, 5: coner2}
weight2 = {0: ring1, 1: ring3, 2: ring2}

# consider rings, coners and neighbour player's cells
# Place the chess-pieces at the outer corners/rings as much as possible
def player(Colour, Board):
    a = set(PossibleMove(Colour, Board))
    la = len(a)
    if la>0:
        for i in range(len(weight)):
            b = list(a & weight[i])
            lb = len(b)
            if lb > 0:
                c = list(Neighbour(Board, b[j][0],b[j][1]).count(Colour) for j in range(lb))
                return b[c.index(max(c))]
    else:
        return (0,0)

def ValidMoveGain(Player, Board, x, y):
    """判断当前落子是否有效，并返回因该落子翻转的对方棋子数量"""
    if not ValidCell(x, y) or Board[x][y] != Empty:
        return 0
    if Neighbour(Board, x, y).count(-1 * Player) == 0:
        return 0

    gain = 0
    for direction in NeighbourDirection1:
        dx, dy = NeighbourDirection[direction]
        nx, ny = x + dx, y + dy
        flipped = 0

        while ValidCell(nx, ny) and Board[nx][ny] == -Player:
            flipped += 1
            nx += dx
            ny += dy
        if flipped > 0 and ValidCell(nx, ny) and Board[nx][ny] == Player:
            gain += flipped
    return gain