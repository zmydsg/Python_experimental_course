import random
import copy
import time

IllegalMove, PlayerError, PlayerSlow, NoMove = [1001, 1002, 1003, 1004]

NeighbourDirection1 = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
NeighbourPosition = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1),
                     (-1, 1), (-1, 0), (-1, -1)]
NeighbourDirection = {'N': (0, -1), 'NE': (1, -1), 'E': (1, 0), 'SE': (1, 1),
                      'S': (0, 1), 'SW': (-1, 1), 'W': (-1, 0), 'NW': (-1, -1)}

Black, White, Empty = [1, -1, 0]
PLAYER_NAMES = {Black: "黑方(电脑)", White: "白方(你)"}
PIECE_CHARS = {Black: "X", White: "O", Empty: "·"}

def BoardInit():
    Board = list(list(Empty for x in range(10)) for y in range(10))
    Board[4][4] = White
    Board[4][5] = Black
    Board[5][5] = White
    Board[5][4] = Black
    return Board

def BoardCopy(Board):
    return copy.deepcopy(Board)

def ValidCell(x, y):
    return (1 <= x <= 8) and (1 <= y <= 8)

def Neighbour(Board, x, y):
    return [Board[x][y-1], Board[x+1][y-1], Board[x+1][y], Board[x+1][y+1],
            Board[x][y+1], Board[x-1][y+1], Board[x-1][y], Board[x-1][y-1]]

def NeighbourCell(Board, Direction, x, y):
    dx, dy = NeighbourDirection[Direction]
    return Board[x + dx][y + dy]

def PossibleMove(Player, Board):
    possible_moves = []
    for x in range(1, 9):
        for y in range(1, 9):
            if Board[x][y] != Empty:
                continue
            has_valid_direction = False
            for i in range(8):
                Direction = NeighbourDirection1[i]
                dx, dy = NeighbourDirection[Direction]
                nx, ny = x + dx, y + dy
                if not ValidCell(nx, ny) or Board[nx][ny] != -Player:
                    continue
                while ValidCell(nx, ny):
                    if Board[nx][ny] == Player:
                        possible_moves.append((x, y))
                        has_valid_direction = True
                        break
                    if Board[nx][ny] == Empty:
                        break
                    nx += dx
                    ny += dy
                if has_valid_direction:
                    break
    return possible_moves

def PlaceMove(Player, Board, x, y):
    if not ValidCell(x, y) or Board[x][y] != Empty:
        print(f"PlaceMove: 无效位置 ({x}, {y})")
        return Board, IllegalMove
    
    valid_directions = []
    for i in range(8):
        Direction = NeighbourDirection1[i]
        dx, dy = NeighbourDirection[Direction]
        nx, ny = x + dx, y + dy
        if not ValidCell(nx, ny) or Board[nx][ny] != -Player:
            continue
        flip_path = []
        while ValidCell(nx, ny):
            if Board[nx][ny] == -Player:
                flip_path.append((nx, ny))
                nx += dx
                ny += dy
            elif Board[nx][ny] == Player:
                valid_directions.append(flip_path)
                break
            else:
                break
    
    if not valid_directions:
        print(f"PlaceMove: 在位置 ({x}, {y}) 没有有效的翻转方向")
        return Board, IllegalMove
    
    Board[x][y] = Player
    for path in valid_directions:
        for (nx, ny) in path:
            Board[nx][ny] = Player
    
    print(f"PlaceMove: 在位置 ({x}, {y}) 成功落子，翻转了 {sum(len(p) for p in valid_directions)} 个棋子")
    return Board, 0

def CountPieces(Board):
    white_count = sum(row.count(White) for row in Board)
    black_count = sum(row.count(Black) for row in Board)
    return white_count, black_count

def print_board(Board):
    print("  1 2 3 4 5 6 7 8")
    print(" +-+-+-+-+-+-+-+-+")
    for y in range(1, 9):
        print(f"{y}|", end="")
        for x in range(1, 9):
            print(f"{PIECE_CHARS[Board[x][y]]}|", end="")
        print(f"\n +-+-+-+-+-+-+-+-+")
    white_count, black_count = CountPieces(Board)
    print(f"当前棋子数 - {PLAYER_NAMES[White]}: {white_count}, {PLAYER_NAMES[Black]}: {black_count}")

