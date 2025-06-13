from Reversi import *
import random
import time

def count_flips(Colour, Board, x, y):
    flip_count = 0
    for direction in NeighbourDirection1:
        dx, dy = NeighbourDirection[direction]
        tx, ty = x + dx, y + dy
        temp_flips = 0
        
        while ValidCell(tx, ty) and Board[tx][ty] == -Colour:
            temp_flips += 1
            tx += dx
            ty += dy
        
        if ValidCell(tx, ty) and Board[tx][ty] == Colour:
            flip_count += temp_flips
    
    return flip_count

def player(Colour, Board):
    possible_moves = PossibleMove(Colour, Board)
    
    if not possible_moves:
        return (0, 0)
    
    corners = [(1,1), (1,8), (8,1), (8,8)]
    edges = [(x,1) for x in range(2,8)] + [(x,8) for x in range(2,8)] + \
            [(1,y) for y in range(2,8)] + [(8,y) for y in range(2,8)]
    
    corner_moves = [move for move in possible_moves if move in corners]
    if corner_moves:
        return random.choice(corner_moves)
    
    scored_moves = []
    for move in possible_moves:
        score = 0
        
        if move in edges:
            score += 10
        
        temp_board = BoardCopy(Board)
        temp_board = PlaceMove(Colour, temp_board, move[0], move[1])
        opponent_moves = len(PossibleMove(-Colour, temp_board))
        score -= opponent_moves * 0.5  
        
        flipped = count_flips(Colour, Board, move[0], move[1])
        score += flipped * 0.2
        
        adjacent_to_corners = [
            (1,2), (2,1), (2,2),  
            (1,7), (2,7), (2,8), 
            (7,1), (7,2), (8,2),  
            (7,7), (7,8), (8,7)   
        ]
        if move in adjacent_to_corners:
            score -= 15
        
        scored_moves.append((move, score))
    
    scored_moves.sort(key=lambda x: x[1], reverse=True)
    best_score = scored_moves[0][1]
    best_moves = [move for move, score in scored_moves if score == best_score]
    
    return random.choice(best_moves)
