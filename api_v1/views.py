from django.http import Http404
from rest_framework import generics

from models import models
from api_v1 import serializers

class LeagueList(generics.ListCreateAPIView):
    queryset = models.League.objects.all()
    serializer_class = serializers.LeagueSerializer
    filter_fields = ('name',)

class LeagueDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    queryset = models.League.objects.all()
    serializer_class = serializers.LeagueSerializer

class TeamList(generics.ListCreateAPIView):
    serializer_class = serializers.TeamSerializer
    filter_fields = ('name',)

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
    filter_fields = ('name',)

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

class GameList(generics.ListCreateAPIView):
    serializer_class = serializers.GameSerializer

    def get_queryset(self):
        league_id = self.kwargs['league_id']
        season_id = self.kwargs['season_id']
        try:
            season = models.Season.objects.get(pk=season_id)
        except models.Season.DoesNotExist:
            raise Http404
        return models.Game.objects.filter(season=season)

    def create(self, request, *args, **kwargs):
        request.data['season'] = kwargs['season_id']
        return super(GameList, self).create(request, *args, **kwargs)

class GameDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = serializers.GameSerializer

    def get_queryset(self):
        league_id = self.kwargs['league_id']
        season_id = self.kwargs['season_id']
        try:
            league = models.League.objects.get(pk=league_id)
        except models.League.DoesNotExist:
            raise Http404
        try:
            season = models.Season.objects.get(pk=season_id, league=league)
        except models.Season.DoesNotExist:
            raise Http404
        return models.Game.objects.filter(season=season)

    def update(self, request, *args, **kwargs):
        request.data['league'] = kwargs['league_id']
        request.data['season'] = kwargs['season_id']
        return super(GameDetail, self).update(request, *args, **kwargs)

class VenueList(generics.ListCreateAPIView):
    queryset = models.Venue.objects.all()
    serializer_class = serializers.VenueSerializer
    filter_fields = ('name', 'alternative_names__name',)

class VenueDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    queryset = models.Venue.objects.all()
    serializer_class = serializers.VenueSerializer

class VenueAlternativeNameList(generics.ListCreateAPIView):
    serializer_class = serializers.VenueAlternativeNameSerializer
    filter_fields = ('name',)

    def get_queryset(self):
        venue_id = self.kwargs['venue_id']
        try:
            venue = models.Venue.objects.get(pk=venue_id)
        except models.Venue.DoesNotExist:
            raise Http404
        return models.VenueAlternativeName.objects.filter(venue=venue)

    def create(self, request, *args, **kwargs):
        request.data['venue'] = kwargs['venue_id']
        return super(VenueAlternativeNameList, self).create(request,
                                                            *args,
                                                            **kwargs)

class VenueAlternativeNameDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = serializers.VenueAlternativeNameSerializer

    def get_queryset(self):
        venue_id = self.kwargs['venue_id']
        try:
            venue = models.Venue.objects.get(pk=venue_id)
        except models.Venue.DoesNotExist:
            raise Http404
        return models.VenueAlternativeName.objects.filter(venue=venue)

    def update(self, request, *args, **kwargs):
        request.data['venue'] = kwargs['venue_id']
        return super(VenueAlternativeNameDetail, self).update(request,
                                                              *args,
                                                              **kwargs)
