from rest_framework.serializers import (HyperlinkedIdentityField,
                                        HyperlinkedRelatedField,
                                        ModelSerializer,
                                        IntegerField)

from models import models

class LeagueSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(
        view_name='api_v1:league_detail',
        lookup_field='id'
    )
    seasons = HyperlinkedIdentityField(
        view_name='api_v1:season_list',
        lookup_field='id',
        lookup_url_kwarg='league_id'
    )
    class Meta:
        model = models.League

class LeagueRelatedHyperlinkedIdentityField(HyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        return self.reverse(view_name,
                            kwargs={self.lookup_url_kwarg: obj.id,
                                    'league_id': obj.league.id},
                            request=request,
                            format=format)

class SeasonRelatedHyperlinkedIdentityField(HyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        return self.reverse(view_name,
                            kwargs={self.lookup_url_kwarg: obj.id,
                                    'season_id': obj.season.id,
                                    'league_id': obj.season.league.id},
                            request=request,
                            format=format)

class TeamSerializer(ModelSerializer):
    url = LeagueRelatedHyperlinkedIdentityField(
        view_name='api_v1:team_detail',
        lookup_url_kwarg='id'
    )
    class Meta:
        model = models.Team

class TeamHyperlink(HyperlinkedRelatedField):
    view_name = 'api_v1:team_detail'
    queryset = models.Team.objects.all()

    def get_url(self, obj, view_name, request, format):
        return self.reverse(view_name,
                            kwargs={'id': obj.id, 'league_id': obj.league.id},
                            request=request,
                            format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
           'league_id': view_kwargs['league_id'],
           'pk': view_kwargs['id']
        }
        return self.get_queryset().get(**lookup_kwargs)

class SeasonSerializer(ModelSerializer):
    url = LeagueRelatedHyperlinkedIdentityField(
        view_name='api_v1:season_detail',
        lookup_url_kwarg='id'
    )
    games = LeagueRelatedHyperlinkedIdentityField(
        view_name='api_v1:game_list',
        lookup_field='id',
        lookup_url_kwarg='season_id'
    )

    class Meta:
        model = models.Season

class GameSerializer(ModelSerializer):
    url = SeasonRelatedHyperlinkedIdentityField(
        view_name='api_v1:game_detail',
        lookup_url_kwarg='id'
    )
    venue = HyperlinkedRelatedField(
        view_name='api_v1:venue_detail',
        lookup_field='id',
        required=False,
        queryset=models.Venue.objects.all()
    )
    team_1 = TeamHyperlink(
        lookup_field='id'
    )
    team_2 = TeamHyperlink(
        lookup_field='id'
    )
    team_1_score = IntegerField(read_only=True)
    team_2_score = IntegerField(read_only=True)

    class Meta:
        model = models.Game

class VenueSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(
        view_name='api_v1:venue_detail',
        lookup_field='id'
    )
    alternative_names = HyperlinkedIdentityField(
        view_name='api_v1:venue_alternative_name_list',
        lookup_field='id',
        lookup_url_kwarg='venue_id'
    )
    class Meta:
        model = models.Venue

class VenueRelatedHyperlinkedIdentityField(HyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        return self.reverse(view_name,
                            kwargs={self.lookup_url_kwarg: obj.id,
                                    'venue_id': obj.venue.id},
                            request=request,
                            format=format)


class VenueAlternativeNameSerializer(ModelSerializer):
    url = VenueRelatedHyperlinkedIdentityField(
        view_name='api_v1:venue_alternative_name_detail',
        lookup_url_kwarg='id'
    )

    class Meta:
        model = models.VenueAlternativeName
