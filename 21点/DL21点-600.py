import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam
from collections import deque, Counter
import matplotlib.pyplot as plt

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

class blackjackEnv:
    """21点游戏环境，用于强化学习"""
    def __init__(self, num_decks=6):
        self.deck = Deck(num_decks)
        self.reset()
    
    def reset(self):
        """重置游戏环境"""
        self.deck.reset()
        self.player_hand = []
        self.dealer_hand = []
        
        # 发初始牌
        self.player_hand.append(self.deck.deal())
        self.dealer_hand.append(self.deck.deal())
        self.player_hand.append(self.deck.deal())
        self.dealer_hand.append(self.deck.deal())
        
        self.done = False
        self.reward = 0
        
        return self._get_state()
    
    def step(self, action):
        """执行动作，返回新状态、奖励和是否结束"""
        # action: 0 = 停牌, 1 = 要牌
        if action == 1:  # 要牌
            self.player_hand.append(self.deck.deal())
            player_value = self._calculate_hand_value(self.player_hand)
            
            if player_value > 21:  # 爆牌
                self.done = True
                self.reward = -1
            elif player_value == 21:  # 21点
                self.done = True
                # 庄家回合
                self._dealer_play()
                dealer_value = self._calculate_hand_value(self.dealer_hand)
                
                if dealer_value > 21 or dealer_value < player_value:
                    self.reward = 1
                elif dealer_value > player_value:
                    self.reward = -1
                else:
                    self.reward = 0  # 平局
        else:  # 停牌
            self.done = True
            player_value = self._calculate_hand_value(self.player_hand)
            
            # 庄家回合
            self._dealer_play()
            dealer_value = self._calculate_hand_value(self.dealer_hand)
            
            if dealer_value > 21 or dealer_value < player_value:
                self.reward = 1
            elif dealer_value > player_value:
                self.reward = -1
            else:
                self.reward = 0  # 平局
        
        return self._get_state(), self.reward, self.done
    
    def _dealer_play(self):
        """庄家的回合"""
        while self._calculate_hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.deal())
    
    def _calculate_hand_value(self, hand):
        """计算手牌的点数"""
        value = 0
        aces = 0
        
        for card in hand:
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
    
    def _get_state(self):
        """获取当前状态"""
        player_value = self._calculate_hand_value(self.player_hand)
        dealer_card = CARD_VALUES[self.dealer_hand[0]]
        
        # 统计玩家手牌中的牌
        player_cards = [0] * 13  # 2-10, J, Q, K, A
        for card in self.player_hand:
            if card in ['J', 'Q', 'K']:
                player_cards[9] += 1  # 10点牌
            elif card == 'A':
                player_cards[12] += 1  # A
            else:
                player_cards[int(card) - 2] += 1
        
        # 统计剩余牌组中的牌
        remaining = self.deck.get_remaining_count()
        deck_cards = [0] * 13
        for card, count in remaining.items():
            if card in ['J', 'Q', 'K']:
                deck_cards[9] += count  # 10点牌
            elif card == 'A':
                deck_cards[12] += count  # A
            else:
                deck_cards[int(card) - 2] += count
        
        # 归一化
        total_cards = sum(deck_cards)
        if total_cards > 0:
            deck_cards = [count / total_cards for count in deck_cards]
        
        # 状态向量: [玩家点数/21, 庄家明牌/10, 玩家手牌分布, 牌组分布]
        state = [player_value / 21, dealer_card / 10] + player_cards + deck_cards
        return np.array(state)

class DQNAgent:
    """深度Q网络智能体"""
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=10000)
        self.gamma = 0.95  # 折扣因子1
        self.epsilon = 1.0  # 探索率
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
    
    def _build_model(self):
        """构建神经网络模型"""
        model = Sequential()
        model.add(Dense(128, input_dim=self.state_size, activation='relu'))  # 增加神经元数量
        model.add(Dense(128, activation='relu'))  # 增加神经元数量
        model.add(Dense(64, activation='relu'))   # 增加一层
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model
    
    def update_target_model(self):
        """更新目标网络"""
        self.target_model.set_weights(self.model.get_weights())
    
    def remember(self, state, action, reward, next_state, done):
        """记忆经验"""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state, training=True):
        """选择动作"""
        if training and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state.reshape(1, -1), verbose=0)
        return np.argmax(act_values[0])
    
    def replay(self, batch_size):
        """经验回放"""
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.target_model.predict(next_state.reshape(1, -1), verbose=0)[0])
            
            target_f = self.model.predict(state.reshape(1, -1), verbose=0)
            target_f[0][action] = target
            self.model.fit(state.reshape(1, -1), target_f, epochs=1, verbose=0)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def load(self, name):
        """加载模型"""
        self.model.load_weights(name)
    
    def save(self, name):
        """保存模型"""
        self.model.save_weights(name)

