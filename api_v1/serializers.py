# from collections import OrderedDict
# from django.db import models
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from models import models

class LeagueSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api_v1:league_detail',
        lookup_field='id'
    )
    class Meta:
        model = models.League
        fields = ('id', 'name', 'url')

class TeamSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(
    #     view_name='api_v1:team_detail',
    #     lookup_field='id'
    # )
    class Meta:
        model = models.Team
        # fields = ('id', 'name', 'url')