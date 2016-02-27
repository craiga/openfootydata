from django.http import Http404
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
        try:
            league = models.League.objects.get(pk=league_id)
        except models.League.DoesNotExist:
            raise Http404
        return models.Team.objects.filter(league=league)

    def create(self, request, *args, **kwargs):
        request.data['league'] = kwargs['league_id']
        return super(TeamList, self).create(request, *args, **kwargs)

class TeamDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = serializers.TeamSerializer

    def get_queryset(self):
        league_id = self.kwargs['league_id']
        try:
            league = models.League.objects.get(pk=league_id)
        except models.League.DoesNotExist:
            raise Http404
        return models.Team.objects.filter(league=league)

    def update(self, request, *args, **kwargs):
        request.data['league'] = kwargs['league_id']
        return super(TeamDetail, self).update(request, *args, **kwargs)

class SeasonList(generics.ListCreateAPIView):
    serializer_class = serializers.SeasonSerializer

    def get_queryset(self):
        league_id = self.kwargs['league_id']
        try:
            league = models.League.objects.get(pk=league_id)
        except models.League.DoesNotExist:
            raise Http404
        return models.Season.objects.filter(league=league)

    def create(self, request, *args, **kwargs):
        request.data['league'] = kwargs['league_id']
        return super(SeasonList, self).create(request, *args, **kwargs)

class SeasonDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = serializers.SeasonSerializer

    def get_queryset(self):
        league_id = self.kwargs['league_id']
        try:
            league = models.League.objects.get(pk=league_id)
        except models.League.DoesNotExist:
            raise Http404
        return models.Season.objects.filter(league=league)

    def update(self, request, *args, **kwargs):
        request.data['league'] = kwargs['league_id']
        return super(SeasonDetail, self).update(request, *args, **kwargs)