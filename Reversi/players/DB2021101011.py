from Reversi import *

corner = {(1, 1), (1, 8), (8, 1), (8, 8)}
edge_positions = {(x, y) for x in range(1, 9) for y in range(1, 9) if x in (1, 8) or y in (1, 8)}
danger_zone = {(1, 2), (1, 7), (2, 1), (2, 8), (7, 1), (7, 8), (8, 2), (8, 7),
               (2, 2), (2, 7), (7, 2), (7, 7), (3, 3), (3, 6), (6, 3), (6, 6)}

position_weight = [
    [2500, -600, 120, 50, 50, 120, -600, 2500],
    [-600, -900, -60, -30, -30, -60, -900, -600],
    [120, -60, 40, 15, 15, 40, -60, 120],
    [50, -30, 15, -40, -40, 15, -30, 50],
    [50, -30, 15, -40, -40, 15, -30, 50],
    [120, -60, 40, 15, 15, 40, -60, 120],
    [-600, -900, -60, -30, -30, -60, -900, -600],
    [2500, -600, 120, 50, 50, 120, -600, 2500]
]


def enhanced_stability(x, y, colour, board):
    stable = 0
    edge_chain = 0

    if (x, y) in edge_positions:
        for dx, dy in [(1, 0), (0, 1)]:
            chain_len = 1
            tx, ty = x + dx, y + dy
            while ValidCell(tx, ty) and board[tx][ty] == colour and (tx, ty) in edge_positions:
                chain_len += 1
                tx += dx
                ty += dy
            tx, ty = x - dx, y - dy
            while ValidCell(tx, ty) and board[tx][ty] == colour and (tx, ty) in edge_positions:
                chain_len += 1
                tx -= dx
                ty -= dy
            edge_chain += chain_len ** 1.5

    for dx, dy in NeighbourPosition:
        path_stable = 0
        tx, ty = x, y
        while ValidCell(tx, ty) and board[tx][ty] == colour:
            path_stable += 1
            tx += dx
            ty += dy
        stable += path_stable * (2 if (dx == 0 or dy == 0) else 1)

    return stable * 10 + edge_chain * 20


def predict_threat(Colour, temp_board):
    opp_moves = PossibleMove(-Colour, temp_board)
    if not opp_moves:
        return 0

    max_threat = 0
    for (ox, oy) in opp_moves:
        threat_board = BoardCopy(temp_board)
        PlaceMove(-Colour, threat_board, ox, oy)
        flipped = sum(row.count(Colour) for row in threat_board) - sum(row.count(Colour) for row in temp_board)
        max_threat = max(max_threat, flipped)
    return max_threat


def player(Colour, Board):
    possible_moves = PossibleMove(Colour, Board)
    if not possible_moves:
        return (0, 0)

    empty_count = sum(row.count(0) for row in Board)
    game_phase = 64 - empty_count
    is_late = empty_count <= 12

    if is_late:
        for move in possible_moves:
            if move in corner:
                return move

    current_edge = {(x, y) for x, y in edge_positions if Board[x][y] == Colour}
    edge_threats = sum(1 for (x, y) in current_edge
                       if any(Board[x + dx][y + dy] == -Colour for dx, dy in NeighbourPosition))

    best_score = -float('inf')
    best_move = possible_moves[0]
    pre_calculated_edge_defense = {move: 0 for move in possible_moves}

    for idx, move in enumerate(possible_moves):
        x, y = move
        pre_calculated_edge_defense[move] = len({(x, y) for x, y in edge_positions if Board[x][y] == Colour} | {(x, y)})

    for move in possible_moves:
        x, y = move
        temp_board = BoardCopy(Board)
        PlaceMove(Colour, temp_board, x, y)

        score = position_weight[x - 1][y - 1] * (1.5 if is_late else 1)

        flipped = sum(row.count(-Colour) for row in temp_board) - sum(row.count(-Colour) for row in Board)
        score += flipped * (15 if is_late else 5)

        edge_defense = pre_calculated_edge_defense[move] - len(current_edge)
        score += edge_defense * 150

        threat = predict_threat(Colour, temp_board)
        score -= threat * (20 if game_phase < 40 else 10)

        score += enhanced_stability(x, y, Colour, temp_board)

        if (x, y) in danger_zone:
            penalty = 1000 if game_phase < 20 else 600 if game_phase < 40 else 300
            score -= penalty

        if 10 < game_phase < 50:
            my_moves = len(PossibleMove(Colour, temp_board))
            opp_moves = len(PossibleMove(-Colour, temp_board))
            score += (my_moves - opp_moves) * (40 if game_phase < 30 else 25)

        if is_late and any(abs(x - c[0]) + abs(y - c[1]) == 1 for c in corner if Board[c[0]][c[1]] == Colour):
            score += 2000

        if score > best_score:
            best_score = score
            best_move = move

    return best_move