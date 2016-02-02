from rest_framework import generics

from models.models import League
from api_v1.serializers import LeagueSerializer

class LeagueList(generics.ListCreateAPIView):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer

class LeagueDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
