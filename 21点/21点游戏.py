from typing import List, Optional
import random
from dataclasses import dataclass
from collections import deque
from enum import Enum
import time

class Suit(Enum):
    HEART = "♥"
    DIAMOND = "♦"
    CLUB = "♣"
    SPADE = "♠"

@dataclass
class Card:
    suit: Suit
    value: str
    
    def __str__(self):
        return f"{self.suit.value}{self.value}"
    
    @property
    def points(self) -> int:
        if self.value in "JQK":
            return 10
        elif self.value == "A":
            return 11
        return int(self.value)

class Deck:
    def __init__(self):
        self.cards = deque(
            [Card(suit, value) for suit in Suit 
             for value in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]]
        )
        self.shuffle()
    
    def shuffle(self):
        cards_list = list(self.cards)
        random.shuffle(cards_list)
        self.cards = deque(cards_list)
    
    def deal(self) -> Optional[Card]:
        return self.cards.popleft() if self.cards else None

class Player:
    def __init__(self, name: str, chips: int = 1000):
        self.name = name
        self.chips = chips
        self.hands: List[Card] = []
        self.bet = 0
        
    def place_bet(self, amount: int) -> bool:
        if amount <= self.chips:
            self.bet = amount
            self.chips -= amount
            return True
        return False
    
    @property
    def hand_value(self) -> int:
        value = 0
        aces = 0
        for card in self.hands:
            if card.value == "A":
                aces += 1
            else:
                value += card.points
        
        for _ in range(aces):
            if value + 11 <= 21:
                value += 11
            else:
                value += 1
        return value
    
    def show_hand(self, hide_first: bool = False) -> str:
        if not self.hands:
            return "无牌"
        cards = self.hands[1:] if hide_first else self.hands
        return " ".join(str(card) for card in cards)

class blackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.dealer = Player("庄家")
        self.players: List[Player] = []
    
    def add_player(self, name: str, chips: int = 1000):
        self.players.append(Player(name, chips))
    
    def play_round(self):
        # 接受下注
        for player in self.players:
            while True:
                try:
                    bet = int(input(f"{player.name} 当前筹码: {player.chips}, 请下注: "))
                    if player.place_bet(bet):
                        break
                    print("筹码不足，请重新下注！")
                except ValueError:
                    print("请输入有效的数字！")
        
        # 发初始牌
        for _ in range(2):
            for player in self.players:
                player.hands.append(self.deck.deal())
            self.dealer.hands.append(self.deck.deal())
        
        # 显示初始牌
        print(f"\n庄家的牌: {self.dealer.show_hand(hide_first=True)} [?]")
        for player in self.players:
            print(f"{player.name}的牌: {player.show_hand()} (点数: {player.hand_value})")
        
        # 玩家回合
        for player in self.players:
            while player.hand_value < 21:
                action = input(f"\n{player.name} 的回合 (当前点数: {player.hand_value})\n要牌(h)还是停牌(s)? ").lower()
                if action == 'h':
                    card = self.deck.deal()
                    player.hands.append(card)
                    print(f"抽到: {card}")
                    print(f"当前牌: {player.show_hand()}")
                elif action == 's':
                    break
        
        # 庄家回合
        print(f"\n庄家的牌: {self.dealer.show_hand()}")
        while self.dealer.hand_value < 17:
            card = self.deck.deal()
            self.dealer.hands.append(card)
            print(f"庄家要牌: {card}")
            time.sleep(1)
        
        # 结算
        dealer_value = self.dealer.hand_value
        print(f"\n庄家最终点数: {dealer_value}")
        
        for player in self.players:
            player_value = player.hand_value
            print(f"\n{player.name} 的点数: {player_value}")
            
            if player_value > 21:
                print(f"{player.name} 爆牌了！损失 {player.bet} 筹码")
            elif dealer_value > 21 or player_value > dealer_value:
                win = player.bet * 2
                player.chips += win
                print(f"{player.name} 赢了！获得 {win} 筹码")
            elif player_value == dealer_value:
                player.chips += player.bet
                print(f"{player.name} 平局！返还 {player.bet} 筹码")
            else:
                print(f"{player.name} 输了！损失 {player.bet} 筹码")
            
            player.hands.clear()
            player.bet = 0
        
        self.dealer.hands.clear()
        if len(self.deck.cards) < 20:
            self.deck = Deck()

if __name__ == "__main__":
    game = blackjackGame()
    game.add_player("玩家1")
    game.add_player("玩家2")
    
    while True:
        print("\n" + "="*50)
        print("新一轮游戏开始！")
        game.play_round()
        
        if not any(player.chips > 0 for player in game.players):
            print("\n所有玩家都破产了！游戏结束！")
            break
            
        play_again = input("\n是否继续游戏？(y/n) ").lower()
        if play_again != 'y':
            break
    
    print("\n游戏结束！")
    for player in game.players:
        print(f"{player.name} 最终筹码: {player.chips}")