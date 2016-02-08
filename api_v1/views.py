from rest_framework import generics

from models import models
from api_v1 import serializers

class LeagueList(generics.ListCreateAPIView):
    queryset = models.League.objects.all()
    serializer_class = serializers.LeagueSerializer

class LeagueDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    queryset = models.League.objects.all()
    serializer_class = serializers.LeagueSerializer

class TeamList(generics.ListCreateAPIView):
    serializer_class = serializers.TeamSerializer

    def get_queryset(self):
        league_id = self.kwargs['league_id']
        return models.Team.objects.filter(league__id=league_id)

class TeamDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_fields = ('league_id', 'team_id')
    queryset = models.Team.objects.all()
    serializer_class = serializers.TeamSerializer
