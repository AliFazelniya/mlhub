"""In-memory registry (Singleton) for trained Stable-Baselines3 DQN models.

Models are loaded **once** at server startup via ``GameConfig.ready()`` and kept
in RAM. HTTP requests must never trigger a ``DQN.load(...)`` call.
"""

import os
import logging

logger = logging.getLogger(__name__)

_SUPPORTED_SIZES = (3, 4, 5)


class ModelRegistry:
    """Lazily-instantiated process-wide singleton holding loaded DQN models."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._models = {}
        self._load_attempted = False

    # -- lifecycle ---------------------------------------------------------
    def load_all(self) -> None:
        """Load every available ``dqn_model_<N>x<N>.zip`` exactly once."""
        if self._load_attempted:
            return
        self._load_attempted = True

        base_dir = os.path.dirname(os.path.abspath(__file__))

        for size in _SUPPORTED_SIZES:
            filename = f"dqn_model_{size}x{size}.zip"
            path = os.path.join(base_dir, filename)
            if not os.path.exists(path):
                logger.warning("RL model missing, skipping: %s", path)
                continue
            try:
                from stable_baselines3 import DQN
                self._models[size] = DQN.load(path)
                logger.info("Loaded RL model %s", filename)
            except Exception as exc:  # pragma: no cover - defensive
                logger.error("Failed to load %s: %s", filename, exc)

    # -- access ------------------------------------------------------------
    def get(self, board_size: int):
        """Return the loaded DQN model for ``board_size`` or ``None``."""
        return self._models.get(board_size)

    def has(self, board_size: int) -> bool:
        return board_size in self._models

    @property
    def available_sizes(self):
        return sorted(self._models.keys())


registry = ModelRegistry()
