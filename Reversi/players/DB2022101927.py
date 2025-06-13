from Reversi import *

# 位置权重表 (8x8)
POSITION_WEIGHTS = (
    (100, -20, 10, 5, 5, 10, -20, 100),
    (-20, -40, -5, -5, -5, -5, -40, -20),
    (10, -5, 15, 3, 3, 15, -5, 10),
    (5, -5, 3, 3, 3, 3, -5, 5),
    (5, -5, 3, 3, 3, 3, -5, 5),
    (10, -5, 15, 3, 3, 15, -5, 10),
    (-20, -40, -5, -5, -5, -5, -40, -20),
    (100, -20, 10, 5, 5, 10, -20, 100)
)

# 角落位置
CORNERS = ((1, 1), (1, 8), (8, 1), (8, 8))

# 危险区域 (可能导致对手占据角落)
DANGER_ZONES = (
    (2, 2), (2, 7), (7, 2), (7, 7),
    (1, 2), (2, 1), (1, 7), (2, 8),
    (7, 1), (8, 2), (7, 8), (8, 7)
)

CountPlayer = lambda color, board: sum(board[i].count(color) for i in range(1, 9))


def evaluate_board(my_color, board, my_moves, opp_moves):
    """评估棋盘状态"""
    score = 0
    opp_color = -my_color
    # 1. 棋子位置权重
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == my_color:
                score += POSITION_WEIGHTS[x - 1][y - 1]
            elif board[x][y] == opp_color:
                score -= POSITION_WEIGHTS[x - 1][y - 1]

    # 2. 行动力评估
    score += (my_moves - opp_moves) * 10

    # 3. 角落控制
    for corner in CORNERS:
        x, y = corner
        if board[x][y] == my_color:
            score += 50
        elif board[x][y] == opp_color:
            score -= 50
    # 4. 潜在威胁评估
    score -= evaluate_threats(my_color, board)
    return score


def evaluate_threats(color, board):
    """评估潜在威胁"""
    threat_score = 0
    opp_color = -color

    # 检查对手能否占据角落
    for corner in CORNERS:
        x, y = corner
        if board[x][y] == Empty:
            # 检查对手是否能直接占据这个角落
            for dx, dy in NeighbourPosition:
                nx, ny = x + dx, y + dy
                if ValidCell(nx, ny) and board[nx][ny] == opp_color:
                    threat_score += 30
                    break

    # 检查危险区域
    for danger in DANGER_ZONES:
        x, y = danger
        if board[x][y] == opp_color:
            threat_score += 10

    return threat_score


def player(color, board):
    moves = PossibleMove(color, board)
    if not moves:
        return (0,0)
    if len(moves)==1:
        return moves[0]
    ts = 80-CountPlayer(Empty, board)
    we1 = []
    opp=-color
    for m in moves:
        nb = BoardCopy(board)
        PlaceMove(color, nb, *m)
        opp_moves = PossibleMove(opp, nb)
        s=-evaluate_board(color, nb, len(moves), len(opp_moves))
        if m in CORNERS:
            s+=200
        elif m in DANGER_ZONES:
            s-=30
        else:
            s += POSITION_WEIGHTS[m[0]-1][m[1]-1]
        we1.append((s, m, nb, opp_moves))
    we1 = sorted(we1, reverse=True, key=lambda x:x[0])[:5]
    he1=[[] for i in range(len(we1))]
    hes=[]
    for (s,m,nb, ops),he in zip(we1, he1):
        x=CountPlayer(opp, nb)
        hes.append(x)
        l=len(ops)
        for op in ops:
            npb = BoardCopy(nb)
            PlaceMove(opp, npb, *op)
            ms = PossibleMove(color, npb)
            if op in CORNERS:
                ps=500
            else:
                ps=evaluate_board(opp, npb, l, len(ms))
                if op in DANGER_ZONES:
                    ps-=50
                else:
                    ps += POSITION_WEIGHTS[op[0]-1][op[1]-1]
            c = CountPlayer(opp, npb)
            ps += 5*(c-x-1)
            safe_moves = [m for m in ms if m not in DANGER_ZONES]
            if not safe_moves:
                ps += 100
                if not ms:
                    ps += 100
            zs=[]
            for m in safe_moves:
                zpb=BoardCopy(npb)
                PlaceMove(color, zpb, *m)
                ps-=(CountPlayer(opp,zpb)-1-c)*3
                zs.append(zpb)
            he.append((ps, op, npb, ms, c, safe_moves, zs))
        he.sort(reverse=True, key=lambda x:x[0])

    cs=[]
    if ts < 20:  # 开局
        opa= 2
    elif ts < 50:  # 中局
        opa= 4
    else:  # 残局
        opa= 5
    me=[]
    for (s,m,nb, ops),he,x in zip(we1, he1, hes):
        l=len(ops)
        for ps,op,npb,ms,c,sv,zs in he[:3]:
            my_moves = CountPlayer(color, npb)
            s -= ps
            if ms in DANGER_ZONES:
                s -= 40
            elif ms in CORNERS:
                s += 70
            elif sv:
                s += max(POSITION_WEIGHTS[mi[0]-1][mi[1]-1] for mi in sv)/2
            else:
                s -= 100
                if not ms:
                    s -= 1000
            s += (len(sv)-l)*5 + (my_moves - x-1)*opa
            s+= (sum(CountPlayer(color, zb) for zb in zs) - (1 + c)*len(zs)) * 3
            me.append(s)
        cs.append(sum(me)/len(me)/2 + min(me)/2 if me else -500 )
        me.clear()
    return we1[max(range(len(cs)), key=lambda i: cs[i])][1]

