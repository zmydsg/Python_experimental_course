import random
from collections import deque, Counter
import numpy as np

# ─── 1. 基础：牌值与 Hi-Lo 计数 ────────────────────────────────────────
VALUES = {
    'A':1, '2':2, '3':3, '4':4, '5':5, '6':6,
    '7':7, '8':8, '9':9, '10':10, 'J':10, 'Q':10, 'K':10
}
# Hi-Lo 计数：2–6:+1，7–9:0，10–A:-1
COUNT_MAP = {**{r:+1 for r in ['2','3','4','5','6']},
             **{r:0  for r in ['7','8','9']},
             **{r:-1 for r in ['10','J','Q','K','A']}}


class Shoe:
    """6 副牌的牌靴，发完或剩 < 52 张时重洗"""
    def __init__(self, n_decks=6):
        self.n_decks = n_decks
        self._shuffle()

    def _shuffle(self):
        self.cards = deque()
        single = list(VALUES.keys())
        for _ in range(self.n_decks):
            self.cards.extend(single*4)
        random.shuffle(self.cards)
        self.running_count = 0  # Hi-Lo 跑牌计数
        self.seen = 0          # 已发牌张数

    def draw(self):
        if len(self.cards) < 52:
            self._shuffle()
        c = self.cards.popleft()
        self.running_count += COUNT_MAP[c]
        self.seen += 1
        return c

    def true_count(self):
        decks_remaining = max((len(self.cards) / 52), 0.1)
        return self.running_count / decks_remaining


def hand_value(cards):
    """计算手牌点数，A 可记为 1 或 11"""
    total = sum(VALUES[c] for c in cards)
    # 如果有 A 且不爆，则加 10
    if 'A' in cards and total + 10 <= 21:
        return total + 10
    return total


# ─── 2. 玩家和庄家策略 ──────────────────────────────────────────────────
def dealer_play(shoe):
    hand = [shoe.draw(), shoe.draw()]
    while hand_value(hand) < 17:
        hand.append(shoe.draw())
    return hand_value(hand)

def player_play(shoe, tc, strategy):
    """
    tc: 当前 true count
    strategy: 函数，输入 (hand_cards, tc)，返回是否继续要牌 (True/False)
    """
    hand = [shoe.draw(), shoe.draw()]
    while strategy(hand, tc):
        if hand_value(hand) >= 21:
            break
        hand.append(shoe.draw())
    return hand_value(hand)


# ─── 3. 示例策略：阈值随 True Count 动态变化 ───────────────────────────
def threshold_strategy(hand, tc):
    """
    当点数 < (12 + tc) 时要牌；否则停牌
    也可以改成：12 + k * tc、或者对软 17 做特殊处理
    """
    thresh = 14 + int(tc)  # 基础阈值 12，随 tc 提升
    return hand_value(hand) < thresh


# ─── 4. 动态下注策略 ───────────────────────────────────────────────────
def bet_size(tc, base_bet=1, max_bet=10):
    """
    当 tc>1 时加大下注，否则下基础注
    下注 = base_bet × min(max(tc,1), max_bet)
    """
    return base_bet * min(max(1, int(tc)), max_bet)


# ─── 5. 模拟 N 局 ───────────────────────────────────────────────────────
def simulate(n_rounds=10000, strategy=threshold_strategy):
    shoe = Shoe(n_decks=6)
    total_profit = 0
    records = Counter(win=0, lose=0, push=0)
    for _ in range(n_rounds):
        tc = shoe.true_count()
        bet = bet_size(tc)
        p = player_play(shoe, tc, strategy)
        d = dealer_play(shoe)
        if p > 21 or (d <= 21 and d > p):
            total_profit -= bet
            records['lose'] += 1
        elif d > 21 or p > d:
            total_profit += bet
            records['win'] += 1
        else:
            records['push'] += 1
        # 平局不算输赢
    return total_profit, records

if __name__ == '__main__':
    profit, rec = simulate(n_rounds=10000)
    print(f"10000局后净收益: {profit:.2f}，记录: {rec}")
