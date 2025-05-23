# main.py - 黑白棋游戏主程序
from GuiPlay import master 
from player1 import player1
from player2 import player2

if __name__ == "__main__":
    print("黑白棋游戏")
    print("1. 简单AI (贪心策略)")
    print("2. 高级AI (极小极大算法)")
    
    choice = input("请选择AI难度 (1 或 2): ")
    
    if choice == "2":
        master(computer_player=player2)
    else:
        master(computer_player=player1)