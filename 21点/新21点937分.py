import random
import numpy as np
from collections import Counter

# 定义牌的值
CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

# 定义牌的类型
CARD_TYPES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Deck:
    def __init__(self, num_decks=6):
        """初始化牌组，默认使用6副牌"""
        self.num_decks = num_decks
        self.reset()
    
    def reset(self):
        """重置牌组"""
        self.cards = []
        for _ in range(self.num_decks):
            for card_type in CARD_TYPES:
                self.cards.extend([card_type] * 4)  # 每种牌有4张
        self.shuffle()
        self.remaining_cards = Counter(self.cards)  # 记录剩余牌的数量
    
    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)
    
    def deal(self):
        """发牌"""
        if len(self.cards) < 10:  # 如果牌不够了，重新洗牌
            self.reset()
        card = self.cards.pop()
        self.remaining_cards[card] -= 1
        return card
    
    def get_remaining_count(self):
        """获取剩余牌的数量"""
        return dict(self.remaining_cards)

class Player:
    def __init__(self, name, strategy=None, bet_strategy=None):
        """初始化玩家"""
        self.name = name
        self.hand = []
        self.score = 0
        self.strategy = strategy
        self.bet_strategy = bet_strategy
        self.bet = 1  # 默认下注1分
    
    def reset_hand(self):
        """重置手牌"""
        self.hand = []
    
    def add_card(self, card):
        """添加一张牌到手中"""
        self.hand.append(card)
    
    def calculate_hand_value(self):
        """计算手牌的点数"""
        value = 0
        aces = 0
        
        for card in self.hand:
            if card == 'A':
                aces += 1
                value += 11
            else:
                value += CARD_VALUES[card]
        
        # 如果点数超过21且有A，则将A的值从11改为1
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
            
        return value
    
    def decide_action(self, dealer_card, deck_info=None):
        """决定行动：要牌(True)或停牌(False)"""
        if self.strategy:
            return self.strategy(self.hand, dealer_card, deck_info)
        else:
            # 默认策略：点数小于17就要牌
            return self.calculate_hand_value() < 17
    
    def decide_bet(self, deck_info=None):
        """决定下注金额"""
        if self.bet_strategy:
            self.bet = self.bet_strategy(deck_info)
        return self.bet

# 庄家策略：超过17点就停牌
def dealer_strategy(hand, dealer_card, deck_info=None):
    value = 0
    aces = 0
    
    for card in hand:
        if card == 'A':
            aces += 1
            value += 11
        else:
            value += CARD_VALUES[card]
    
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1
        
    return value < 17

# 基于记牌的高级策略
def card_counting_strategy(hand, dealer_card, deck_info):
    player_value = 0
    aces = 0
    
    for card in hand:
        if card == 'A':
            aces += 1
            player_value += 11
        else:
            player_value += CARD_VALUES[card]
    
    while player_value > 21 and aces > 0:
        player_value -= 10
        aces -= 1
    
    # 如果已经爆牌，就不要牌
    if player_value > 21:
        return False
    
    # 如果已经21点，就不要牌
    if player_value == 21:
        return False
    
    # 计算牌组中高牌和低牌的比例
    high_cards = sum(deck_info.get(card, 0) for card in ['10', 'J', 'Q', 'K', 'A'])
    low_cards = sum(deck_info.get(card, 0) for card in ['2', '3', '4', '5', '6'])
    
    # 计算当前牌组中爆牌的概率
    bust_threshold = 21 - player_value
    bust_cards = sum(deck_info.get(card, 0) for card in CARD_TYPES if CARD_VALUES[card] > bust_threshold)
    total_cards = sum(deck_info.values())
    bust_probability = bust_cards / total_cards if total_cards > 0 else 0
    
    # 庄家的明牌
    dealer_value = CARD_VALUES[dealer_card]
    
    # 策略决策
    if player_value >= 17:
        # 点数高时，通常停牌
        return False
    elif player_value >= 13 and dealer_value <= 6:
        # 庄家可能爆牌的情况，保守一些
        return False
    elif player_value <= 11:
        # 点数低时，要牌
        return True
    else:
        # 根据爆牌概率决定
        if bust_probability < 0.4:  # 爆牌概率低于40%就要牌
            return True
        else:
            return False

# 基于记牌的下注策略
def card_counting_bet_strategy(deck_info):
    if not deck_info:
        return 1
    
    # 计算牌组中高牌和低牌的比例
    high_cards = sum(deck_info.get(card, 0) for card in ['10', 'J', 'Q', 'K', 'A'])
    low_cards = sum(deck_info.get(card, 0) for card in ['2', '3', '4', '5', '6'])
    total_cards = sum(deck_info.values())
    
    if total_cards == 0:
        return 1
    
    # 计算高低牌比例
    ratio = high_cards / total_cards if total_cards > 0 else 0.5
    
    # 根据比例调整下注
    if ratio > 0.6:  # 高牌比例高，对玩家有利
        return min(10, max(1, int(ratio * 10)))  # 最高下注10分
    else:
        return 1  # 保守下注

