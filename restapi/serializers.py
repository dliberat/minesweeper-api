from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from restapi.exceptions import InvalidMoveException, GameOverException
from restapi.models import Game, Move
from restapi.sweepergame import SweeperGame

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = [
            'id',
            'num_rows',
            'num_cols',
            'num_mines',
            'created_at',
        ]


class GameDetailSerializer(serializers.ModelSerializer):
    tiles = serializers.ListField(child=serializers.ListField(
        child=serializers.IntegerField(),
        read_only=True
    ), read_only=True)

    class Meta:
        model = Game
        fields = [
            'id',
            'num_rows',
            'num_cols',
            'num_mines',
            'created_at',
            'tiles',
        ]

class LatestStateMixin(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()

    def get_state(self, obj):
        """Replay the entire history of moves
        and build the latest game state"""

        move_history = Move.objects.filter(
            game_id=obj.game_id).order_by('order')

        game = SweeperGame.from_tile_arr(obj.game_id.tiles)

        try:
            for move in move_history:
                if move.action == 'R':
                    game = game.reveal_tile(move.row, move.col)
                elif move.action == 'F':
                    game = game.set_flag(move.row, move.col)
                else:
                    raise Exception('Invalid action')
        except InvalidMoveException:
            raise ValidationError('Invalid move')
        except GameOverException:
            raise ValidationError('Cannot apply move to completed game')

        return {
            'status': game.status.value,
            'tiles': game.tiles
        }


class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = [
            'id',
            'game_id',
            'order',
            'row',
            'col',
            'action'
        ]
        read_only_fields = ('order',)


class MoveDetailSerializer(LatestStateMixin):
    class Meta:
        model = Move
        fields = [
            'id',
            'game_id',
            'order',
            'row',
            'col',
            'action',
            'state',
        ]


class MoveCreateSerializer(LatestStateMixin):
    class Meta:
        model = Move
        fields = [
            'game_id',
            'row',
            'col',
            'action',
            'state',
        ]

