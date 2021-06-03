from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from restapi import const

class Game(models.Model):
    num_rows = models.IntegerField(
        validators=[MinValueValidator(const.MIN_ROWS), MaxValueValidator(const.MAX_ROWS)],
    )
    num_cols = models.IntegerField(
        validators=[MinValueValidator(const.MIN_COLS), MaxValueValidator(const.MAX_COLS)],
    )
    num_mines = models.IntegerField(
        validators=[MinValueValidator(const.MIN_MINES)]
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f'[Game (r={self.num_rows},c={self.num_cols},m={self.num_mines})'

    class Meta:
        ordering = ['-created_at']
