import numpy as np
from rl_env import DoozEnv
from rl_agent import DQNAgent
import torch

def train_agent(episodes=1000, board_size=5):
    env = DoozEnv(board_size=board_size)
    agent = DQNAgent(board_size=board_size)
    
    print(f"Starting agent training on a {board_size}x{board_size} board for {episodes} episodes...")
    
    for e in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            legal_moves_2d = env.board.get_legal_moves()
            legal_actions = [r * board_size + c for (r, c) in legal_moves_2d]

            action = agent.act(state, legal_actions)
            
            next_state, reward, done, _, _ = env.step(action)
            total_reward += reward
            
            agent.remember(state, action, reward, next_state, done)
            agent.replay()
            
            state = next_state
        if e % 10 == 0:
            agent.update_target_model()
            
        if (e + 1) % 50 == 0:
            print(f"Episode: {e+1}/{episodes} | Total Reward: {total_reward:.2f} | Epsilon: {agent.epsilon:.3f}")
            
    torch.save(agent.model.state_dict(), f"dooz_dqn_{board_size}x{board_size}.pth")
    print("Training complete and model saved!")

if __name__ == "__main__":
    train_agent(episodes=500, board_size=10)