from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from models.models import League
from . import json_converters

def league_list(request):
    """List leagues."""
    data = {'leagues': {}}
    leagues = League.objects.all()
    for league in leagues:
        data['leagues'][league.id] = json_converters.league(league)
    return JsonResponse(data)

def league_detail(request, league_id):
    """Show detail of a league."""
    league = get_object_or_404(League, pk=league_id)
    return JsonResponse(json_converters.league(league))
