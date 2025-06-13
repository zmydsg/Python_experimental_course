#coding=gb2312

# Python�γ���ĿV3.0 2025ר��ģ��
# �Ż���ڰ���AIģ��

import random
import copy

# ������붨��
IllegalMove, PlayerError, PlayerSlow, NoMove = (1001, 1002, 1003, 1004)

# ���������ֵ䣨8������
NeighbourDirection = {
    'N': (0, -1),   # ��
    'NE': (1, -1),  # ����
    'E': (1, 0),    # ��
    'SE': (1, 1),   # ����
    'S': (0, 1),    # ��
    'SW': (-1, 1),  # ����
    'W': (-1, 0),   # ��
    'NW': (-1, -1)  # ����
}

# ������ɫ����
Black, White, Empty = 1, -1, 0  # ��ɫ���ӣ���ɫ���ӣ���λ

# ս��Ȩ�ؾ���10x10��
WEIGHT_MATRIX = [
    # ��Χ������/�У�������������
    [0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
    # ��1�У�ʵ����Ϸ�У�
    [0, 200, -50, 100,  50,  50, 100, -50, 200,   0],  # �����ֵ200��Σ������-50
    # ��2��
    [0, -50, -75,  10,  10,  10,  10, -75, -50,   0],  # ��Σ������-75
    # ��3��
    [0, 100,  10,  30,  15,  15,  30,  10, 100,   0],  # ��Ե����߼�ֵ
    # ��4-5�У���������
    [0,  50,  10,  15,   5,   5,  15,  10,  50,   0],  # ���ĵͼ�ֵ
    [0,  50,  10,  15,   5,   5,  15,  10,  50,   0],  # �Գ����
    # ��6-8�У�����Գƣ�
    [0, 100,  10,  30,  15,  15,  30,  10, 100,   0],
    [0, -50, -75,  10,  10,  10,  10, -75, -50,   0],
    [0, 200, -50, 100,  50,  50, 100, -50, 200,   0],
    # ��Χ������
    [0,   0,   0,   0,   0,   0,   0,   0,   0,   0],
]

def BoardInit():
    """��ʼ��10x10���̼���ʼ����"""
    board = [[Empty]*10 for _ in range(10)]  # ����ȫ������
    # ���ó�ʼ����
    board[4][4] = White  # d4
    board[5][5] = White  # e5
    board[4][5] = Black  # e4
    board[5][4] = Black  # d5
    return board

def BoardCopy(board):
    """��������״̬���������"""
    return copy.deepcopy(board)

def ValidCell(x, y):
    """��֤�����Ƿ��ڿ���������(1-8)"""
    return 1 <= x <= 8 and 1 <= y <= 8

def Neighbour(board, x, y):
    """��ȡ��ǰ����8����������ڵ�Ԫ��״̬"""
    return {dir: board[x+dx][y+dy] if (0<=x+dx<10 and 0<=y+dy<10) else None
            for dir, (dx, dy) in NeighbourDirection.items()}

def NeighbourCell(board, direction, x, y):
    """��ָ������������ⵥԪ��"""
    dx, dy = NeighbourDirection[direction]
    cells = []
    nx, ny = x+dx, y+dy  # ��ʼλ��
    while 0 <= nx < 10 and 0 <= ny < 10:  # �����߽���
        cells.append(board[nx][ny])
        nx += dx
        ny += dy
    return cells

def PossibleMove(player, board):
    """���ɵ�ǰ��ҵ����кϷ��߷����Ż���֤�棩"""
    legal_moves = set()  # ʹ�ü��ϱ����ظ�
    # �������п�����λ��
    for x in range(1, 9):
        for y in range(1, 9):
            if board[x][y] != Empty:
                continue  # �����������ӵ�λ��
            
            # ���8������
            for dx, dy in NeighbourDirection.values():
                nx, ny = x+dx, y+dy  # ����λ��
                # ������֤�������ǶԷ�����
                if not ValidCell(nx, ny) or board[nx][ny] != -player:
                    continue
                
                # �����⣺Ѱ�ұ������ӷ��
                while ValidCell(nx+dx, ny+dy):
                    nx += dx
                    ny += dy
                    # �ҵ������������¼Ϊ�Ϸ��ƶ�
                    if board[nx][ny] == player:
                        legal_moves.add((x, y))
                        break
                    # ������λ����ֹ���
                    elif board[nx][ny] == Empty:
                        break
    return list(legal_moves)

def PlaceMove(player, board, x, y):
    """ִ�����Ӳ���ת�Է�����"""
    if not ValidCell(x, y) or board[x][y] != Empty:
        return board  # ��Ч�ƶ�ֱ�ӷ���
    
    flip_list = []  # ��Ҫ��ת����������
    # ���8������Ŀɷ�ת����
    for dx, dy in NeighbourDirection.values():
        temp_flips = []  # ��ʱ�洢��ǰ����ķ�ת����
        nx, ny = x+dx, y+dy  # ��ʼ���λ��
        
        # �ռ������Է�����
        while ValidCell(nx, ny) and board[nx][ny] == -player:
            temp_flips.append((nx, ny))
            nx += dx
            ny += dy
        
        # ��֤��ֹ������������������
        if ValidCell(nx, ny) and board[nx][ny] == player:
            flip_list.extend(temp_flips)  # ȷ�Ͽɷ�ת
    
    # ����������״̬
    new_board = BoardCopy(board)
    new_board[x][y] = player  # ���õ�ǰ�������
    # ��ת���б���Χ������
    for fx, fy in flip_list:
        new_board[fx][fy] = player
    return new_board

def drawBoard(board):
    """�ı�ģʽ���̿��ӻ�"""
    print("  1 2 3 4 5 6 7 8")  # �б�
    for y in range(1, 9):
        row = [f'{y}|']  # �б�
        for x in range(1, 9):
            piece = board[x][y]
            # ���Ż���ʾ
            row.append('W' if piece == White else 'B' if piece == Black else '.')
        print(' '.join(row))  # �����

def PlayGame(player_white, player_black):
    """��Ϸ���̿����������վ��жϣ�"""
    board = BoardInit()  # ��ʼ������
    current = White       # �׷�����
    consecutive_passes = 0  # ������Ȩ����
    
    while consecutive_passes < 2:  # ˫��������Ȩʱ����
        try:
            # ��ȡ��ǰ����߷�
            if current == White:
                move = player_white(current, BoardCopy(board))
            else:
                move = player_black(current, BoardCopy(board))
            
            # ������Ȩ���
            if move == (0, 0):
                consecutive_passes += 1
                current = -current  # �л����
                continue
                
            # ��֤�߷��Ϸ���
            if move not in PossibleMove(current, board):
                raise IllegalMove  # �����쳣
            
            # ִ���߷���������Ȩ����
            board = PlaceMove(current, board, *move)
            consecutive_passes = 0
            current = -current  # �л����
            
        except Exception as e:
            # ����Ƿ��ƶ�
            if isinstance(e, IllegalMove):
                current = -current
                consecutive_passes += 1
                continue
    
    # �������յ÷�
    white_score = sum(row.count(White) for row in board)
    black_score = sum(row.count(Black) for row in board)
    return board, black_score - white_score  # ���طֲ�

# ��ǿ��AI����
def player(colour, board):
    """��������AI���ߺ���"""
    corners = [(1,1), (1,8), (8,1), (8,8)]  # �Ľ�����
    legal_moves = PossibleMove(colour, board)
    if not legal_moves:
        return (0, 0)  # �޺Ϸ��ƶ�ʱ��Ȩ
    
    # ��һ�����ԣ���������
    corner_moves = [m for m in legal_moves if m in corners]
    if corner_moves:
        return strategic_choice(corner_moves, colour, board)
    
    # �ڶ������ԣ���Ե��ȫ���
    edge_moves = [m for m in legal_moves 
                 if m[0] in (1,8) or m[1] in (1,8)]  # ��Եλ��
    safe_edges = []
    for move in edge_moves:
        # ģ���߷���������ܷ��ý���
        simulated = PlaceMove(colour, board, *move)
        opp_moves = PossibleMove(-colour, simulated)
        if not any(c in opp_moves for c in corners):
            safe_edges.append(move)  # ��ȫ��Եλ��
    
    if safe_edges:
        return strategic_choice(safe_edges, colour, board)
    elif edge_moves:
        return strategic_choice(edge_moves, colour, board)
    
    # ���������ԣ��ۺ�λ���Ż�
    return strategic_choice(legal_moves, colour, board)

def strategic_choice(candidates, colour, board):
    """�����ؾ����㷨"""
    corners = [(1,1), (1,8), (8,1), (8,8)]  # �ڲ�����ȷ������
    best_score = -float('inf')  # ��ʼ��ͷ�
    best_moves = []
    
    for move in candidates:
        # ����1��λ�ü�ֵ��Ȩ�ؾ���
        position_value = WEIGHT_MATRIX[move[0]][move[1]]
        
        # ����2����ʱ�����ԣ����ֿ��ƶ�����
        simulated = PlaceMove(colour, board, *move)
        opp_mobility = len(PossibleMove(-colour, simulated))
        
        # ����3��Ǳ���ȶ��Լӳ�
        edge_bonus = 20 if (move[0] in (1,8) or move[1] in (1,8)) else 0
        corner_bonus = 100 if move in corners else 0
        
        # �ۺ����ֹ�ʽ
        total_score = position_value * 1.5 - opp_mobility * 3 + edge_bonus + corner_bonus           
        
        # �������ѡ��
        if total_score > best_score:
            best_score = total_score
            best_moves = [move]
        elif total_score == best_score:
            best_moves.append(move)
    
    # ���ѡ����Ѻ�ѡ������̶�ģʽ��
    return random.choice(best_moves) if best_moves else (0,0)

# GUI����������
player1 = player  # ���ֽӿ�һ��

# ���Դ���
if __name__ == "__main__":
    # �Զ�ս����
    final_board, score = PlayGame(player1, player1)
    print(f"���շֲ�: {score}")
    drawBoard(final_board)