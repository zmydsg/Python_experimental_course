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
    total_cards = sum(deck_info.values())
    
    # 计算当前牌组中爆牌的概率
    bust_threshold = 21 - player_value
    bust_cards = sum(deck_info.get(card, 0) for card in CARD_TYPES if CARD_VALUES[card] > bust_threshold)
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

# 优化的记牌策略
def improved_card_counting_strategy(hand, dealer_card, deck_info):
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
    mid_cards = sum(deck_info.get(card, 0) for card in ['7', '8', '9'])
    low_cards = sum(deck_info.get(card, 0) for card in ['2', '3', '4', '5', '6'])
    total_cards = sum(deck_info.values())
    
    # 计算当前牌组中爆牌的概率
    bust_threshold = 21 - player_value
    bust_cards = sum(deck_info.get(card, 0) for card in CARD_TYPES if CARD_VALUES[card] > bust_threshold)
    bust_probability = bust_cards / total_cards if total_cards > 0 else 0
    
    # 计算庄家爆牌概率
    dealer_value = CARD_VALUES[dealer_card]
    dealer_bust_prob = 0
    
    # 庄家明牌为2-6时，爆牌概率较高
    if dealer_card in ['2', '3', '4', '5', '6']:
        dealer_bust_prob = 0.4
    # 庄家明牌为7-9时，爆牌概率中等
    elif dealer_card in ['7', '8', '9']:
        dealer_bust_prob = 0.25
    # 庄家明牌为10或A时，爆牌概率低
    else:
        dealer_bust_prob = 0.15
    
    # 根据玩家手牌和庄家明牌制定策略
    
    # 软手牌策略（含A且A可以当作11点）
    if 'A' in hand and player_value <= 21:
        # 软17或以上，停牌
        if player_value >= 19:
            return False
        # 软18，庄家明牌为9、10或A时要牌，否则停牌
        elif player_value == 18 and dealer_card in ['9', '10', 'J', 'Q', 'K', 'A']:
            return True
        # 软13-17，庄家明牌为2-6时停牌，否则要牌
        elif 13 <= player_value <= 17 and dealer_card in ['2', '3', '4', '5', '6']:
            return False
        # 其他软手牌情况要牌
        else:
            return True
    
    # 硬手牌策略
    else:
        # 17或以上，停牌
        if player_value >= 17:
            return False
        # 13-16，庄家明牌为2-6时停牌
        elif 13 <= player_value <= 16 and dealer_card in ['2', '3', '4', '5', '6']:
            return False
        # 12点，庄家明牌为4-6时停牌
        elif player_value == 12 and dealer_card in ['4', '5', '6']:
            return False
        # 11点或以下，要牌
        elif player_value <= 11:
            return True
        # 其他情况，根据爆牌概率和庄家爆牌概率综合决定
        else:
            # 如果庄家爆牌概率高，且自己爆牌概率也高，则停牌
            if dealer_bust_prob > 0.3 and bust_probability > 0.5:
                return False
            # 如果自己爆牌概率低于35%，则要牌
            elif bust_probability < 0.35:
                return True
            # 其他情况停牌
            else:
                return False

# 优化的下注策略
def improved_betting_strategy(deck_info):
    if not deck_info:
        return 1
    
    # 计算牌组中高牌和低牌的比例
    high_cards = sum(deck_info.get(card, 0) for card in ['10', 'J', 'Q', 'K', 'A'])
    low_cards = sum(deck_info.get(card, 0) for card in ['2', '3', '4', '5', '6'])
    total_cards = sum(deck_info.values())
    
    if total_cards == 0:
        return 1
    
    # 计算高低牌比例 - 使用Hi-Lo系统
    hi_lo_count = 0
    for card, count in deck_info.items():
        if card in ['2', '3', '4', '5', '6']:
            hi_lo_count += count  # 低牌+1
        elif card in ['10', 'J', 'Q', 'K', 'A']:
            hi_lo_count -= count  # 高牌-1
    
    # 计算真实计数（考虑剩余牌组数量）
    true_count = hi_lo_count / (total_cards / 52) if total_cards >= 52 else hi_lo_count
    
    # 根据真实计数调整下注
    if true_count >= 2:
        return min(10, max(1, int(2 + true_count)))  # 最高下注10分
    elif true_count >= 1:
        return 2
    else:
        return 1  # 保守下注

def main():
    """主函数"""
    print("开始21点游戏模拟...")
    
    # 创建两个游戏实例，一个使用原始策略，一个使用改进策略
    original_game = Game(num_rounds=10000)
    original_game.player = Player("原始策略玩家", strategy=card_counting_strategy, bet_strategy=card_counting_bet_strategy)
    
    improved_game = Game(num_rounds=10000)
    improved_game.player = Player("改进策略玩家", strategy=improved_card_counting_strategy, bet_strategy=improved_betting_strategy)
    
    # 运行游戏
    print("运行原始策略...")
    original_results = original_game.play_game()
    original_analysis = analyze_results(original_results["results"])
    
    print("运行改进策略...")
    improved_results = improved_game.play_game()
    improved_analysis = analyze_results(improved_results["results"])
    
    # 输出原始策略结果
    print(f"\n原始策略结果分析 (共{len(original_results['results'])}局):")
    print(f"玩家获胜: {original_analysis['player_wins']} 局 ({original_analysis['player_win_rate']:.2%})")
    print(f"庄家获胜: {original_analysis['dealer_wins']} 局 ({original_analysis['dealer_wins']/len(original_results['results']):.2%})")
    print(f"平局: {original_analysis['ties']} 局 ({original_analysis['ties']/len(original_results['results']):.2%})")
    print(f"平均下注: {original_analysis['avg_bet']:.2f} 分")
    print(f"净得分: {original_analysis['net_points']} 分")
    
    # 输出改进策略结果
    print(f"\n改进策略结果分析 (共{len(improved_results['results'])}局):")
    print(f"玩家获胜: {improved_analysis['player_wins']} 局 ({improved_analysis['player_win_rate']:.2%})")
    print(f"庄家获胜: {improved_analysis['dealer_wins']} 局 ({improved_analysis['dealer_wins']/len(improved_results['results']):.2%})")
    print(f"平局: {improved_analysis['ties']} 局 ({improved_analysis['ties']/len(improved_results['results']):.2%})")
    print(f"平均下注: {improved_analysis['avg_bet']:.2f} 分")
    print(f"净得分: {improved_analysis['net_points']} 分")
    
    # 比较两种策略
    print("\n策略比较:")
    win_rate_diff = improved_analysis['player_win_rate'] - original_analysis['player_win_rate']
    net_points_diff = improved_analysis['net_points'] - original_analysis['net_points']
    
    print(f"胜率差异: {win_rate_diff:.2%} ({'提高' if win_rate_diff > 0 else '降低'})")
    print(f"净得分差异: {net_points_diff} 分 ({'提高' if net_points_diff > 0 else '降低'})")
    
    if net_points_diff > 0:
        print(f"改进策略比原始策略更有效，净得分提高了 {net_points_diff} 分!")
    else:
        print(f"改进策略未能超过原始策略，净得分降低了 {abs(net_points_diff)} 分。")

if __name__ == "__main__":
    main()