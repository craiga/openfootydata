import json

from django.test import TestCase

from models.models import Season
from .helpers import create_season, create_league, random_string, DeleteTestCase

class SeasonDetailTest(TestCase):
    def test_season_detail(self):
        """Get season detail."""
        season = create_season()
        url = '/v1/leagues/{}/seasons/{}'.format(season.league.id, season.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['id'], season.id)
        self.assertEqual(data['name'], season.name)
        url_regex = r'/v1/leagues/{}/seasons/{}$'.format(season.league.id,
                                                         season.id)
        self.assertRegex(data['url'], url_regex)
        url_regex = r'/v1/leagues/{}/seasons/{}/games$'.format(season.league.id,
                                                               season.id)
        self.assertRegex(data['games'], url_regex)
        self.assertEqual(data['league'], season.league.id)

    def test_no_such_season(self):
        """Test when no season exists."""
        league = create_league()
        url = '/v1/leagues/{}/seasons/no-such-season'.format(league.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_no_such_league(self):
        """Test when no league exists."""
        season = create_season()
        url = '/v1/leagues/no-such-league/seasons/{}'.format(season.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_season_not_in_league(self):
        """Test when season not in league."""
        league = create_league()
        season = create_season()
        url = '/v1/leagues/{}/seasons/{}'.format(league.id, season.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class SeasonListTest(TestCase):
    def test_list_seasons(self):
        """Get a list of seasons."""
        league = create_league()
        season1 = create_season(league)
        season2 = create_season(league)
        season3 = create_season()
        response = self.client.get('/v1/leagues/{}/seasons'.format(league.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 2)
        seen_season1 = False
        seen_season2 = False
        for season in data['results']:
            if season['id'] == season1.id:
                seen_season1 = True
                test_season = season1
            else:
                seen_season2 = True
                test_season = season2
            self.assertEqual(season['id'], test_season.id)
            self.assertEqual(season['name'], test_season.name)
            url_regex = r'/v1/leagues/{}/seasons/{}$'.format(
                test_season.league.id, test_season.id)
            self.assertRegex(season['url'], url_regex)
            url_regex = r'/v1/leagues/{}/seasons/{}/games$'.format(
                test_season.league.id, test_season.id)
            self.assertRegex(season['games'], url_regex)
            self.assertEqual(season['league'], test_season.league.id)
        self.assertTrue(seen_season1)
        self.assertTrue(seen_season2)

    def test_filter_seasons(self):
        """Get a list of seasons filtered by name."""
        league = create_league()
        season1 = create_season(league)
        season2 = create_season(league)
        season3 = create_season()
        response = self.client.get('/v1/leagues/{}/seasons?name={}'.format(
            league.id, season1.name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], season1.id)
        self.assertEqual(data['results'][0]['name'], season1.name)
        url_regex = r'/v1/leagues/{}/seasons/{}$'.format(league.id, season1.id)
        self.assertRegex(data['results'][0]['url'], url_regex)
        url_regex = r'/v1/leagues/{}/seasons/{}/games$'.format(league.id,
                                                               season1.id)
        self.assertRegex(data['results'][0]['games'], url_regex)
        self.assertEqual(data['results'][0]['league'], season1.league.id)

    def test_no_seasons_in_league(self):
        """Get a list of seasons when none exist in the given league."""
        league1 = create_league()
        season1 = create_season(league1)
        season2 = create_season(league1)
        league2 = create_league()
        response = self.client.get('/v1/leagues/{}/seasons'.format(league2.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 0)

    def test_no_such_league(self):
        """Test when no matching league exists."""
        response = self.client.get('/v1/leagues/no_such_league/seasons')
        self.assertEqual(response.status_code, 404)

class SeasonCreateTest(TestCase):
    def test_create_season(self):
        """Create a season."""
        league = create_league()
        post_data = {'id': random_string(),
                     'name': random_string()}
        url = '/v1/leagues/{}/seasons'.format(league.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        url_regex = r'/v1/leagues/{}/seasons/{}$'.format(league.id,
                                                         post_data['id'])
        self.assertRegex(response['Location'], url_regex)
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], post_data['id'])
        self.assertEqual(response_data['name'], post_data['name'])
        self.assertEqual(response_data['league'], league.id)
        self.assertRegex(response_data['url'], url_regex)
        url_regex = r'/v1/leagues/{}/seasons/{}/games$'.format(league.id,
                                                               post_data['id'])
        self.assertRegex(response_data['games'], url_regex)
        season = Season.objects.get(pk=post_data['id'])
        self.assertEqual(season.id, post_data['id'])
        self.assertEqual(season.name, post_data['name'])
        self.assertEqual(season.league.id, league.id)

    def test_missing_id(self):
        """Create a season without an ID"""
        league = create_league()
        post_data = {'name': random_string()}
        url = '/v1/leagues/{}/seasons'.format(league.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

    def test_invalid_id(self):
        """Create a season with an invalid ID"""
        league = create_league()
        url = '/v1/leagues/{}/seasons'.format(league.id)
        invalid_ids = ('', random_string(length=201), 'hello-world')
        for invalid_id in invalid_ids:
            post_data = {'id': invalid_id,
                         'name': random_string()}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)

    def test_existing_id(self):
        """Create a season with an ID that already exists"""
        season = create_season()
        post_data = {'id': season.id, 'name': random_string()}
        url = '/v1/leagues/{}/seasons'.format(season.league.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

    def test_missing_name(self):
        """Create a season without a name"""
        league = create_league()
        post_data = {'id': random_string()}
        url = '/v1/leagues/{}/seasons'.format(league.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

class SeasonEditTest(TestCase):
    def test_edit_season(self):
        """Edit a season"""
        season = create_season()
        put_data = {'id': season.id,
                    'name': random_string()}
        url = '/v1/leagues/{}/seasons/{}'.format(season.league.id, season.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], put_data['id'])
        self.assertEqual(response_data['name'], put_data['name'])
        self.assertEqual(response_data['league'], season.league.id)
        url_regex = r'/v1/leagues/{}/seasons/{}$'.format(season.league.id,
                                                         season.id)
        self.assertRegex(response_data['url'], url_regex)
        url_regex = r'/v1/leagues/{}/seasons/{}/games$'.format(season.league.id,
                                                               season.id)
        self.assertRegex(response_data['games'], url_regex)
        season.refresh_from_db()
        self.assertEqual(season.name, put_data['name'])
        self.assertEqual(season.league.id, season.league.id)

    def test_no_such_season(self):
        """Edit a non-existent season"""
        league = create_league()
        put_data = {'id': random_string(),
                    'name': random_string()}
        url = '/v1/leagues/{}/seasons/no_such_season'.format(league.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_no_such_league(self):
        """Edit a season in a non-existent league"""
        season = create_season()
        put_data = {'id': season.id,
                    'name': random_string()}
        url = '/v1/leagues/no_such_league/seasons/{}'.format(season.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_season_not_in_league(self):
        """Edit a season from a league it doesn't exist in"""
        league = create_league()
        season = create_season()
        put_data = {'id': season.id,
                    'name': random_string()}
        url = '/v1/leagues/{}/seasons/{}'.format(league.id, season.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_missing_name(self):
        """Edit a season without a name"""
        season = create_season()
        put_data = {'id': season.id}
        url = '/v1/leagues/{}/seasons/{}'.format(season.league.id, season.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

class SeasonDeleteTest(DeleteTestCase):
    def test_delete(self):
        """Test deleting seasons."""
        season = create_season()
        other_league = create_league()
        self.assertSuccess('leagues', season.league.id, 'seasons', season.id)
        self.assertNotFound('leagues', season.league.id, 'seasons', 'no_such')
        self.assertNotFound('leagues', 'no_such', 'seasons', season.id)
        self.assertNotFound('leagues', other_league.id, 'seasons', season.id)
