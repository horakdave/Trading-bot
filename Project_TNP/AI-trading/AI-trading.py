import gym
from gym import spaces
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class StockTradingEnv(gym.Env):
    def __init__(self, stock_symbol, initial_balance=10000):
        super(StockTradingEnv, self).__init__()
        
        self.stock_symbol = stock_symbol
        self.initial_balance = initial_balance  
        self.balance = initial_balance
        self.shares_held = 0
        self.current_step = 0
        
        # Get stock data
        self.stock_data = self._get_stock_data()
        
        # Define action space (0: hold, 1: buy, 2: sell)
        self.action_space = spaces.Discrete(3)
        
        # Define observation space (price, balance, shares_held)
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0]),
            high=np.array([np.inf, np.inf, np.inf]),
            dtype=np.float32
        )

    def _get_stock_data(self):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        df = yf.download(self.stock_symbol, start=start_date, end=end_date)
        return df['Close'].values

    def reset(self):
        self.balance = self.initial_balance
        self.shares_held = 0
        self.current_step = 0
        return self._get_observation()

    def _get_observation(self):
        return np.array([
            self.stock_data[self.current_step],
            self.balance,
            self.shares_held
        ])

    def step(self, action):
        current_price = self.stock_data[self.current_step]
        
        # Execute action
        if action == 1:  # Buy
            shares_to_buy = self.balance // current_price
            self.shares_held += shares_to_buy
            self.balance -= shares_to_buy * current_price
        
        elif action == 2:  # Sell
            self.balance += self.shares_held * current_price
            self.shares_held = 0

        # Move to next step
        self.current_step += 1
        
        # Calculate reward (change in portfolio value)
        new_portfolio_value = self.balance + (self.shares_held * current_price)
        reward = new_portfolio_value - self.initial_balance
        
        # Check if episode is done
        done = self.current_step >= len(self.stock_data) - 1
        
        return self._get_observation(), reward, done, {}

# Example usage with a simple random agent
def main():
    env = StockTradingEnv("AAPL")  # Use Apple stock as an example
    episodes = 5

    for episode in range(episodes):
        state = env.reset()
        done = False
        total_reward = 0

        while not done:
            action = env.action_space.sample()  # Random action
            next_state, reward, done, _ = env.step(action)
            total_reward += reward

        print(f"Episode: {episode + 1}, Total Reward: {total_reward}")

if __name__ == "__main__":
    main()