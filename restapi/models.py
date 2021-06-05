import logging

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.utils.timezone import now

from restapi import const
from restapi.sweepergame import SweeperGame

logger = logging.getLogger('sweeper')

class Game(models.Model):
    class Meta:
        ordering = ['-created_at']

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Time at which the user made the first move.'
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Time at which the game was completed.'
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


class Move(models.Model):
    class Meta:
        unique_together = ('game_id', 'order')
        ordering = ['game_id', 'order']

    REVEAL = 'R'
    FLAG = 'F'
    ACTION_CHOICES = [
        (REVEAL, 'Reveal'),
        (FLAG, 'Flag'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game_id = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField(
        help_text='Sequence ordering for a specific game'
    )
    row = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(const.MAX_ROWS-1)]
    )
    col = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(const.MAX_COLS-1)]
    )
    action = models.CharField(
        max_length=1,
        choices=ACTION_CHOICES,
        default=REVEAL,
        help_text='Action being performed. "R" to reveal a tile, "F" to flag it.'
    )

    def __str__(self):
        return f'[Move (id={self.id},game_id={self.game_id},order={self.order})]'

    def save(self, *args, **kwargs):
        if not self.id:
            # auto-increment the order field separately for each game_id
            logger.debug('Creating new move')

            agg = Move.objects.filter(
                game_id=self.game_id
                ).aggregate(models.Max('order'))

            if agg['order__max'] is not None:
                self.order = agg['order__max'] + 1
            else:
                # this is the first move in the game
                self.order = 0
                self.game_id.start_time = now()
                self.game_id.save()

        super(Move, self).save(*args, **kwargs)
