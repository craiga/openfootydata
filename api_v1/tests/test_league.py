import json

from django.test import TestCase
from django.core.urlresolvers import reverse as url_reverse

from models.models import League
from . import create_league, random_string, DeleteTestCase, GetTestCase


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

    def assertLeagues(self, json, leagues):
        """
        Assert that the given list of parsed league JSON data is the same as
        the given list of leagues.
        """
        self.assertEqual(len(json), len(leagues))
        leagues = {league.id:league for league in leagues}
        for json_item in json:
            self.assertLeague(json_item, leagues[json_item['id']])
            del leagues[json_item['id']]
        self.assertEqual(0, len(leagues))

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

class LeagueListTest(GetTestCase, LeagueTestCase):
    def test_list_leagues(self):
        """Get a list of leagues."""
        leagues = (create_league(), create_league())
        self.assertSuccess('leagues')
        json = self.assertJson()
        self.assertLeagues(json['results'], leagues)

    def test_filter_leagues(self):
        """Get a list of leagues filtered by name."""
        leagues = (create_league(), create_league())
        for league in leagues:
            self.assertSuccess('leagues?name=' + league.name)
            json = self.assertJson()
            self.assertLeagues(json['results'], (league,))

    def test_no_leagues(self):
        """Get a list of leagues when none exist."""
        self.assertSuccess('leagues')
        json = self.assertJson()
        self.assertEqual(len(json['results']), 0)

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