def human_player(Colour, Board):
    possible = PossibleMove(Colour, Board)
    if not possible:
        print(f"{PLAYER_NAMES[Colour]}没有可落子的位置，跳过此轮")
        return (0, 0)
    
    print(f"\n{PLAYER_NAMES[Colour]}回合，请选择落子位置(x,y)")
    print("可能的落子位置: ", possible)
    
    while True:
        try:
            move = input("请输入坐标(例如: 3 5)，或输入q退出: ")
            if move.lower() == 'q':
                exit(0)
                
            x, y = map(int, move.split())
            if (x, y) in possible:
                return (x, y)
            print("无效的落子位置，请选择可能的落子位置！")
        except (ValueError, IndexError):
            print("输入格式错误，请输入两个数字，如: 3 5")

ring1 = {(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
         (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8),
         (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (2, 8), (3, 8),
         (4, 8), (5, 8), (6, 8), (7, 8)}
corner1 = {(1,1), (1,8), (8,1), (8,8)}
ring2 = {(2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (7, 2), (7, 3),
         (7, 4), (7, 5), (7, 6), (7, 7), (3, 2), (4, 2), (5, 2), (6, 2),
         (3, 7), (4, 7), (5, 7), (6, 7)}
corner2 = {(2,2), (2,7), (7,2), (7,7)}
ring3 = {(3, 3), (3, 4), (3, 5), (3, 6), (6, 3), (6, 4), (6, 5), (6, 6),
         (4, 3), (5, 3), (4, 6), (5, 6)}
corner3 = {(3,3), (3,6), (6,3), (6,6)}
weight = {0: corner1, 1: ring1, 2: corner3, 3: ring3, 4: ring2-corner2, 5: corner2}
weight2 = {0: ring1, 1: ring3, 2: ring2}

opening_weights = [
    [150, -30, 15, 5, 5, 15, -30, 150],
    [-30, -50, -3, -3, -3, -3, -50, -30],
    [15, -3, 10, 3, 3, 10, -3, 15],
    [5, -3, 3, 1, 1, 3, -3, 5],
    [5, -3, 3, 1, 1, 3, -3, 5],
    [15, -3, 10, 3, 3, 10, -3, 15],
    [-30, -50, -3, -3, -3, -3, -50, -30],
    [150, -30, 15, 5, 5, 15, -30, 150]
]

midgame_weights = [
    [180, -25, 10, 5, 5, 10, -25, 180],
    [-25, -45, -2, -2, -2, -2, -45, -25],
    [10, -2, 8, 2, 2, 8, -2, 10],
    [5, -2, 2, 1, 1, 2, -2, 5],
    [5, -2, 2, 1, 1, 2, -2, 5],
    [10, -2, 8, 2, 2, 8, -2, 10],
    [-25, -45, -2, -2, -2, -2, -45, -25],
    [180, -25, 10, 5, 5, 10, -25, 180]
]

endgame_weights = [
    [220, -15, 0, 0, 0, 0, -15, 220],
    [-15, -40, 0, 0, 0, 0, -40, -15],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [-15, -40, 0, 0, 0, 0, -40, -15],
    [220, -15, 0, 0, 0, 0, -15, 220]
]

def evaluate_position(Colour, board):
    empty_count = sum(row.count(Empty) for row in board)
    if empty_count > 44:
        position_weights = opening_weights
    elif empty_count > 12:
        position_weights = midgame_weights
    else:
        position_weights = endgame_weights

    my_score = 0
    opp_score = 0
    opponent = -Colour

    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] == Colour:
                my_score += position_weights[x - 1][y - 1]
            elif board[x][y] == opponent:
                opp_score += position_weights[x - 1][y - 1]

    my_moves = PossibleMove(Colour, board)
    opp_moves = PossibleMove(opponent, board)
    my_mobility = len(my_moves)
    opp_mobility = len(opp_moves)
    
    mobility_weight = 8 if empty_count > 12 else 5
    my_score += my_mobility * mobility_weight
    opp_score += opp_mobility * mobility_weight

    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    corner_weight = 50  
    for (x, y) in corners:
        if board[x][y] == Colour:
            my_score += corner_weight
        elif board[x][y] == opponent:
            opp_score += corner_weight

    if empty_count <= 20:
        my_stable = count_stable_discs(Colour, board)
        opp_stable = count_stable_discs(opponent, board)
        stable_weight = 20  
        my_score += my_stable * stable_weight
        opp_score += opp_stable * stable_weight

    if opp_mobility == 0 and my_mobility > 0:
        my_score += 30  

    if empty_count <= 12:
        my_discs = sum(1 for row in board for cell in row if cell == Colour)
        opp_discs = sum(1 for row in board for cell in row if cell == opponent)
        disc_diff = my_discs - opp_discs
        my_score += disc_diff * 5

    return my_score - opp_score

def count_stable_discs(Colour, board):
    stable = 0
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] != Colour:
                continue
           
            if x == 1 or x == 8 or y == 1 or y == 8:
                stable += 1
                continue
                
            stable_directions = 0
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx <= 8 and 1 <= ny <= 8 and board[nx][ny] == Colour:
                    stable_directions += 1
                    if stable_directions >= 2:
                        stable += 1
                        break
    return stable

def gives_opponent_corner(Colour, Board, move):
    (x, y) = move
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    adjacent_corners = {
        (1, 1): [(1, 2), (2, 1), (2, 2)],
        (1, 8): [(1, 7), (2, 8), (2, 7)],
        (8, 1): [(7, 1), (8, 2), (7, 2)],
        (8, 8): [(7, 8), (8, 7), (7, 7)]
    }
    opponent = -Colour
    
    for corner in corners:
        if Board[corner[0]][corner[1]] != Empty:
            continue
        if (x, y) in adjacent_corners[corner]:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                nx, ny = corner[0] + dx, corner[1] + dy
                if (nx, ny) == (x, y):
                    return True
    return False

def opening_strategy(Colour, Board, moves):
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    adjacent_to_corners = [(1, 2), (2, 1), (1, 7), (2, 8), (7, 1), (8, 2), (7, 8), (8, 7)]
    
    for move in moves:
        if move in corners:
            return move

    safe_moves = [move for move in moves if not gives_opponent_corner(Colour, Board, move)]
    
    if not safe_moves:
        safe_moves = moves
    
    return search_best_move(Colour, Board, safe_moves, depth=2)

def midgame_strategy(Colour, Board, moves):
    return search_best_move(Colour, Board, moves, depth=3)

def endgame_strategy(Colour, Board, moves, depth):
    empty_count = sum(row.count(Empty) for row in Board)
    
    if empty_count <= 4:
        current_depth = 8  
    elif empty_count <= 8:
        current_depth = 6
    elif empty_count <= 12:
        current_depth = 4
    else:
        current_depth = depth
    
    return search_best_move(Colour, Board, moves, depth=current_depth)

def search_best_move(Colour, Board, moves, depth):
    if not moves:
        return (0, 0)
    
    if len(moves) == 1:
        return moves[0]
    
    opponent = -Colour
    best_move = moves[0]
    best_score = -float('inf')
    alpha = -float('inf')
    beta = float('inf')
    
    moves_sorted = sorted(
        moves,
        key=lambda m: evaluate_position(Colour, PlaceMove(Colour, BoardCopy(Board), *m)[0]),
        reverse=True
    )
    
    max_branches = 15 if depth > 3 else 20
    moves_to_search = moves_sorted[:max_branches]
    
    for (x, y) in moves_to_search:
        new_board, _ = PlaceMove(Colour, BoardCopy(Board), x, y)

        score = alphabeta(
            opponent, new_board, depth - 1, alpha, beta, False, Colour
        )
        
        if score > best_score:
            best_score = score
            best_move = (x, y)

        alpha = max(alpha, best_score)
        
        if alpha >= beta:
            break
    
    return best_move

def alphabeta(player, board, depth, alpha, beta, is_maximizing, Colour):
    moves = PossibleMove(player, board)
    opponent = -player
    
    if depth == 0 or not moves:
        return evaluate_position(Colour, board)
    
    if depth <= 2:
        quick_eval = evaluate_position(Colour, board)
        if is_maximizing and quick_eval > beta:
            return beta
        if not is_maximizing and quick_eval < alpha:
            return alpha
    
    moves_sorted = sorted(
        moves,
        key=lambda m: evaluate_position(player, PlaceMove(player, BoardCopy(board), *m)[0]),
        reverse=is_maximizing
    )

    max_branches = 10 if depth > 3 else 15
    moves_to_search = moves_sorted[:max_branches]
    
    if is_maximizing:
        value = -float('inf')
        for (x, y) in moves_to_search:
            new_board, _ = PlaceMove(player, BoardCopy(board), x, y)
            value = max(value, alphabeta(
                opponent, new_board, depth - 1, alpha, beta, False, Colour
            ))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = float('inf')
        for (x, y) in moves_to_search:
            new_board, _ = PlaceMove(player, BoardCopy(board), x, y)
            value = min(value, alphabeta(
                opponent, new_board, depth - 1, alpha, beta, True, Colour
            ))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

def player(Colour, Board):
    moves = PossibleMove(Colour, Board)
    if not moves:
        return (0, 0)

    empty_count = sum(row.count(Empty) for row in Board)

    if empty_count <= 4:
        for move in moves:
            new_board, _ = PlaceMove(Colour, BoardCopy(Board), *move)
            if not PossibleMove(-Colour, new_board):
                return move
    
    if empty_count > 44:
        return opening_strategy(Colour, Board, moves)
    elif empty_count > 12:
        return midgame_strategy(Colour, Board, moves)
    else:
        return endgame_strategy(Colour, Board, moves, depth=4)

def computer_strategy(Colour, Board):
    return player(Colour, Board)

def PlayGame(show_board=True):
    InternalBoard = BoardInit()
    end = False
    game_round = 1
    black_moves = PossibleMove(Black, InternalBoard)
    if not black_moves:
        print("黑棋(电脑)在初始状态下没有合法移动，游戏将由白棋(你)开始")
    
    if show_board:
        print("===== 黑白棋游戏开始 =====")
        print("你使用白棋(O)，电脑使用黑棋(X)")
        print_board(InternalBoard)
    
    while not end:
        print(f"\n===== 第{game_round}回合 =====")
        
        print(f"\n--- {PLAYER_NAMES[White]}回合 ---")
        white_move = human_player(White, InternalBoard)
        if white_move == (0, 0):
            print(f"{PLAYER_NAMES[White]}没有可落子的位置")
        else:
            InternalBoard, err = PlaceMove(White, InternalBoard, white_move[0], white_move[1])
            if err == IllegalMove:
                print(f"{PLAYER_NAMES[White]}落子无效！请重新选择")
                continue
            if show_board:
                print(f"{PLAYER_NAMES[White]}在位置{white_move}落子")
                print_board(InternalBoard)
        
        black_moves = PossibleMove(Black, InternalBoard)
        white_moves = PossibleMove(White, InternalBoard)
        if not white_moves and not black_moves:
            end = True
            break
        
        print(f"\n--- {PLAYER_NAMES[Black]}回合 ---")
        print("电脑正在思考...")
        start_time = time.perf_counter()
        black_move = computer_strategy(Black, InternalBoard)
        computer_time = time.perf_counter() - start_time
        print(f"电脑思考用时: {computer_time:.2f}秒")
        
        if black_move == (0, 0):
            print(f"{PLAYER_NAMES[Black]}没有可落子的位置")
        else:
            InternalBoard, err = PlaceMove(Black, InternalBoard, black_move[0], black_move[1])
            if err == IllegalMove:
                print(f"{PLAYER_NAMES[Black]}落子无效！")
            else:
                if show_board:
                    print(f"{PLAYER_NAMES[Black]}在位置{black_move}落子")
                    print_board(InternalBoard)
        
        black_moves = PossibleMove(Black, InternalBoard)
        white_moves = PossibleMove(White, InternalBoard)
        if not white_moves and not black_moves:
            end = True
        
        game_round += 1
    
    white_count, black_count = CountPieces(InternalBoard)
    print("\n===== 游戏结束 =====")
    print_board(InternalBoard)
    
    if black_count > white_count:
        print(f"很遗憾，{PLAYER_NAMES[Black]}获胜！")
    elif white_count > black_count:
        print(f"恭喜！{PLAYER_NAMES[White]}获胜！")
    else:
        print("平局！")
    
    print(f"最终棋子数 - {PLAYER_NAMES[White]}: {white_count}, {PLAYER_NAMES[Black]}: {black_count}")
    return InternalBoard, black_count - white_count

def main():
    print("欢迎来到黑白棋单人对战游戏！")
    print("游戏规则:")
    print("1. 你使用白棋(O)，电脑使用黑棋(X)，白方先行")
    print("2. 落子后，夹在自己棋子之间的对手棋子会被翻转")
    print("3. 输入坐标(x,y)进行落子，x和y范围为1-8（例如：3 5 表示第3列第5行）")
    print("4. 输入q可以随时退出游戏\n")
    
    PlayGame()

if __name__ == "__main__":
    main()