from rest_framework import serializers

from .models import Game

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