def train_agent(episodes=10000, batch_size=64):
    """训练智能体"""
    env = blackjackEnv()
    state_size = 28  # 玩家点数, 庄家明牌, 玩家手牌分布(13), 牌组分布(13)
    action_size = 2  # 停牌或要牌
    agent = DQNAgent(state_size, action_size)
    
    rewards = []
    win_rates = []
    
    print("开始训练，请稍候...")
    
    for e in range(episodes):
        state = env.reset()
        state = np.reshape(state, [1, state_size])
        
        episode_rewards = []
        
        while True:
            action = agent.act(state[0])
            next_state, reward, done = env.step(action)
            next_state = np.reshape(next_state, [1, state_size])
            
            agent.remember(state[0], action, reward, next_state[0], done)
            state = next_state
            
            episode_rewards.append(reward)
            
            if done:
                agent.update_target_model()
                break
        
        if e % 100 == 0:
            agent.save("blackjack_dqn.h5")
        
        agent.replay(batch_size)
        
        # 记录奖励
        total_reward = sum(episode_rewards)
        rewards.append(total_reward)
        
        # 每1000轮计算一次胜率
        if (e + 1) % 1000 == 0:
            win_rate = evaluate_agent(agent, 1000, verbose=False)
            win_rates.append(win_rate)
            print(f"训练进度: {e+1}/{episodes}, 胜率: {win_rate:.2%}, Epsilon: {agent.epsilon:.2f}")
    
    # 绘制奖励曲线
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(rewards)
    plt.title('奖励曲线')
    plt.xlabel('回合')
    plt.ylabel('奖励')
    
    plt.subplot(1, 2, 2)
    plt.plot(range(1000, episodes + 1, 1000), win_rates)
    plt.title('胜率曲线')
    plt.xlabel('回合')
    plt.ylabel('胜率')
    
    plt.tight_layout()
    plt.savefig('training_curves.png')
    plt.show()
    
    return agent

def evaluate_agent(agent, num_games=10000, verbose=True):
    """评估智能体的表现"""
    env = blackjackEnv()
    wins = 0
    losses = 0
    draws = 0
    
    for _ in range(num_games):
        state = env.reset()
        state = np.reshape(state, [1, 28])
        
        while True:
            action = agent.act(state[0], training=False)
            next_state, reward, done = env.step(action)
            state = np.reshape(next_state, [1, 28])
            
            if done:
                if reward == 1:
                    wins += 1
                elif reward == -1:
                    losses += 1
                else:
                    draws += 1
                break
    
    win_rate = wins / num_games
    loss_rate = losses / num_games
    draw_rate = draws / num_games
    
    if verbose:
        print(f"评估结果 (共{num_games}局):")
        print(f"胜率: {win_rate:.2%}")
        print(f"负率: {loss_rate:.2%}")
        print(f"平局率: {draw_rate:.2%}")
        print(f"净得分: {wins - losses}")
    
    return win_rate

def advanced_strategy(player_value, dealer_card, count_info=None):
    """高级策略，结合基本策略和记牌"""
    dealer_value = CARD_VALUES[dealer_card]
    
    # 如果没有记牌信息，使用基本策略
    if count_info is None:
        # 硬手牌策略
        if player_value >= 17:
            return 0  # 停牌
        elif player_value <= 11:
            return 1  # 要牌
        elif player_value >= 13 and dealer_value <= 6:
            return 0  # 停牌
        elif player_value == 12 and 4 <= dealer_value <= 6:
            return 0  # 停牌
        else:
            return 1  # 要牌
    
    # 使用记牌信息优化决策
    high_cards_ratio = count_info.get('high_ratio', 0.5)
    
    # 根据记牌调整策略
    if player_value >= 17:
        return 0  # 停牌
    elif player_value <= 11:
        return 1  # 要牌
    elif player_value >= 13 and dealer_value <= 6:
        return 0  # 停牌
    elif player_value == 12:
        if 4 <= dealer_value <= 6:
            return 0  # 停牌
        elif high_cards_ratio > 0.6:  # 如果高牌比例高，更容易爆牌
            return 0  # 停牌
        else:
            return 1  # 要牌
    else:  # 玩家点数为13-16
        if dealer_value <= 6:
            return 0  # 停牌
        elif high_cards_ratio > 0.65:  # 如果高牌比例高，更容易爆牌
            return 0  # 停牌
        else:
            return 1  # 要牌

