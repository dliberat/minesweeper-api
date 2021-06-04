from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField

from restapi import const
from restapi.sweepergame import SweeperGame

class Game(models.Model):
    class Meta:
        ordering = ['-created_at']

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
        editable=False,
    )
    tiles = ArrayField(
        ArrayField(models.IntegerField())
    )

    def __str__(self):
        return f'[Game (r={self.num_rows},c={self.num_cols},m={self.num_mines})'

    def save(self, *args, **kwargs):
        if not self.id:
            game = SweeperGame(
                self.num_rows,
                self.num_cols,
                self.num_mines,
            )
            self.tiles = game.tiles
        super(Game, self).save(*args, **kwargs)
