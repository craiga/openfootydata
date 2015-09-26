from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from models.models import League
from . import json_converters

def league_detail(request, league_id):
    """Show detail of a league."""
    league = get_object_or_404(League, pk=league_id)
    return JsonResponse(json_converters.league(league))

def page_not_found(request):
    """Return a 404 error."""
    return JsonResponse({'status': 404, 'message': 'Page not found'}, status=404)
