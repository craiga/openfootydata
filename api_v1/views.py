from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator

from models.models import League
from . import json_converters

def league_list(request):
    """List leagues."""
    paginator = Paginator(League.objects.all(),
                          request.GET.get('per_page') or 20)
    leagues = paginator.page(request.GET.get('page') or 1)
    data = {'page': leagues.number,
            'page_size': paginator.per_page,
            'num_items': paginator.count,
            'num_pages': paginator.num_pages,
            'leagues': {}}
    for league in leagues:
        data['leagues'][league.id] = json_converters.league(league)
    return JsonResponse(data)

def league_detail(request, league_id):
    """Show detail of a league."""
    league = get_object_or_404(League, pk=league_id)
    return JsonResponse(json_converters.league(league))
