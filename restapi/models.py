from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Game(models.Model):
    num_rows = models.IntegerField(
        validators=[MinValueValidator(6), MaxValueValidator(20)],
    )
    num_cols = models.IntegerField(
        validators=[MinValueValidator(6), MaxValueValidator(20)],
    )
    num_mines = models.IntegerField(
        validators=[MinValueValidator(2)]
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f'[Game (r={self.num_rows},c={self.num_cols},m={self.num_mines})'

    class Meta:
        ordering = ['-created_at']
