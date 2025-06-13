from Reversi import *

def player(Colour, Board) -> tuple[int, int]:
    def get_flips(Board, player, x, y) -> int:
        total_flips = 0
        for dx, dy in NeighbourPosition:
            current_x, current_y = x + dx, y + dy
            flips_in_dir = 0
            while ValidCell(current_x, current_y):
                cell = Board[current_x][current_y]
                if cell == -player:
                    flips_in_dir += 1
                    current_x += dx
                    current_y += dy
                elif cell == player:
                    total_flips += flips_in_dir
                    break
                else:
                    break
        return total_flips

    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)
    
    weight_table = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 100, -20, 10, 5, 5, 10, -20, 100, 0],
        [0, -20, -50, -2, -2, -2, -2, -50, -20, 0],
        [0, 10, -2, -1, -1, -1, -1, -2, 10, 0],
        [0, 5, -2, -1, -1, -1, -1, -2, 5, 0],
        [0, 5, -2, -1, -1, -1, -1, -2, 5, 0],
        [0, 10, -2, -1, -1, -1, -1, -2, 10, 0],
        [0, -20, -50, -2, -2, -2, -2, -50, -20, 0],
        [0, 100, -20, 10, 5, 5, 10, -20, 100, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    
    best_score = -float('inf')
    best_moves = []
    for (x, y) in moves:
        weight_score = weight_table[x][y]
        flips = get_flips(Board, Colour, x, y)
        score = weight_score * 100 + flips
        if score > best_score:
            best_score = score
            best_moves = [(x, y)]
        elif score == best_score:
            best_moves.append((x, y))
    
    return random.choice(best_moves) if best_moves else (0, 0)