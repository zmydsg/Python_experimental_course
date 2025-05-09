import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Input, Concatenate
from tensorflow.keras.optimizers import Adam
from collections import deque, Counter
import matplotlib.pyplot as plt
import os

# 设置TensorFlow日志级别，减少不必要的警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 定义牌的值
CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

# 定义牌的类型
CARD_TYPES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class SumTree:
    """用于优先经验回放的和树数据结构"""
    def __init__(self, capacity):
        self.capacity = capacity  # 叶节点数量
        self.tree = np.zeros(2 * capacity - 1)  # 树的节点总数
        self.data = np.zeros(capacity, dtype=object)  # 存储经验数据
        self.data_pointer = 0  # 指向下一个可用的数据位置
        self.size = 0  # 当前存储的经验数量
    
    def add(self, priority, data):
        """添加新的经验"""
        tree_idx = self.data_pointer + self.capacity - 1  # 叶节点索引
        self.data[self.data_pointer] = data  # 存储经验数据
        self.update(tree_idx, priority)  # 更新优先级
        
        self.data_pointer = (self.data_pointer + 1) % self.capacity  # 循环使用存储空间
        if self.size < self.capacity:
            self.size += 1
    
    def update(self, tree_idx, priority):
        """更新节点优先级"""
        change = priority - self.tree[tree_idx]
        self.tree[tree_idx] = priority
        
        # 向上传播变化
        while tree_idx != 0:
            tree_idx = (tree_idx - 1) // 2
            self.tree[tree_idx] += change
    
    def get_leaf(self, v):
        """获取叶节点"""
        parent_idx = 0
        
        while True:
            left_idx = 2 * parent_idx + 1
            right_idx = left_idx + 1
            
            # 如果到达叶节点，返回
            if left_idx >= len(self.tree):
                leaf_idx = parent_idx
                break
            
            # 向下搜索
            if v <= self.tree[left_idx]:
                parent_idx = left_idx
            else:
                v -= self.tree[left_idx]
                parent_idx = right_idx
        
        data_idx = leaf_idx - (self.capacity - 1)
        return leaf_idx, self.tree[leaf_idx], self.data[data_idx]
    
    def total_priority(self):
        """返回总优先级"""
        return self.tree[0]

class PrioritizedReplayBuffer:
    """优先经验回放缓冲区"""
    def __init__(self, capacity, alpha=0.6, beta=0.4, beta_increment=0.001):
        self.tree = SumTree(capacity)
        self.alpha = alpha  # 优先级指数
        self.beta = beta  # 重要性采样指数
        self.beta_increment = beta_increment  # beta增量
        self.max_priority = 1.0  # 最大优先级
    
    def add(self, experience):
        """添加经验"""
        priority = self.max_priority ** self.alpha
        self.tree.add(priority, experience)
    
    def sample(self, batch_size):
        """采样经验"""
        batch = []
        indices = []
        priorities = []
        segment = self.tree.total_priority() / batch_size
        
        self.beta = min(1.0, self.beta + self.beta_increment)  # beta逐渐增加到1
        
        for i in range(batch_size):
            a = segment * i
            b = segment * (i + 1)
            v = np.random.uniform(a, b)
            
            idx, priority, experience = self.tree.get_leaf(v)
            
            indices.append(idx)
            priorities.append(priority)
            batch.append(experience)
        
        # 计算重要性权重
        sampling_probabilities = np.array(priorities) / self.tree.total_priority()
        weights = (self.tree.size * sampling_probabilities) ** (-self.beta)
        weights /= weights.max()  # 归一化权重
        
        return batch, indices, np.array(weights)
    
    def update_priorities(self, indices, priorities):
        """更新优先级"""
        for idx, priority in zip(indices, priorities):
            priority = (priority + 1e-5) ** self.alpha  # 添加小值防止优先级为0
            self.max_priority = max(self.max_priority, priority)
            self.tree.update(idx, priority)
    
    def __len__(self):
        """返回当前存储的经验数量"""
        return self.tree.size

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

class BlackjackEnv:
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
                    self.reward = 1.5  # 21点给予更高奖励
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
        
        # 检查是否有A
        has_usable_ace = 0
        if 'A' in self.player_hand and player_value <= 21:
            has_usable_ace = 1
        
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
        
        # 状态向量: [玩家点数/21, 庄家明牌/10, 是否有可用A, 玩家手牌分布, 牌组分布]
        state = [player_value / 21, dealer_card / 10, has_usable_ace] + player_cards + deck_cards
        return np.array(state)