class Game:
    def __init__(self, num_rounds=10000):
        """初始化游戏"""
        self.deck = Deck(num_decks=6)
        self.dealer = Player("庄家", strategy=dealer_strategy)
        self.player = Player("玩家", strategy=card_counting_strategy, bet_strategy=card_counting_bet_strategy)
        self.num_rounds = num_rounds
        self.player_score = 0
        self.dealer_score = 0
        self.ties = 0
    
    def play_round(self):
        """进行一轮游戏"""
        # 重置手牌
        self.dealer.reset_hand()
        self.player.reset_hand()
        
        # 获取当前牌组信息
        deck_info = self.deck.get_remaining_count()
        
        # 玩家决定下注
        bet = self.player.decide_bet(deck_info)
        
        # 发牌
        self.player.add_card(self.deck.deal())
        self.dealer.add_card(self.deck.deal())
        self.player.add_card(self.deck.deal())
        self.dealer.add_card(self.deck.deal())
        
        # 玩家回合
        dealer_up_card = self.dealer.hand[0]  # 庄家的明牌
        
        while self.player.decide_action(dealer_up_card, deck_info):
            self.player.add_card(self.deck.deal())
            player_value = self.player.calculate_hand_value()
            if player_value > 21:
                break
        
        # 庄家回合
        if self.player.calculate_hand_value() <= 21:
            while self.dealer.decide_action(None, None):
                self.dealer.add_card(self.deck.deal())
        
        # 计算结果
        player_value = self.player.calculate_hand_value()
        dealer_value = self.dealer.calculate_hand_value()
        
        result = 0  # 0表示平局，1表示玩家赢，-1表示庄家赢
        
        if player_value > 21:
            result = -1  # 玩家爆牌，庄家赢
        elif dealer_value > 21:
            result = 1  # 庄家爆牌，玩家赢
        elif player_value > dealer_value:
            result = 1  # 玩家点数大，玩家赢
        elif player_value < dealer_value:
            result = -1  # 庄家点数大，庄家赢
        
        # 更新分数
        if result == 1:
            self.player_score += bet
        elif result == -1:
            self.player_score -= bet
        
        return result, bet
    
    def play_game(self):
        """进行多轮游戏"""
        results = []
        for _ in range(self.num_rounds):
            result, bet = self.play_round()
            results.append((result, bet))
            
            if result == 1:
                self.player_score += 1
            elif result == -1:
                self.dealer_score += 1
            else:
                self.ties += 1
        
        return {
            "player_score": self.player_score,
            "dealer_score": self.dealer_score,
            "ties": self.ties,
            "net_score": self.player_score - self.dealer_score,
            "results": results
        }

def analyze_results(results):
    """分析游戏结果"""
    player_wins = sum(1 for r, _ in results if r == 1)
    dealer_wins = sum(1 for r, _ in results if r == -1)
    ties = sum(1 for r, _ in results if r == 0)
    
    total_rounds = len(results)
    player_win_rate = player_wins / total_rounds if total_rounds > 0 else 0
    
    total_bet = sum(bet for _, bet in results)
    avg_bet = total_bet / total_rounds if total_rounds > 0 else 0
    
    net_points = sum(r * bet for r, bet in results)
    
    return {
        "player_wins": player_wins,
        "dealer_wins": dealer_wins,
        "ties": ties,
        "player_win_rate": player_win_rate,
        "avg_bet": avg_bet,
        "net_points": net_points
    }

def main():
    """主函数"""
    print("开始21点游戏模拟...")
    game = Game(num_rounds=10000)
    game_results = game.play_game()
    
    analysis = analyze_results(game_results["results"])
    
    print(f"\n游戏结果分析 (共{len(game_results['results'])}局):")
    print(f"玩家获胜: {analysis['player_wins']} 局 ({analysis['player_win_rate']:.2%})")
    print(f"庄家获胜: {analysis['dealer_wins']} 局 ({analysis['dealer_wins']/len(game_results['results']):.2%})")
    print(f"平局: {analysis['ties']} 局 ({analysis['ties']/len(game_results['results']):.2%})")
    print(f"平均下注: {analysis['avg_bet']:.2f} 分")
    print(f"净得分: {analysis['net_points']} 分")
    
    print("\n策略评估:")
    if analysis['net_points'] > 0:
        print(f"该策略成功击败了庄家，净赢得 {analysis['net_points']} 分!")
    else:
        print(f"该策略未能击败庄家，净输掉 {abs(analysis['net_points'])} 分。")

if __name__ == "__main__":
    main()