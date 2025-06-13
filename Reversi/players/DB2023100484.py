from Reversi import *

def player(Colour, Board):
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)

    empty_count = sum(row.count(Empty) for row in Board)
    if empty_count > 40:
        return opening_move(Colour, Board, moves)
    elif empty_count > 12:
        return midgame_move(Colour, Board, moves)
    else:
        return endgame_move(Colour, Board, moves)


def opening_move(Colour, Board, moves):
    position_weights = [
        [0, 500, -50,  25,  10,  10,  25, -50, 500, 0],
        [0, -50, -75,  -8,  -5,  -5,  -8, -75, -50, 0],
        [0,  25,  -8,  20,   5,   5,  20,  -8,  25, 0],
        [0,  10,  -5,   5,   3,   3,   5,  -5,  10, 0],
        [0,  10,  -5,   5,   3,   3,   5,  -5,  10, 0],
        [0,  25,  -8,  20,   5,   5,  20,  -8,  25, 0],
        [0, -50, -75,  -8,  -5,  -5,  -8, -75, -50, 0],
        [0, 500, -50,  25,  10,  10,  25, -50, 500, 0],
        [0,   0,   0,   0,   0,   0,   0,   0,   0, 0]
    ]

    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner

    trap_positions = [(1,2), (2,1), (2,2), (1,7), (2,8), (2,7), (7,1), (8,2), (7,2), (7,8), (8,7), (7,7)]

    best_score = -10**9
    best_move = moves[0]

    for (x, y) in moves:
        base_score = position_weights[x][y]
        flipped = count_flipped(Board, Colour, x, y)
        temp_board = PlaceMove(Colour, BoardCopy(Board), x, y)
        my_mobility = len(PossibleMove(Colour, temp_board))
        opponent_mobility = len(PossibleMove(-Colour, temp_board))
        mobility_diff = my_mobility - opponent_mobility

        opponent_corner = any(corner in PossibleMove(-Colour, temp_board) for corner in corners)
        corner_penalty = -300 if opponent_corner else 0
        edge_penalty = -20 if (x in (2, 7) or y in (2, 7)) else 0
        trap_penalty = -150 if (x, y) in trap_positions else 0

        total_score = (
            0.4 * base_score +
            0.3 * flipped +
            0.2 * mobility_diff +
            corner_penalty +
            edge_penalty +
            trap_penalty
        )

        if total_score > best_score:
            best_score = total_score
            best_move = (x, y)

    return best_move


def midgame_move(Colour, Board, moves):
    position_weights = [
        [0, 200, -30,  20,   8,   8,  20, -30, 200, 0],
        [0, -30, -50,  -5,  -3,  -3,  -5, -50, -30, 0],
        [0,  20,  -5,  15,   4,   4,  15,  -5,  20, 0],
        [0,   8,  -3,   4,   2,   2,   4,  -3,   8, 0],
        [0,   8,  -3,   4,   2,   2,   4,  -3,   8, 0],
        [0,  20,  -5,  15,   4,   4,  15,  -5,  20, 0],
        [0, -30, -50,  -5,  -3,  -3,  -5, -50, -30, 0],
        [0, 200, -30,  20,   8,   8,  20, -30, 200, 0],
        [0,   0,   0,   0,   0,   0,   0,   0,   0, 0]
    ]

    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    trap_positions = [(1,2), (2,1), (2,2), (1,7), (2,8), (2,7), (7,1), (8,2), (7,2), (7,8), (8,7), (7,7)]

    for corner in corners:
        if corner in moves:
            return corner

    best_score = -10**9
    best_move = moves[0]

    for (x, y) in moves:
        base_score = position_weights[x][y]
        flipped = count_flipped(Board, Colour, x, y)
        temp_board = PlaceMove(Colour, BoardCopy(Board), x, y)
        my_mobility = len(PossibleMove(Colour, temp_board))
        opponent_mobility = len(PossibleMove(-Colour, temp_board))
        mobility = (my_mobility - opponent_mobility) / max(1, my_mobility + opponent_mobility)

        opponent_corner = any(corner in PossibleMove(-Colour, temp_board) for corner in corners)
        corner_penalty = -400 if opponent_corner else 0
        edge_penalty = -30 if (x in (2, 7) or y in (2, 7)) else 0
        trap_penalty = -100 if (x, y) in trap_positions else 0

        total_score = (
            0.3 * base_score +
            0.4 * flipped +
            0.3 * mobility * 100 +
            corner_penalty +
            edge_penalty +
            trap_penalty
        )

        if total_score > best_score:
            best_score = total_score
            best_move = (x, y)

    return best_move


