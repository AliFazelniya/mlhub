# Django RL Tic-Tac-Toe

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Django](https://img.shields.io/badge/django-4.2%2B-green)

A modern, robust web application serving a 5x5 Reinforcement Learning Tic-Tac-Toe agent. 
The backend exposes a REST API powered by a Deep Q-Network (DQN) model trained using Stable-Baselines3, while the frontend provides a sleek, interactive browser-based UI.

## 🚀 Features
- **Client-Server Architecture**: Separation of concerns with a Django API backend and a Vanilla JS frontend.
- **Deep Reinforcement Learning**: AI gameplay driven by a highly optimized, pre-trained Stable-Baselines3 model.
- **Efficient Inference**: The model utilizes a Singleton loading pattern inside Django to load only once into memory, guaranteeing ultra-fast response times.
- **Modern UI**: Dark-themed responsive 5x5 CSS Grid interface.

## 📂 Architecture Overview

- `core/` — Django project settings, WSGI, and global routing.
- `game/` — The primary app. Contains the API endpoints, RL game logic (`board.py`), and the DQN model payload.
- `templates/` — HTML rendering templates.
- `static/` — Frontend CSS styles and JavaScript logic.

## 🛠 Installation & Setup

1. **Clone the repository** (or navigate to the directory):
   ```bash
   cd tictactoe
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Database Migrations** (if applicable):
   ```bash
   python manage.py migrate
   ```

5. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```

6. **Play**: Open your browser and navigate to `http://127.0.0.1:8000/`.

## 🧠 Model Specifications
- **Framework**: Stable-Baselines3 (DQN)
- **State Space**: 5x5 grid (Represented as 1.0 for AI, -1.0 for Human, 0.0 for Empty)
- **Action Space**: Discrete (0-24)

## 📄 License
This project is licensed under the MIT License.
