import json
import uuid
from pprint import pprint

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

class LeagueCreateTest(TestCase):
    def test_create_league(self):
        """Create a league."""
        post_data = {'id': 'AFL', 'name': 'Australian Football League'}
        response = self.client.post('/v1/leagues', post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertRegex(response['Location'], '/v1/leagues/AFL$')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], 'AFL')
        self.assertEqual(response_data['name'], 'Australian Football League')
        self.assertRegex(response_data['url'], '/v1/leagues/AFL$')
        league = League.objects.get(pk='AFL')
        self.assertEqual(league.id, 'AFL')
        self.assertEqual(league.name, 'Australian Football League')

    def test_missing_id(self):
        """Create a league without an ID"""
        response = self.client.post('/v1/leagues', {'name': 'blah'})
        self.assertEqual(response.status_code, 400)

    def test_invalid_id(self):
        """Create a league with an invalid ID"""
        response = self.client.post('/v1/leagues', {'id': '', 'name': 'blah'})
        self.assertEqual(response.status_code, 400)
        invalid_post_data = {'id': 'x' * 201, 'name': 'blah'}
        response = self.client.post('/v1/leagues', invalid_post_data)
        self.assertEqual(response.status_code, 400)

    def test_existing_id(self):
        """Create a league with an ID that alrady exists"""
        league = League(id='AFL', name='Australian Football League')
        league.save()
        post_data = {'id': 'AFL', 'name': 'Australian Football League'}
        response = self.client.post('/v1/leagues', post_data)
        self.assertEqual(response.status_code, 400)

    def test_missing_name(self):
        """Create a league without a name"""
        response = self.client.post('/v1/leagues', {'id': 'blah'})
        self.assertEqual(response.status_code, 400)

class LeagueEditTest(TestCase):
    def test_edit_league(self):
        """Edit a league"""
        league = League(id='AFL', name='Always Failing Law')
        league.save()
        put_data = {'id': 'AFL', 'name': 'Australian Football League'}
        response = self.client.put('/v1/leagues/AFL',
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], 'AFL')
        self.assertEqual(response_data['name'], 'Australian Football League')
        self.assertRegex(response_data['url'], '/v1/leagues/AFL$')
        league.refresh_from_db()
        self.assertEqual(league.id, 'AFL')
        self.assertEqual(league.name, 'Australian Football League')

    def test_missing_name(self):
        """Edit a league without a name"""
        league = League(id='AFL', name='Always Failing Law')
        league.save()
        put_data = {'id': 'AFL'}
        response = self.client.put('/v1/leagues/AFL',
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_no_such_league(self):
        """Edit a non-existent league"""
        put_data = {'id': 'AFL', 'name': 'Australian Football League'}
        response = self.client.put('/v1/leagues/no_such_league',
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)