def endgame_move(Colour, Board, moves):
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    for corner in corners:
        if corner in moves:
            return corner

    best_score = -10**9
    best_move = moves[0]

    for (x, y) in moves:
        temp_board = PlaceMove(Colour, BoardCopy(Board), x, y)
        opponent_moves = PossibleMove(-Colour, temp_board)
        if any(corner in opponent_moves for corner in corners):
            continue

        current_score = evaluate_board(temp_board, Colour)

        if opponent_moves:
            min_score = 10**9
            for (ox, oy) in opponent_moves:
                opp_board = PlaceMove(-Colour, BoardCopy(temp_board), ox, oy)
                opp_score = evaluate_board(opp_board, Colour)
                min_score = min(min_score, opp_score)
            score = min_score
        else:
            score = current_score * 1.5

        corner_bonus = 100 if (x, y) in corners else 0
        edge_penalty = -50 if (x, y) in [(1, 2), (1, 7), (2, 1), (2, 8),
                                        (7, 1), (7, 8), (8, 2), (8, 7)] else 0

        total_score = score + corner_bonus + edge_penalty

        if total_score > best_score:
            best_score = total_score
            best_move = (x, y)

    return best_move


def count_flipped(Board, Colour, x, y):
    total = 0
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),           (0, 1),
                   (1, -1),  (1, 0),  (1, 1)]:
        tx, ty = x + dx, y + dy
        count = 0
        while 1 <= tx <= 8 and 1 <= ty <= 8 and Board[tx][ty] == -Colour:
            count += 1
            tx += dx
            ty += dy
        if 1 <= tx <= 8 and 1 <= ty <= 8 and Board[tx][ty] == Colour:
            total += count
    return total


def evaluate_board(Board, Colour):
    corner_value = 30
    edge_value = 8
    stable_value = 15

    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    edges = [(1, j) for j in range(2, 8)] + [(8, j) for j in range(2, 8)] + \
            [(i, 1) for i in range(2, 8)] + [(i, 8) for i in range(2, 8)]

    my_score = 0
    opp_score = 0
    my_stable = 0
    opp_stable = 0

    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] == Colour:
                my_score += 1
                if (x, y) in corners:
                    my_score += corner_value
                elif (x, y) in edges:
                    my_score += edge_value
                if is_stable(Board, x, y):
                    my_stable += 1
            elif Board[x][y] == -Colour:
                opp_score += 1
                if (x, y) in corners:
                    opp_score += corner_value
                elif (x, y) in edges:
                    opp_score += edge_value
                if is_stable(Board, x, y):
                    opp_stable += 1

    mobility_factor = 2 * (len(PossibleMove(Colour, Board)) - len(PossibleMove(-Colour, Board)))
    potential_factor = 0.5 * (count_potential_moves(Board, Colour) - count_potential_moves(Board, -Colour))
    stability_factor = 3 * (my_stable - opp_stable)

    return (my_score - opp_score) + mobility_factor + potential_factor + stability_factor


def is_stable(Board, x, y):
    if (x, y) in [(1, 1), (1, 8), (8, 1), (8, 8)]:
        return True
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for dx, dy in directions:
        tx, ty = x, y
        while 1 <= tx+dx <= 8 and 1 <= ty+dy <= 8:
            tx += dx
            ty += dy
            if Board[tx][ty] != Board[x][y]:
                return False
    return True


def count_potential_moves(Board, Colour):
    moves = PossibleMove(Colour, Board)
    potential = 0
    for (x, y) in moves:
        for dx, dy in [(-1,-1), (-1,0), (-1,1),
                       (0,-1),          (0,1),
                       (1,-1),  (1,0),  (1,1)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= 8 and 1 <= ny <= 8 and Board[nx][ny] == Empty:
                potential += 1
    return potential
