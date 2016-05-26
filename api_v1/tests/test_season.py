import json

from django.test import TestCase

from models.models import Season
from . import (create_season,
               create_league,
               random_string,
               DeleteTestCase,
               GetTestCase)


class SeasonTestCase:
    """Base class for all season tests."""

    def assertSeason(self, json, season):
        """
        Assert that the given parse season JSON data is the same as the given
        season.
        """
        self.assertEqual(json['id'], season.id)
        self.assertEqual(json['name'], season.name)
        self.assertSeasonUrl(json['url'], season)
        self.assertGamesUrl(json['games'], season)
        self.assertEqual(json['league'], season.league_id)

    def assertSeasons(self, json, seasons):
        """
        Assert that the given list of parsed season JSON data is the same as
        the given list of seasons.
        """
        self.assertEqual(len(json), len(seasons))
        seasons = {season.id:season for season in seasons}
        for json_item in json:
            self.assertSeason(json_item, seasons[json_item['id']])
            del seasons[json_item['id']]
        self.assertEqual(0, len(seasons))

    def assertSeasonUrl(self, url, season):
        """Assert that the given URL relates to the given season."""
        url_regex = '/v1/leagues/{}/seasons/{}$'.format(season.league_id,
                                                        season.id)
        self.assertRegex(url, url_regex)

    def assertGamesUrl(self, url, season):
        """Assert that the given URL relates to games in the given season."""
        url_regex = '/v1/leagues/{}/seasons/{}/games$'.format(season.league_id,
                                                              season.id)
        self.assertRegex(url, url_regex)


class SeasonDetailTest(GetTestCase, SeasonTestCase):
    def test_season_detail(self):
        """Get season detail."""
        season = create_season()
        self.assertSuccess('leagues', season.league_id, 'seasons', season.id)
        json = self.assertJson()
        self.assertSeason(json, season)

    def test_no_such_season(self):
        """Test when no season exists."""
        season = create_season()
        other_league = create_league()
        self.assertNotFound('leagues', season.league_id, 'seasons', 'no_season')
        self.assertNotFound('leagues', 'no_such_league', 'seasons', season.id)
        self.assertNotFound('leagues', other_league.id, 'seasons', season.id)


class SeasonListTest(GetTestCase, SeasonTestCase):
    def test_list_seasons(self):
        """Get a list of seasons."""
        league = create_league()
        seasons_in_league = (create_season(league), create_season(league))
        season_outside_of_league = create_season()
        self.assertSuccess('leagues', league.id, 'seasons')
        json = self.assertJson()
        self.assertSeasons(json['results'], seasons_in_league)

    def test_filter_seasons(self):
        """Get a list of seasons filtered by name."""
        league = create_league()
        seasons = (create_season(league), create_season(league))
        for season in seasons:
            self.assertSuccess('leagues', league.id,
                               'seasons?name=' + season.name)
            json = self.assertJson()
            self.assertSeasons(json['results'], (season,))

    def test_no_seasons_in_league(self):
        """Get a list of seasons when none exist in the given league."""
        league = create_league()
        self.assertSuccess('leagues', league.id, 'seasons')
        json = self.assertJson()
        self.assertEqual(len(json['results']), 0)

    def test_no_such_league(self):
        """Test when no matching league exists."""
        self.assertNotFound('leagues', 'no_such_league', 'seasons')

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
        self.assertEqual(season.league_id, league.id)

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
        url = '/v1/leagues/{}/seasons'.format(season.league_id)
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
        url = '/v1/leagues/{}/seasons/{}'.format(season.league_id, season.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], put_data['id'])
        self.assertEqual(response_data['name'], put_data['name'])
        self.assertEqual(response_data['league'], season.league_id)
        url_regex = r'/v1/leagues/{}/seasons/{}$'.format(season.league_id,
                                                         season.id)
        self.assertRegex(response_data['url'], url_regex)
        url_regex = r'/v1/leagues/{}/seasons/{}/games$'.format(season.league_id,
                                                               season.id)
        self.assertRegex(response_data['games'], url_regex)
        season.refresh_from_db()
        self.assertEqual(season.name, put_data['name'])
        self.assertEqual(season.league_id, season.league_id)

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
        url = '/v1/leagues/{}/seasons/{}'.format(season.league_id, season.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

class SeasonDeleteTest(DeleteTestCase):
    def test_delete(self):
        """Test deleting seasons."""
        season = create_season()
        other_league = create_league()
        self.assertSuccess('leagues', season.league_id, 'seasons', season.id)
        self.assertNotFound('leagues', season.league_id, 'seasons', 'no_such')
        self.assertNotFound('leagues', 'no_such', 'seasons', season.id)
        self.assertNotFound('leagues', other_league.id, 'seasons', season.id)
