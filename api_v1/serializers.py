from rest_framework.serializers import (HyperlinkedIdentityField,
                                        HyperlinkedRelatedField,
                                        SlugRelatedField,
                                        ModelSerializer,
                                        IntegerField,
                                        CharField)

from models import models

class LeagueSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api_v1:league_detail')
    seasons = HyperlinkedIdentityField(view_name='api_v1:season_list',
                                       lookup_url_kwarg='league_id')

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
        view_name='api_v1:team_detail')
    alternative_names = SlugRelatedField(many=True,
                                         read_only=True,
                                         slug_field='name')

    class Meta:
        model = models.Team

class TeamHyperlink(HyperlinkedRelatedField):
    view_name = 'api_v1:team_detail'
    queryset = models.Team.objects.all()

    def get_url(self, obj, view_name, request, format):
        team = models.Team.objects.get(pk=obj.pk)
        return self.reverse(view_name,
                            kwargs={self.lookup_url_kwarg: team.id,
                                    'league_id': team.league.id},
                            request=request,
                            format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {'league_id': view_kwargs['league_id'],
           self.lookup_url_kwarg: view_kwargs[self.lookup_url_kwarg]}
        return self.get_queryset().get(**lookup_kwargs)

class TeamRelatedHyperlinkedIdentityField(HyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        return self.reverse(view_name,
                            kwargs={self.lookup_url_kwarg: obj.id,
                                    'team_id': obj.team.id,
                                    'league_id': obj.team.league.id},
                            request=request,
                            format=format)

class TeamAlternativeNameSerializer(ModelSerializer):
    url = TeamRelatedHyperlinkedIdentityField(
        view_name='api_v1:team_alternative_name_detail')

    class Meta:
        model = models.TeamAlternativeName

class SeasonSerializer(ModelSerializer):
    url = LeagueRelatedHyperlinkedIdentityField(
        view_name='api_v1:season_detail')
    games = LeagueRelatedHyperlinkedIdentityField(view_name='api_v1:game_list',
                                                  lookup_url_kwarg='season_id')

    class Meta:
        model = models.Season

class GameSerializer(ModelSerializer):
    url = SeasonRelatedHyperlinkedIdentityField(view_name='api_v1:game_detail')
    venue = HyperlinkedRelatedField(view_name='api_v1:venue_detail',
                                    required=False,
                                    queryset=models.Venue.objects.all())
    team_1 = TeamHyperlink()
    team_2 = TeamHyperlink()
    team_1_score = IntegerField(read_only=True)
    team_2_score = IntegerField(read_only=True)

    class Meta:
        model = models.Game

class VenueSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='api_v1:venue_detail')
    alternative_names = SlugRelatedField(many=True,
                                         read_only=True,
                                         slug_field='name')
    timezone = CharField(read_only=True)

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
        view_name='api_v1:venue_alternative_name_detail')

    class Meta:
        model = models.VenueAlternativeName
