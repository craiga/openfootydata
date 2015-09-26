from django.core.urlresolvers import reverse

def league(league):
    """Create JSON view of a league."""
    return {'id': league.id, 'name': league.name,
            'url': reverse('api_v1:league_detail',
                           kwargs={'league_id': 'afl'})}
