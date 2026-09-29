import os
import random
import numpy as np
import argparse
from stable_baselines3 import DQN
from rl_env import TicEnv

class RLSparringPartner:
    def __init__(self, model, board_size, ai_mark='X', human_mark='O'):
        self.model = model
        self.board_size = board_size
        self.ai = ai_mark
        self.human = human_mark

    def get_best_move(self, board):
        legal_moves = board.get_legal_moves()
        if not legal_moves:
            return None
            
        state = np.zeros((self.board_size, self.board_size), dtype=np.float32)
        for r in range(self.board_size):
            for c in range(self.board_size):
                if board.grid[r][c] == self.ai:
                    state[r, c] = 1.0
                elif board.grid[r][c] == self.human:
                    state[r, c] = -1.0
                    
        action, _ = self.model.predict(state, deterministic=True)
        row = action.item() // self.board_size
        col = action.item() % self.board_size

        if (row, col) not in legal_moves:
            return random.choice(legal_moves)
        return (row, col)

def train_self_play(board_size=5, generations=5, steps_per_gen=50000):
    print(f"Starting self-play matches on a {board_size}x{board_size} board...")
    
    env = TicEnv(board_size=board_size)
    model_path = f"dqn_model_{board_size}x{board_size}.zip"
    
    if os.path.exists(model_path):
        print("[+] Previous model found. The agent is ready to fight its own clones!")
        model = DQN.load(model_path, env=env)
    else:
        print("[-] Model not found. Please run train.py first.")
        return
    
    for gen in range(generations):
        print(f"\n--- Starting generation {gen + 1} of {generations} ---")
        
        if gen > 0:
            print(">> Upgrading opponent's brain to the latest learned version...")
            clone_opponent = RLSparringPartner(model, board_size, ai_mark='X', human_mark='O')
            env.sparring_partner = clone_opponent
            
        model.learn(total_timesteps=steps_per_gen, reset_num_timesteps=False, log_interval=1000)

        model.save(f"dqn_model_{board_size}x{board_size}")
        
    print("\nSelf-play training completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Self-Play Training")
    parser.add_argument("-s", "--board_size", type=int, default=5)
    args = parser.parse_args()

    if 3 <= args.board_size <= 10:
        train_self_play(board_size=args.board_size)