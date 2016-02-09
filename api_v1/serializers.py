from rest_framework import serializers

from models import models

class LeagueSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api_v1:league_detail',
        lookup_field='id'
    )
    class Meta:
        model = models.League

class TeamHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        return self.reverse(view_name,
                            kwargs={'id': obj.id, 'league_id': obj.league.id},
                            request=request,
                            format=format)

class TeamSerializer(serializers.ModelSerializer):
    url = TeamHyperlinkedIdentityField(
        view_name='api_v1:team_detail'
    )
    class Meta:
        model = models.Team
