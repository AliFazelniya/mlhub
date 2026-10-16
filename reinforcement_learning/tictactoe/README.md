# AI-Powered Multi-Grid Tic-Tac-Toe Web App

**Django + Deep Reinforcement Learning (Stable-Baselines3 DQN) & Alpha-Beta Minimax**

A modern, responsive, production-ready web application that migrates a local
Pygame desktop game into a full Django project backed by SQLite. Players compete
against either a trained Deep Q-Network agent or a classical Alpha-Beta pruning
engine across board sizes from 3×3 to 10×10.

---

## Unique Game Mechanics & Scoring Formula

### Full-board completion rule

Unlike classic tic-tac-toe, the game **does not end on the first 3-in-a-row**.
Play continues until the entire grid is full (`board.is_full()`), so every match
is a strategic race for the highest total score rather than a single win line.

### Run-scoring formula

After every move, `Board.calculate_scores()` scans all cached row, column, and
diagonal coordinates (`_line_coords`). For every **consecutive run of `n ≥ 3`**
identical marks it awards:

```
score = (n - 2) + (n - 3) * (n - 3)
       = (n - 2) + (n - 3)²
```

So a run of 3 scores 1 point, a run of 4 scores 3, a run of 5 scores 6, and
longer runs grow quadratically — rewarding long, connected chains dramatically.

The winner is the side with the higher total score when the board is full.

---

## AI Architecture

### 1. Deep Q-Network (`RL Agent (DQN)`)

- **Library:** Stable-Baselines3 `DQN` with an `MlpPolicy` over a
  `Box(-1, 1, shape=(N, N))` observation (AI = `1.0`, human = `-1.0`, empty = `0.0`).
- **Action space:** `Discrete(N²)`; the 1-D action is decoded to
  `row = action // N`, `col = action % N`.
- **Curriculum learning:** Models are trained independently per board size
  (`dqn_model_3x3.zip`, `dqn_model_4x4.zip`, `dqn_model_5x5.zip`), starting at
  small boards and scaling up.
- **Self-play training:** `train_selfplay.py` promotes the learning agent into
  its own sparring partner each generation, closing the skill loop against
  increasingly strong versions of itself.
- **Robust inference:** If the network proposes an illegal cell, the agent falls
  back to Minimax and then to a random legal move so the game never crashes.

### 2. Alpha-Beta Minimax (`Minimax AI`)

- `MinimaxAI` uses **Alpha-Beta pruning** with **dynamic depth scaling**
  (`_calculate_dynamic_depth`: depth 6 for ≤4×4, 5 for ≤6×6, 4 for larger) and
  **heuristic move ordering** (`_get_smart_moves_from_legal`) based on adjacency
  density and distance to the board centre.
- It is the universal fallback: any board size without a trained DQN model is
  served by Minimax automatically.

---

## Web Architecture & Features

- **Singleton in-memory model loading:** A `ModelRegistry` singleton loads every
  available DQN `.zip` **once at server startup** inside `GameConfig.ready()`
  (`game/apps.py`). HTTP requests never load a model from disk — inference reuses
  the in-RAM instances.
- **REST API endpoints:**
  - `GET /` — single-page game interface.
  - `POST /api/move/` — validates the human move, computes the AI reply, returns
    the updated grid, scores, engine used, and game-over state. On the final
    move it persists a `MatchHistory` row.
  - `GET /api/history/` — aggregate statistics (total games, wins, losses, ties,
    win rate) plus the 10 most recent matches.
  - `POST /api/history/clear/` — resets match history.
- **SQLite Match History:** Every finished match is stored in `db.sqlite3` via the
  `MatchHistory` model, with a clean Django admin list/filter view.
- **Catppuccin Mocha frontend:** A responsive HTML5/CSS3/Vanilla-JS single-page UI
  reproducing the exact palette from the original `gui.py`, with animated SVG
  marks, coordinate headers, AI-move highlighting, a live scoreboard, a match
  history dashboard, and an animated game-over modal.

---

## Project Structure

```
tictactoe/
├── config/                     # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── game/                       # Main application
│   ├── apps.py                 # GameConfig.ready() → model registry bootstrap
│   ├── ai_manager.py           # Engine selection + RL/Minimax fallback
│   ├── admin.py                # MatchHistory admin
│   ├── models.py               # MatchHistory model
│   ├── views.py                # Page + REST API views
│   ├── urls.py
│   ├── engine/                 # Pure-Python game core
│   │   ├── board.py            # Board + run-scoring
│   │   └── minmax.py           # MinimaxAI (Alpha-Beta)
│   ├── models_rl/              # RL integration
│   │   ├── registry.py         # Singleton in-memory DQN registry
│   │   ├── rl_agent.py         # RLAgent inference wrapper
│   │   └── dqn_model_3x3.zip   # Trained DQN models
│   │       dqn_model_4x4.zip
│   │       dqn_model_5x5.zip
│   ├── templates/game/index.html
│   └── static/game/
│       ├── css/style.css
│       └── js/app.js
├── backup/                     # Archived legacy Pygame & training scripts
│   ├── main.py
│   ├── gui.py
│   ├── rl_env.py
│   ├── train.py
│   └── train_selfplay.py
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

---

## Setup & Usage Guide

All commands must run inside the existing **`ml`** virtual environment
(`~/.venvs/ml/bin/python`), which already provides PyTorch,
Stable-Baselines3, Gymnasium, and NumPy.

```bash

# 1. (If Django is missing) install it into that same environment
pip install -r requirements.txt

# 2. Apply database migrations
python manage.py makemigrations
python manage.py migrate

# 3. Start the development server
python manage.py runserver
# → open http://127.0.0.1:8000/
```

### Retraining models

The training scripts are preserved in `backup/`:

```bash
cd backup
python train.py --board_size 5          # train a fresh DQN for a board size
python train_selfplay.py --board_size 5 # continue with self-play generations
```

Copy the resulting `dqn_model_<N>x<N>.zip` into `game/models_rl/` to make it
available to the web app (it will be picked up on the next server start).

### Admin

Create a superuser and inspect stored matches at `/admin/`:

```bash
python manage.py createsuperuser
```
