from django.db import models


class MatchHistory(models.Model):
    RESULT_CHOICES = [
        ('WIN', 'Win'),
        ('LOSS', 'Loss'),
        ('TIE', 'Tie'),
    ]
    MARK_CHOICES = [
        ('X', 'X'),
        ('O', 'O'),
    ]
    ENGINE_CHOICES = [
        ('rl', 'RL Agent (DQN)'),
        ('minimax', 'Minimax AI'),
    ]

    board_size = models.IntegerField()
    human_mark = models.CharField(max_length=1, choices=MARK_CHOICES)
    ai_engine = models.CharField(max_length=10, choices=ENGINE_CHOICES)
    human_score = models.IntegerField(default=0)
    ai_score = models.IntegerField(default=0)
    result = models.CharField(max_length=4, choices=RESULT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name_plural = 'Match histories'

    def __str__(self):
        return (
            f"[{self.board_size}x{self.board_size}] {self.result} "
            f"{self.human_score}-{self.ai_score} ({self.ai_engine})"
        )
