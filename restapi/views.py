from rest_framework import viewsets

from .models import Game, Move
from .serializers import GameSerializer, GameDetailSerializer, \
    MoveSerializer, MoveDetailSerializer, MoveCreateSerializer

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
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Move.objects.filter(owner=self.request.user)