class DoubleDQNAgent:
    """双重深度Q网络智能体"""
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = PrioritizedReplayBuffer(capacity=50000)
        self.gamma = 0.99  # 折扣因子
        self.epsilon = 1.0  # 探索率
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995
        self.learning_rate = 0.0005
        self.tau = 0.001  # 软更新参数
        
        # 创建主网络和目标网络
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
    
    def _build_model(self):
        """构建神经网络模型"""
        # 使用函数式API构建更复杂的网络
        input_layer = Input(shape=(self.state_size,))
        
        # 分离输入的不同部分
        player_dealer = tf.slice(input_layer, [0, 0], [-1, 3])  # 玩家点数、庄家明牌、是否有A
        player_cards = tf.slice(input_layer, [0, 3], [-1, 13])  # 玩家手牌分布
        deck_cards = tf.slice(input_layer, [0, 16], [-1, 13])   # 牌组分布
        
        # 处理玩家和庄家信息
        x1 = Dense(64, activation='relu')(player_dealer)
        x1 = Dense(32, activation='relu')(x1)
        
        # 处理玩家手牌分布
        x2 = Dense(64, activation='relu')(player_cards)
        x2 = Dense(32, activation='relu')(x2)
        
        # 处理牌组分布
        x3 = Dense(64, activation='relu')(deck_cards)
        x3 = Dense(32, activation='relu')(x3)
        
        # 合并所有特征
        merged = Concatenate()([x1, x2, x3])
        
        # 共享层
        x = Dense(128, activation='relu')(merged)
        x = Dense(64, activation='relu')(x)
        
        # 输出层
        output_layer = Dense(self.action_size, activation='linear')(x)
        
        model = Model(inputs=input_layer, outputs=output_layer)
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        
        return model
    
    def update_target_model(self):
        """硬更新目标网络"""
        self.target_model.set_weights(self.model.get_weights())
    
    def soft_update_target_model(self):
        """软更新目标网络"""
        model_weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        new_weights = []
        
        # 逐个处理每个权重张量
        for i in range(len(model_weights)):
            new_weights.append(self.tau * model_weights[i] + (1 - self.tau) * target_weights[i])
        
        self.target_model.set_weights(new_weights)
    
    def remember(self, state, action, reward, next_state, done):
        """记忆经验"""
        self.memory.add((state, action, reward, next_state, done))
    
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
        
        # 从优先经验回放缓冲区采样
        experiences, indices, weights = self.memory.sample(batch_size)
        
        states = np.array([exp[0] for exp in experiences])
        actions = np.array([exp[1] for exp in experiences])
        rewards = np.array([exp[2] for exp in experiences])
        next_states = np.array([exp[3] for exp in experiences])
        dones = np.array([exp[4] for exp in experiences])
        
        # Double DQN更新
        # 使用主网络选择动作
        next_actions = np.argmax(self.model.predict(next_states, verbose=0), axis=1)
        
        # 使用目标网络评估这些动作的价值
        next_q_values = self.target_model.predict(next_states, verbose=0)
        target_q_values = np.array([q_values[action] for q_values, action in zip(next_q_values, next_actions)])
        
        # 计算目标Q值
        targets = rewards + (1 - dones) * self.gamma * target_q_values
        
        # 获取当前Q值预测
        current_q = self.model.predict(states, verbose=0)
        
        # 计算TD误差
        td_errors = np.abs(targets - np.array([q[a] for q, a in zip(current_q, actions)]))
        
        # 更新优先级
        self.memory.update_priorities(indices, td_errors)
        
        # 更新Q值
        for i, action in enumerate(actions):
            current_q[i][action] = targets[i]
        
        # 使用重要性采样权重训练模型
        self.model.fit(states, current_q, sample_weight=weights, epochs=1, verbose=0)
        
        # 软更新目标网络
        self.soft_update_target_model()
        
        # 衰减探索率
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def load(self, name):
        """加载模型"""
        try:
            self.model.load_weights(name)
            self.target_model.load_weights(name)
            print(f"成功加载模型: {name}")
        except:
            print(f"无法加载模型: {name}")
    
    def save(self, name):
        """保存模型"""
        try:
            self.model.save_weights(name)
            print(f"成功保存模型: {name}")
        except Exception as e:
            print(f"保存模型时出错: {str(e)}")
            print("请确保已安装h5py包")