def simulate_games_with_advanced_strategy(num_games=10000):
    """使用高级策略模拟游戏"""
    env = blackjackEnv()
    wins = 0
    losses = 0
    draws = 0
    
    print(f"开始使用高级策略模拟{num_games}局游戏...")
    
    for game in range(num_games):
        env.reset()
        done = False
        
        # 计算记牌信息
        remaining = env.deck.get_remaining_count()
        high_cards = sum(remaining.get(card, 0) for card in ['10', 'J', 'Q', 'K', 'A'])
        total_cards = sum(remaining.values())
        high_ratio = high_cards / total_cards if total_cards > 0 else 0.5
        
        count_info = {'high_ratio': high_ratio}
        
        while not done:
            player_value = env._calculate_hand_value(env.player_hand)
            dealer_card = env.dealer_hand[0]
            
            # 使用高级策略决策
            action = advanced_strategy(player_value, dealer_card, count_info)
            
            _, reward, done = env.step(action)
            
            # 更新记牌信息
            if not done:
                remaining = env.deck.get_remaining_count()
                high_cards = sum(remaining.get(card, 0) for card in ['10', 'J', 'Q', 'K', 'A'])
                total_cards = sum(remaining.values())
                high_ratio = high_cards / total_cards if total_cards > 0 else 0.5
                count_info = {'high_ratio': high_ratio}
        
        if reward == 1:
            wins += 1
        elif reward == -1:
            losses += 1
        else:
            draws += 1
        
        # 显示进度
        if (game + 1) % 1000 == 0:
            print(f"已完成: {game+1}/{num_games} 局")
    
    win_rate = wins / num_games
    loss_rate = losses / num_games
    draw_rate = draws / num_games
    net_score = wins - losses
    
    print(f"\n高级策略模拟结果 (共{num_games}局):")
    print(f"胜率: {win_rate:.2%}")
    print(f"负率: {loss_rate:.2%}")
    print(f"平局率: {draw_rate:.2%}")
    print(f"净得分: {net_score}")
    
    return net_score

def simulate_games_with_dqn(agent, num_games=10000):
    """使用DQN智能体模拟游戏"""
    env = blackjackEnv()
    wins = 0
    losses = 0
    draws = 0
    
    print(f"开始使用DQN智能体模拟{num_games}局游戏...")
    
    for game in range(num_games):
        state = env.reset()
        state = np.reshape(state, [1, 28])
        done = False
        
        while not done:
            action = agent.act(state[0], training=False)
            next_state, reward, done = env.step(action)
            state = np.reshape(next_state, [1, 28])
        
        if reward == 1:
            wins += 1
        elif reward == -1:
            losses += 1
        else:
            draws += 1
        
        # 显示进度
        if (game + 1) % 1000 == 0:
            print(f"已完成: {game+1}/{num_games} 局")
    
    win_rate = wins / num_games
    loss_rate = losses / num_games
    draw_rate = draws / num_games
    net_score = wins - losses
    
    print(f"\nDQN智能体模拟结果 (共{num_games}局):")
    print(f"胜率: {win_rate:.2%}")
    print(f"负率: {loss_rate:.2%}")
    print(f"平局率: {draw_rate:.2%}")
    print(f"净得分: {net_score}")
    
    return net_score

def main():
    """主函数"""
    print("21点游戏自动模拟")
    print("1. 使用深度强化学习 (DQN) 训练智能体")
    print("2. 使用高级策略直接模拟")
    
    choice = input("请选择模式 (1 或 2): ")
    
    if choice == '1':
        # 训练DQN智能体
        print("开始训练DQN智能体...")
        agent = train_agent(episodes=10000, batch_size=64)
        
        # 使用训练好的智能体模拟游戏
        simulate_games_with_dqn(agent, num_games=10000)
    else:
        # 使用高级策略直接模拟
        simulate_games_with_advanced_strategy(num_games=10000)

if __name__ == "__main__":
    main()