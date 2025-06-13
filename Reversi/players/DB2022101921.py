from Reversi import *

def player(Colour, Board):
    """
    翻转棋策略
    参数:
        Colour: 当前玩家颜色 (1=Black, -1=White)
        Board: 当前棋盘状态
    返回:
        (x, y): 最佳移动位置
    """
    # 获取所有合法移动
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)

    # 根据游戏阶段选择不同策略
    EmptyCount = sum(row.count(Empty) for row in Board)
    if EmptyCount > 40:  # 开局阶段
        return kaijuyidong(Colour, Board, moves)
    elif EmptyCount > 12:  # 中局阶段
        return zhongjuyidong(Colour, Board, moves)
    else:  # 终局阶段
        return jieshuyidong(Colour, Board, moves)


def kaijuyidong(Colour, Board, moves):
    """开局策略：优先占据关键位置和角落"""
    # 棋盘位置权重 (开局)
    PositionWeights = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 500, -50, 30, 10, 10, 30, -50, 500, 0],
        [0, -50, -100, -10, -5, -5, -10, -100, -50, 0],
        [0, 30, -10, 20, 3, 3, 20, -10, 30, 0],
        [0, 10, -5, 3, 3, 3, 3, -5, 10, 0],
        [0, 10, -5, 3, 3, 3, 3, -5, 10, 0],
        [0, 30, -10, 20, 3, 3, 20, -10, 30, 0],
        [0, -50, -100, -10, -5, -5, -10, -100, -50, 0],
        [0, 500, -50, 30, 10, 10, 30, -50, 500, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    # 优先选择角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner

    # 评估每个移动的得分
    BestScore = -float('inf')
    BestMove = moves[0]

    for x, y in moves:
        # 计算位置权重
        score = PositionWeights[x][y]

        # 避免给对手创造角落机会
        TempBoard = BoardCopy(Board)
        TempBoard = PlaceMove(Colour, TempBoard, x, y)
        OpponentMoves = PossibleMove(-Colour, TempBoard)
        OpponentCorner = any(corner in OpponentMoves for corner in corners)
        if OpponentCorner:
            score -= 200  # 严重惩罚会给对手角落机会的移动

        # 计算行动力 (我方可能移动数 - 对方可能移动数)
        MyMobility = len(PossibleMove(Colour, TempBoard))
        OpponentMobility = len(OpponentMoves)
        mobility = MyMobility - OpponentMobility

        # 综合得分
        TotalScore = score + 10 * mobility

        if TotalScore > BestScore:
            BestScore = TotalScore
            BestMove = (x, y)

    return BestMove


def zhongjuyidong(Colour, Board, moves):
    """中局策略：平衡位置权重、行动力和翻转棋子数"""
    # 棋盘位置权重 (中局)
    PositionWeights = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 200, -20, 15, 5, 5, 15, -20, 200, 0],
        [0, -20, -40, -5, -3, -3, -5, -40, -20, 0],
        [0, 15, -5, 10, 2, 2, 10, -5, 15, 0],
        [0, 5, -3, 2, 2, 2, 2, -3, 5, 0],
        [0, 5, -3, 2, 2, 2, 2, -3, 5, 0],
        [0, 15, -5, 10, 2, 2, 10, -5, 15, 0],
        [0, -20, -40, -5, -3, -3, -5, -40, -20, 0],
        [0, 200, -20, 15, 5, 5, 15, -20, 200, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    # 优先选择角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner

    BestScore = -float('inf')
    BestMove = moves[0]

    for x, y in moves:
        # 计算位置权重
        score = PositionWeights[x][y]

        # 计算翻转棋子数
        flipped = jisuanfanzhuanshu(Board, Colour, x, y)

        # 计算行动力
        TempBoard = BoardCopy(Board)
        TempBoard = PlaceMove(Colour, TempBoard, x, y)
        MyMobility = len(PossibleMove(Colour, TempBoard))
        OpponentMobility = len(PossibleMove(-Colour, TempBoard))
        mobility = MyMobility - OpponentMobility

        # 避免给对手创造角落机会
        OpponentMoves = PossibleMove(-Colour, TempBoard)
        OpponentCorner = any(corner in OpponentMoves for corner in corners)
        if OpponentCorner:
            score -= 300  # 严重惩罚会给对手角落机会的移动

        # 综合得分
        TotalScore = 0.4 * score + 0.3 * flipped + 0.3 * mobility

        if TotalScore > BestScore:
            BestScore = TotalScore
            BestMove = (x, y)

    return BestMove


def jieshuyidong(Colour, Board, moves):
    """终局策略：最大化棋子数，使用简单搜索"""
    # 优先选择角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner

    BestScore = -float('inf')
    BestMove = moves[0]

    for x, y in moves:
        TempBoard = BoardCopy(Board)
        TempBoard = PlaceMove(Colour, TempBoard, x, y)

        # 简单评估：棋子数差
        score = pinggu(TempBoard, Colour)

        # 考虑对手的最佳回应
        OpponentMoves = PossibleMove(-Colour, TempBoard)
        if OpponentMoves:
            MinScore = float('inf')
            for ox, oy in OpponentMoves:
                OpponentTempBoard = BoardCopy(TempBoard)
                OpponentTempBoard = PlaceMove(-Colour, OpponentTempBoard, ox, oy)
                OpponentScore = pinggu(OpponentTempBoard, Colour)
                if OpponentScore < MinScore:
                    MinScore = OpponentScore
            score = MinScore

        if score > BestScore:
            BestScore = score
            BestMove = (x, y)

    return BestMove


def jisuanfanzhuanshu(Board, Colour, x, y):
    """计算在(x,y)落子后会翻转多少对手棋子"""
    flipped = 0
    for i in range(8):
        XCurtrent = x
        YCurrent = y
        Direction = NeighbourDirection1[i]
        cell = NeighbourCell(Board, Direction, XCurtrent, YCurrent)
        while ValidCell(XCurtrent, YCurrent):
            if cell == (-1) * Colour:
                XCurtrent += NeighbourDirection[Direction][0]
                YCurrent += NeighbourDirection[Direction][1]
                cell = NeighbourCell(Board, Direction, XCurtrent, YCurrent)
                flipped += 1
                continue
            elif cell == Colour:
                break
            else:
                flipped = 0
                break
    return flipped


def pinggu(Board, Colour):
    """评估棋盘状态"""
    MyCount = 0
    OpponentCount = 0
    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Colour:
                MyCount += 1
            elif Board[x][y] == -Colour:
                OpponentCount += 1
    return MyCount - OpponentCount

if __name__ == "__main__":
    winCount = 0
    player1time = 0
    player2time = 0
    #board,result, PlayTime, error = PlayGame(player2, player1) 
    for i in range(100):
        if i%10 == 0 :
            print("第", i ,"局")
        board,result, PlayTime, error = PlayGame(player, player1) 
        player1time += PlayTime[0]
        player2time += PlayTime[1]
        if(result < 0) :
            winCount += 1
    print("result:",result)
    print("PlayTime:",PlayTime)
    print("winCount:",winCount)
    print("error:",error)
    print("winRate:",winCount/100*100,"%")
    print("player1time:",player1time,"s")
    print("player2time:",player2time,"s")