def train_agent(episodes=10000, batch_size=64, save_interval=500):
    """训练智能体"""
    env = BlackjackEnv()
    state_size = 29  # 玩家点数, 庄家明牌, 是否有可用A, 玩家手牌分布(13), 牌组分布(13)
    action_size = 2  # 停牌或要牌
    agent = DoubleDQNAgent(state_size, action_size)
    
    rewards = []
    win_rates = []
    avg_rewards = []
    
    print("开始训练，请稍候...")
    
    try:
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
                    break
            
            # 经验回放
            if len(agent.memory) > batch_size:
                agent.replay(batch_size)
            
            # 记录奖励
            total_reward = sum(episode_rewards)
            rewards.append(total_reward)
            
            # 计算平均奖励
            if e % 100 == 0:
                avg_reward = np.mean(rewards[-100:]) if len(rewards) >= 100 else np.mean(rewards)
                avg_rewards.append(avg_reward)
                print(f"Episode: {e+1}/{episodes}, Avg Reward: {avg_reward:.3f}, Epsilon: {agent.epsilon:.3f}")
            
            # 每save_interval轮保存模型
            if (e + 1) % save_interval == 0:
                agent.save(f"blackjack_ddqn_{e+1}.h5")
            
            # 每1000轮计算一次胜率
            if (e + 1) % 1000 == 0:
                win_rate = evaluate_agent(agent, 1000, verbose=False)
                win_rates.append(win_rate)
                print(f"训练进度: {e+1}/{episodes}, 胜率: {win_rate:.2%}, Epsilon: {agent.epsilon:.3f}")
        
        # 保存最终模型
        agent.save("blackjack_ddqn_final.h5")
        
        # 绘制奖励曲线
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        plt.plot(rewards)
        plt.title('每轮奖励')
        plt.xlabel('回合')
        plt.ylabel('奖励')
        
        plt.subplot(1, 3, 2)
        plt.plot(range(0, episodes, 100), avg_rewards)
        plt.title('平均奖励 (每100轮)')
        plt.xlabel('回合')
        plt.ylabel('平均奖励')
        
        plt.subplot(1, 3, 3)
        plt.plot(range(1000, episodes + 1, 1000), win_rates)
        plt.title('胜率曲线')
        plt.xlabel('回合')
        plt.ylabel('胜率')
        
        plt.tight_layout()
        plt.savefig('training_curves.png')
        plt.show()
        
    except KeyboardInterrupt:
        print("训练被用户中断")
        agent.save("blackjack_ddqn_interrupted.h5")
    
    return agent

def evaluate_agent(agent, num_games=10000, verbose=True):
    """评估智能体的表现"""
    env = BlackjackEnv()
    wins = 0
    losses = 0
    draws = 0
    
    for _ in range(num_games):
        state = env.reset()
        state = np.reshape(state, [1, 29])
        
        while True:
            action = agent.act(state[0], training=False)
            next_state, reward, done = env.step(action)
            state = np.reshape(next_state, [1, 29])
            
            if done:
                if reward > 0:
                    wins += 1
                elif reward < 0:
                    losses += 1
                else:
                    draws += 1
                break
    
    win_rate = wins / num_games
    loss_rate = losses / num_games
    draw_rate = draws / num_games
    net_score = wins - losses
    
    if verbose:
        print(f"评估结果 (共{num_games}局):")
        print(f"胜率: {win_rate:.2%}")
        print(f"负率: {loss_rate:.2%}")
        print(f"平局率: {draw_rate:.2%}")
        print(f"净得分: {net_score}")
    
    return win_rate

def simulate_games(agent, num_games=10000):
    """使用训练好的智能体模拟游戏"""
    env = BlackjackEnv()
    wins = 0
    losses = 0
    draws = 0
    
    print(f"开始模拟{num_games}局游戏...")
    
    for game in range(num_games):
        state = env.reset()
        state = np.reshape(state, [1, 29])
        done = False
        
        while not done:
            action = agent.act(state[0], training=False)
            next_state, reward, done = env.step(action)
            state = np.reshape(next_state, [1, 29])
        
        if reward > 0:
            wins += 1
        elif reward < 0:
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
    
    print(f"\n模拟结果 (共{num_games}局):")
    print(f"胜率: {win_rate:.2%}")
    print(f"负率: {loss_rate:.2%}")
    print(f"平局率: {draw_rate:.2%}")
    print(f"净得分: {net_score}")
    
    return net_score

def load_and_simulate(model_path, num_games=10000):
    """加载已训练的模型并模拟游戏"""
    state_size = 29
    action_size = 2
    agent = DoubleDQNAgent(state_size, action_size)
    agent.load(model_path)
    agent.epsilon = 0  # 设置为0，完全使用学习到的策略
    
    return simulate_games(agent, num_games)

def main():
    """主函数"""
    print("21点游戏强化学习")
    print("1. 训练新的智能体")
    print("2. 加载已有模型并模拟")
    
    choice = input("请选择模式 (1 或 2): ")
    
    if choice == '1':
        # 训练新的智能体
        episodes = int(input("请输入训练回合数 (建议10000-50000): ") or "10000")
        agent = train_agent(episodes=episodes)
        
        # 使用训练好的智能体模拟游戏
        simulate_games(agent, num_games=10000)
    else:
        # 加载已有模型并模拟
        model_path = input("请输入模型路径 (默认为blackjack_ddqn_final.h5): ") or "blackjack_ddqn_final.h5"
        num_games = int(input("请输入模拟游戏局数: ") or "10000")
        load_and_simulate(model_path, num_games)

if __name__ == "__main__":
    main()