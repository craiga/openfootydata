import json
import uuid

from django.test import TestCase
from django.core import urlresolvers

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
        self.assertRegex(data['url'], '/v1/leagues/afl$')

    def test_no_such_league(self):
        """Test when no league exists."""
        response = self.client.get('/v1/leagues/no_such_league')
        self.assertEqual(response.status_code, 404)

class LeagueListTest(TestCase):
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
        self.assertEqual(len(data['results']), 2)
        self.assertEqual(data['results'][0]['id'], 'afl')
        self.assertEqual(data['results'][0]['name'], league1.name)
        self.assertRegex(data['results'][0]['url'], '/v1/leagues/afl$')
        self.assertEqual(data['results'][1]['id'], 'vfl')
        self.assertEqual(data['results'][1]['name'], league2.name)
        self.assertRegex(data['results'][1]['url'], '/v1/leagues/vfl$')

    def test_no_leagues(self):
        """Get a list of leagues when none exist."""
        self.assertEqual(League.objects.all().count(), 0)
        response = self.client.get('/v1/leagues')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 0)
