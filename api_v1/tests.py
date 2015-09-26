import json
from pprint import pprint

from django.test import TestCase

from models.models import League

class LeagueDetailTest(TestCase):
    def test_league_detail(self):
        """Get league detail."""
        league = League(id='afl', name='Australian Football League')
        league.save()
        response = self.client.get('/v1/leagues/afl')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['id'], league.id)
        self.assertEqual(data['name'], league.name)
        self.assertEqual(data['url'], '/v1/leagues/afl')

    def test_no_such_league(self):
        """Test when no league exists."""
        response = self.client.get('/v1/leagues/no_such_league')
        self.assertEqual(response.status_code, 404)

    def test_list_leagues(self):
        """Get a list of leagues."""
        league1 = League(id='afl', name='Australian Football League')
        league1.save()
        league2 = League(id='vfl', name='Victorian Football League')
        league2.save()
        response = self.client.get('/v1/leagues')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['leagues']), 2)
        self.assertEqual(data['leagues'][league1.id]['id'], league1.id)
        self.assertEqual(data['leagues'][league1.id]['name'], league1.name)
        self.assertEqual(data['leagues'][league1.id]['url'], '/v1/leagues/afl')
        self.assertEqual(data['leagues'][league2.id]['id'], league2.id)
        self.assertEqual(data['leagues'][league2.id]['name'], league2.name)
        self.assertEqual(data['leagues'][league2.id]['url'], '/v1/leagues/afl')

    def test_empty_list_of_leagues(self):
        """Get a list of leagues when none exist."""
        self.assertEqual(League.objects.all().count(), 0)
        response = self.client.get('/v1/leagues')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['leagues']), 0)