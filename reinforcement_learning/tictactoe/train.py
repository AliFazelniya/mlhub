from stable_baselines3 import DQN
from rl_env import TicEnv
import argparse

def train_agent(board_size=3, total_steps=150000):
    print(f"Starting training on a {board_size}x{board_size} board...")
    
    env = TicEnv(board_size=board_size)
    
    model = DQN(
        "MlpPolicy", 
        env, 
        verbose=1, 
        learning_rate=1e-3, 
        buffer_size=100000, 
        learning_starts=1000, 
        batch_size=64, 
        tau=1.0, 
        gamma=0.99, 
        train_freq=4, 
        gradient_steps=1,
        exploration_fraction=0.5, 
        exploration_initial_eps=1.0, 
        exploration_final_eps=0.01
    )
    
    model.learn(total_timesteps=total_steps, log_interval=100)
    
    model.save(f"dqn_model_{board_size}x{board_size}")
    print("The model was successfully saved!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train RL Model for a particular board size")
    parser.add_argument("-s", "--board_size", type=int, default=3, help="Particular board size (3 to 10)")
    args = parser.parse_args()

    if 3 <= args.board_size <= 10:
        train_agent(board_size=args.board_size)
    else:
        print("Error: The board size is not valid. It must be between 3 and 10.")
    