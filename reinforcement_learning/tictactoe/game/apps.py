import os
import warnings

from django.apps import AppConfig


class GameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'game'

    def ready(self):
        # Suppress low-level logs (TensorFlow / oneDNN / warnings) at startup.
        os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')
        os.environ.setdefault('TF_ENABLE_ONEDNN_OPTS', '0')
        warnings.filterwarnings("ignore")

        # Memory optimization: load every available DQN model into RAM once.
        try:
            from game.models_rl.registry import registry
            registry.load_all()
        except Exception as exc:  # pragma: no cover - defensive
            import logging
            logging.getLogger(__name__).error(
                "RL model registry initialization failed: %s", exc
            )
