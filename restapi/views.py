import logging
from rest_framework import viewsets

from django.utils.timezone import now

from restapi.models import Game, Move
from restapi.serializers import GameSerializer, GameDetailSerializer, \
    MoveSerializer, MoveDetailSerializer, MoveCreateSerializer

from restapi.sweepergame import SweeperGame, GameStatus
from restapi.exceptions import InvalidMoveException, GameOverException

logger = logging.getLogger('sweeper')

class GameViewSet(viewsets.ModelViewSet):
    serializer_class = GameSerializer
    detail_serializer_class = GameDetailSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            if hasattr(self, 'detail_serializer_class'):
                return self.detail_serializer_class

        return super(GameViewSet, self).get_serializer_class()


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Game.objects.filter(owner=self.request.user)


class MoveViewSet(viewsets.ModelViewSet):
    serializer_class = MoveSerializer
    detail_serializer_class = MoveDetailSerializer
    create_serializer_class = MoveCreateSerializer
    filterset_fields = ['game_id']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            if hasattr(self, 'detail_serializer_class'):
                return self.detail_serializer_class
        elif self.action == 'create':
            if hasattr(self, 'create_serializer_class'):
                return self.create_serializer_class

        return super(MoveViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        """
        Side Effects:
            Updates Game model's `end_time` field if the
            move results in the game being finished.
        """

        try:
            game_id = int(self.request.data['game_id'])
            row = int(self.request.data['row'])
            col = int(self.request.data['row'])
            action = self.request.data['action']
        except ValueError:
            raise ValidationError('Missing required field.')

        logger.debug('gid=%d, r=%d, c=%d, a=%s', game_id, row, col, action)

        try:
            game_obj = Game.objects.get(pk=game_id)
        except Exception:
            raise ValidationError('Specified game_id does not exist.')

        logger.debug('got game objejct')

        move_history = Move.objects.filter(
            game_id=game_obj
        ).order_by('order')

        game = SweeperGame.from_tile_arr(game_obj.tiles)

        try:
            for move in move_history:

                if move.action == 'R':
                    game = game.reveal_tile(move.row, move.col)
                elif move.action == 'F':
                    game = game.set_flag(move.row, move.col)
                else:
                    # this should never logically happen.
                    # Therefore, if it does, we return 500.
                    logger.exception('Unexpected move action: %s', move.action)
                    raise Exception('Invalid action')

            # after all previous moves have been applied,
            # we try applying the new one that was provided in the request
            if action == 'R':
                game = game.reveal_tile(row, col)
            elif action == 'F':
                game = game.set_flag(row, col)
            else:
                raise ValidationError('Invalid action')

        except InvalidMoveException:
            raise ValidationError('Invalid move')
        except GameOverException:
            raise ValidationError('Cannot apply move to completed game')

        if game_obj.end_time is None and \
            game.status != GameStatus.IN_PROGRESS:
            logger.debug('Game is over. Updating end_time on model.')
            game_obj.end_time = now()
            game_obj.save()

        r, c = self.request.data['row'], self.request.data['col']
        logger.debug('saving move %d, %d', r, c)
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Move.objects.filter(owner=self.request.user)
