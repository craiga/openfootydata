import json

from django.test import TestCase

from models.models import League
from .helpers import create_league, random_string, DeleteTestCase, GetTestCase


class LeagueTestCase:
    """Base class for all league tests."""

    def assertLeague(self, json, league):
        """
        Assert that the given parsed league JSON data is the same as the given
        league.
        """
        self.assertEqual(json['id'], league.id)
        self.assertEqual(json['name'], league.name)
        self.assertLeagueUrl(json['url'], league)
        self.assertSeasonsUrl(json['seasons'], league)

    def assertLeagueUrl(self, url, league):
        """Assert that the given URL relates to the given league."""
        self.assertRegex(url, '/v1/leagues/{}$'.format(league.id))

    def assertSeasonsUrl(self, url, league):
        """
        Assert that the given URL relates to the seasons in the given league.
        """
        self.assertRegex(url, '/v1/leagues/{}/seasons$'.format(league.id))


class LeagueDetailTest(GetTestCase, LeagueTestCase):
    def test_league_detail(self):
        """Get league detail."""
        league = create_league()
        self.assertSuccess('leagues', league.id)
        json = self.assertJson()
        self.assertLeague(json, league)

    def test_no_such_league(self):
        """Test when no league exists."""
        self.assertNotFound('leagues', 'no_such_league')

class LeagueListTest(TestCase):
    def test_list_leagues(self):
        """Get a list of leagues."""
        league1 = create_league()
        league2 = create_league()
        response = self.client.get('/v1/leagues')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 2)
        seen_league1 = False
        seen_league2 = False
        for league in data['results']:
            if league['id'] == league1.id:
                seen_league1 = True
                test_league = league1
            else:
                seen_league2 = True
                test_league = league2
            self.assertEqual(league['id'], test_league.id)
            self.assertEqual(league['name'], test_league.name)
            url_regex = r'/v1/leagues/{}$'.format(test_league.id)
            self.assertRegex(league['url'], url_regex)
            url_regex = r'/v1/leagues/{}/seasons$'.format(test_league.id)
            self.assertRegex(league['seasons'], url_regex)
        self.assertTrue(seen_league1)
        self.assertTrue(seen_league2)

    def test_filter_leagues(self):
        """Get a list of leagues filtered by name."""
        league1 = create_league()
        league2 = create_league()
        response = self.client.get('/v1/leagues?name=' + league1.name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], league1.id)
        self.assertEqual(data['results'][0]['name'], league1.name)
        url_regex = r'/v1/leagues/{}$'.format(league1.id)
        self.assertRegex(data['results'][0]['url'], url_regex)
        url_regex = r'/v1/leagues/{}/seasons$'.format(league1.id)
        self.assertRegex(data['results'][0]['seasons'], url_regex)
        response = self.client.get('/v1/leagues?name=' + league2.name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], league2.id)
        self.assertEqual(data['results'][0]['name'], league2.name)
        url_regex = r'/v1/leagues/{}$'.format(league2.id)
        self.assertRegex(data['results'][0]['url'], url_regex)
        url_regex = r'/v1/leagues/{}/seasons$'.format(league2.id)
        self.assertRegex(data['results'][0]['seasons'], url_regex)


    def test_no_leagues(self):
        """Get a list of leagues when none exist."""
        response = self.client.get('/v1/leagues')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 0)

class LeagueCreateTest(TestCase):
    def test_create_league(self):
        """Create a league."""
        post_data = {'id': random_string(), 'name': random_string()}
        response = self.client.post('/v1/leagues', post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        url_regex = r'/v1/leagues/{}$'.format(post_data['id'])
        self.assertRegex(response['Location'], url_regex)
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], post_data['id'])
        self.assertEqual(response_data['name'], post_data['name'])
        self.assertRegex(response_data['url'], url_regex)
        url_regex = r'/v1/leagues/{}/seasons$'.format(post_data['id'])
        self.assertRegex(response_data['seasons'], url_regex)
        league = League.objects.get(pk=post_data['id'])
        self.assertEqual(league.id, post_data['id'])
        self.assertEqual(league.name, post_data['name'])

    def test_missing_id(self):
        """Create a league without an ID"""
        response = self.client.post('/v1/leagues', {'name': random_string()})
        self.assertEqual(response.status_code, 400)

    def test_invalid_id(self):
        """Create a league with an invalid ID"""
        invalid_ids = ('', random_string(length=201), 'hello-world')
        # Empty string
        for invalid_id in invalid_ids:
            post_data = {'id': invalid_id, 'name': random_string()}
            response = self.client.post('/v1/leagues', post_data)
            self.assertEqual(response.status_code, 400)

    def test_existing_id(self):
        """Create a league with an ID that alrady exists"""
        league = create_league()
        post_data = {'id': league.id, 'name': random_string()}
        response = self.client.post('/v1/leagues', post_data)
        self.assertEqual(response.status_code, 400)

    def test_missing_name(self):
        """Create a league without a name"""
        response = self.client.post('/v1/leagues', {'id': random_string()})
        self.assertEqual(response.status_code, 400)

class LeagueEditTest(TestCase):
    def test_edit_league(self):
        """Edit a league"""
        league = create_league()
        put_data = {'id': league.id, 'name': random_string()}
        response = self.client.put('/v1/leagues/{}'.format(league.id),
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], league.id)
        self.assertEqual(response_data['name'], put_data['name'])
        url_regex = r'/v1/leagues/{}$'.format(league.id)
        self.assertRegex(response_data['url'], url_regex)
        url_regex = r'/v1/leagues/{}/seasons$'.format(league.id)
        self.assertRegex(response_data['seasons'], url_regex)
        league.refresh_from_db()
        self.assertEqual(league.name, put_data['name'])

    def test_missing_name(self):
        """Edit a league without a name"""
        league = create_league()
        put_data = {'id': league.id}
        response = self.client.put('/v1/leagues/{}'.format(league.id),
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_no_such_league(self):
        """Edit a non-existent league"""
        put_data = {'id': random_string(), 'name': random_string()}
        response = self.client.put('/v1/leagues/no_such_league',
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

class LeagueDeleteTest(DeleteTestCase):
    def test_delete(self):
        """Test deleting leagues."""
        league = create_league()
        self.assertSuccess('leagues', league.id)
        self.assertNotFound('leagues', 'no_such_league')
