from django.http import Http404
from rest_framework import generics

from models import models
from api_v1 import serializers


class LeagueList(generics.ListCreateAPIView):
    queryset = models.League.objects.all()
    serializer_class = serializers.LeagueSerializer
    filter_fields = ('name',)


class LeagueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.League.objects.all()
    serializer_class = serializers.LeagueSerializer


class TeamView:
    def get_queryset(self):
        league_id = self.kwargs['league_id']
        try:
            league = models.League.objects.get(pk=league_id)
        except models.League.DoesNotExist:
            raise Http404
        return models.Team.objects.filter(league=league)


class TeamList(TeamView, generics.ListCreateAPIView):
    serializer_class = serializers.TeamSerializer
    filter_fields = ('name', 'alternative_names__name')

    def create(self, request, *args, **kwargs):
        request.data['league'] = kwargs['league_id']
        return super(TeamList, self).create(request, *args, **kwargs)


class TeamDetail(TeamView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.TeamSerializer

    def update(self, request, *args, **kwargs):
        request.data['league'] = kwargs['league_id']
        return super(TeamDetail, self).update(request, *args, **kwargs)


class TeamAlternativeNameView:
    def get_queryset(self):
        league_id = self.kwargs['league_id']
        team_id = self.kwargs['team_id']
        try:
            league = models.League.objects.get(pk=league_id)
        except models.League.DoesNotExist:
            raise Http404
        try:
            team = models.Team.objects.get(pk=team_id, league=league)
        except models.Team.DoesNotExist:
            raise Http404
        return models.TeamAlternativeName.objects.filter(team=team)


class TeamAlternativeNameList(TeamAlternativeNameView,
                              generics.ListCreateAPIView):
    serializer_class = serializers.TeamAlternativeNameSerializer
    filter_fields = ('name',)

    def create(self, request, *args, **kwargs):
        request.data['team'] = kwargs['team_id']
        return super(TeamAlternativeNameList, self).create(request,
                                                            *args,
                                                            **kwargs)


class TeamAlternativeNameDetail(TeamAlternativeNameView,
                                generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.TeamAlternativeNameSerializer

    def update(self, request, *args, **kwargs):
        request.data['team'] = kwargs['team_id']
        return super(TeamAlternativeNameDetail, self).update(request,
                                                              *args,
                                                              **kwargs)


class SeasonView:
    def get_queryset(self):
        league_id = self.kwargs['league_id']
        try:
            league = models.League.objects.get(pk=league_id)
        except models.League.DoesNotExist:
            raise Http404
        return models.Season.objects.filter(league=league)


class SeasonList(SeasonView, generics.ListCreateAPIView):
    serializer_class = serializers.SeasonSerializer
    filter_fields = ('name',)

    def create(self, request, *args, **kwargs):
        request.data['league'] = kwargs['league_id']
        return super(SeasonList, self).create(request, *args, **kwargs)


class SeasonDetail(SeasonView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.SeasonSerializer

    def update(self, request, *args, **kwargs):
        request.data['league'] = kwargs['league_id']
        return super(SeasonDetail, self).update(request, *args, **kwargs)


class GameView:
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


class GameList(GameView, generics.ListCreateAPIView):
    serializer_class = serializers.GameSerializer
    ordering = ('start',)
    filter_fields = ('team_1', 'team_2')

    def create(self, request, *args, **kwargs):
        request.data['season'] = kwargs['season_id']
        return super(GameList, self).create(request, *args, **kwargs)


class GameDetail(GameView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.GameSerializer

    def update(self, request, *args, **kwargs):
        request.data['league'] = kwargs['league_id']
        request.data['season'] = kwargs['season_id']
        return super(GameDetail, self).update(request, *args, **kwargs)


class VenueList(generics.ListCreateAPIView):
    queryset = models.Venue.objects.all()
    serializer_class = serializers.VenueSerializer
    filter_fields = ('name', 'alternative_names__name',)


class VenueDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Venue.objects.all()
    serializer_class = serializers.VenueSerializer


class VenueAlternativeNameView:
    def get_queryset(self):
        venue_id = self.kwargs['venue_id']
        try:
            venue = models.Venue.objects.get(pk=venue_id)
        except models.Venue.DoesNotExist:
            raise Http404
        return models.VenueAlternativeName.objects.filter(venue=venue)


class VenueAlternativeNameList(VenueAlternativeNameView,
                               generics.ListCreateAPIView):
    serializer_class = serializers.VenueAlternativeNameSerializer
    filter_fields = ('name',)

    def create(self, request, *args, **kwargs):
        request.data['venue'] = kwargs['venue_id']
        return super(VenueAlternativeNameList, self).create(request,
                                                            *args,
                                                            **kwargs)


class VenueAlternativeNameDetail(VenueAlternativeNameView,
                                 generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.VenueAlternativeNameSerializer

    def update(self, request, *args, **kwargs):
        request.data['venue'] = kwargs['venue_id']
        return super(VenueAlternativeNameDetail, self).update(request,
                                                              *args,
                                                              **kwargs)
