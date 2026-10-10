# Django RL Tic-Tac-Toe

A modern, robust Django-based web application serving a 5x5 Reinforcement Learning Tic-Tac-Toe agent. 
The AI is powered by a DQN model trained with Stable-Baselines3.

## Project Structure

- `core/`: Django project settings and configurations.
- `game/`: The main Django app containing the backend API, game logic (`board.py`), and the pre-trained RL model.
- `templates/`: HTML templates for the frontend UI.
- `static/`: CSS and JavaScript files.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install django stable-baselines3[extra] numpy shimmy
   ```
3. Run the server:
   ```bash
   python manage.py runserver
   ```
