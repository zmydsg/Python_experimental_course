
from Reversi import *
def player(Colour, Board):
    legal_moves = PossibleMove(Colour, Board)
    if not legal_moves:
        return (0, 0)

    # 优先级 1: 直接占领角落
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    available_corners = [c for c in corners if c in legal_moves]
    if available_corners:
        return random.choice(available_corners)

    # 优先级 2: 避免让对手获得角落
    danger_zones = [(2, 2), (2, 7), (7, 2), (7, 7), 
                   (1, 2), (2, 1), (1, 7), (2, 8),
                   (7, 1), (8, 2), (7, 8), (8, 7)]
    safe_moves = [m for m in legal_moves if m not in danger_zones]
    if safe_moves:
        legal_moves = safe_moves  # 缩小选择范围

    # 优先级 3: 评估移动的潜在价值
    scored_moves = []
    for move in legal_moves:
        score = 0
        
        # 基础分：边缘位置+20分
        x, y = move
        if x == 1 or x == 8 or y == 1 or y == 8:
            score += 20

        # 对于角落邻近的格子，避免让对手获得角落机会
        for dx, dy in NeighbourPosition:
            nx, ny = x + dx, y + dy
            if (nx, ny) in corners and Board[nx][ny] == Empty:
                score -= 25  # 危险位置扣分

        # 行动力分：使对手下一步可选移动最少
        temp_board = BoardCopy(Board)
        PlaceMove(Colour, temp_board, x, y)
        opponent_moves = PossibleMove(-Colour, temp_board)
        score -= len(opponent_moves) * 3  # 对手选择越少越好

        # 积极扩展：控制棋盘中心（尽量占据中间位置）
        if 3 <= x <= 6 and 3 <= y <= 6:
            score += 7  # 中心位置得分

        # 额外分：增加对边角的控制
        for corner in corners:
            if corner in legal_moves:
                score += 10  # 加分为了更好地控制对方角落

        scored_moves.append((score, move))
    
    # 选择最高分的移动（若有多个则随机）
    scored_moves.sort(reverse=True, key=lambda x: x[0])
    max_score = scored_moves[0][0]
    best_moves = [m for s, m in scored_moves if s == max_score]
    return random.choice(best_moves)