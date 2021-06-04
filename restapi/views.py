from rest_framework import viewsets

from .models import Game
from .serializers import GameSerializer, GameDetailSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    detail_serializer_class = GameDetailSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            if hasattr(self, 'detail_serializer_class'):
                return self.detail_serializer_class

        return super(GameViewSet, self).get_serializer_class()
