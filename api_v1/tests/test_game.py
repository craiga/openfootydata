import json
import re
from random import randint
from urllib.parse import quote as urlencode
from datetime import datetime, timedelta

from django.test import TestCase
import dateutil.parser
import pytz

from models.models import Game
from . import (create_game,
               create_season,
               create_league,
               create_venue,
               create_team,
               random_string,
               random_datetime,
               GetTestCase,
               DeleteTestCase)
from .test_team import TeamTestCase
from .test_venue import VenueTestCase


class GameTestCase(TeamTestCase, VenueTestCase):
    """Base class for all game tests."""

    def assertGame(self, json, game):
        """
        Assert that the given parse game JSON data is the same as the given
        game.
        """
        self.assertEqual(json['id'], game.id)
        self.assertGameUrl(json['url'], game)
        self.assertEqual(dateutil.parser.parse(json['start']),
                         game.start)
        self.assertVenueUrl(json['venue'], game.venue)
        self.assertTeamUrl(json['team_1'], game.team_1)
        self.assertEqual(json['team_1_score'], game.team_1_score)
        self.assertEqual(json['team_1_goals'], game.team_1_goals)
        self.assertEqual(json['team_1_behinds'], game.team_1_behinds)
        self.assertTeamUrl(json['team_2'], game.team_2)
        self.assertEqual(json['team_2_score'], game.team_2_score)
        self.assertEqual(json['team_2_goals'], game.team_2_goals)
        self.assertEqual(json['team_2_behinds'], game.team_2_behinds)

    def assertGameUrl(self, url, game):
        """Assert that the given URL relates to the given game."""
        url_regex = '/v1/leagues/{}/seasons/{}/games/{}$'.format(
            game.season.league_id, game.season_id, game.id)
        self.assertRegex(url, url_regex)


class GameDetailTest(GetTestCase, GameTestCase):
    def test_game_detail(self):
        """Test getting game detail."""
        game = create_game()
        self.assertSuccess('leagues', game.season.league_id,
                           'seasons', game.season_id,
                           'games', game.id)
        json = self.assertJson()
        self.assertGame(json, game)

    def test_no_such_game(self):
        """Test when no game exists."""
        game = create_game()
        other_season = create_season()
        other_league = create_league()
        self.assertNotFound('leagues', game.season.league_id,
                            'seasons', game.season_id,
                            'games', 'no_such_game')
        self.assertNotFound('leagues', game.season.league_id,
                            'seasons', 'no_such_season',
                            'games', game.id)
        self.assertNotFound('leagues', 'no_such_league',
                            'seasons', game.season_id,
                            'games', game.id)
        self.assertNotFound('leagues', game.season.league_id,
                            'seasons', other_season.id,
                            'games', game.id)
        self.assertNotFound('leagues', other_league.id,
                            'seasons', game.season_id,
                            'games', game.id)

class GameListTest(GetTestCase, GameTestCase):
    def test_list_games(self):
        """Get a list of games."""
        league = create_league()
        season = create_season(league=league)
        now = datetime.now(pytz.utc)
        game_tomorrow = create_game(season=season,
                                    league=league,
                                    start=now + timedelta(days=1))
        game_yesterday = create_game(season=season,
                                     league=league,
                                     start=now - timedelta(days=1))
        game_last_week = create_game(season=season,
                                     league=league,
                                     start=now - timedelta(days=7))
        game_next_week = create_game(season=season,
                                     league=league,
                                     start=now + timedelta(days=7))
        game_now = create_game(season=season, league=league, start=now)
        game_other_league = create_game()
        game_other_season = create_game(league=league)
        self.assertSuccess('leagues', season.league_id,
                           'seasons', season.id,
                           'games')
        json = self.assertJson()
        self.assertEquals(5, len(json['results']))
        self.assertGame(json['results'][0], game_last_week)
        self.assertGame(json['results'][1], game_yesterday)
        self.assertGame(json['results'][2], game_now)
        self.assertGame(json['results'][3], game_tomorrow)
        self.assertGame(json['results'][4], game_next_week)

    def test_filter_by_team(self):
        """Test filtering by team."""
        league = create_league()
        season = create_season(league=league)
        game_1 = create_game(season=season, league=league)
        game_2 = create_game(season=season, league=league)
        game_3 = create_game(team_1=game_1.team_1)
        game_4 = create_game(league=league)
        self.assertSuccess('leagues', season.league_id,
                           'seasons', season.id,
                           'games?team_1=' + game_1.team_1_id)
        json = self.assertJson()
        self.assertEquals(1, len(json['results']))
        self.assertGame(json['results'][0], game_1)
        self.assertSuccess('leagues', season.league_id,
                           'seasons', season.id,
                           'games?team_2=' + game_2.team_2_id)
        json = self.assertJson()
        self.assertEquals(1, len(json['results']))
        self.assertGame(json['results'][0], game_2)

    def test_no_games_in_season(self):
        """Get a list of games when none exist in the given season."""
        season = create_season()
        game_1 = create_game()
        game_2 = create_game()
        self.assertSuccess('leagues', season.league_id,
                           'seasons', season.id,
                           'games')
        json = self.assertJson()
        self.assertEquals(0, len(json['results']))

    def test_no_such_season(self):
        """Test when no matching season exists."""
        season = create_season()
        other_league = create_league()
        self.assertNotFound('leagues', season.league_id,
                            'seasons', 'no_such_season',
                            'games')
        self.assertNotFound('leagues', 'no_such_league',
                            'seasons', season.id,
                            'games')
        self.assertNotFound('leagues', other_league.id,
                            'seasons', season.id,
                            'games')

class GameCreateTest(TestCase):
    def test_create_game(self):
        """Create a game."""
        season = create_season()
        venue = create_venue()
        venue_url = '/v1/venues/{}'.format(venue.id)
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        post_data = {'start': random_datetime(),
                     'venue': venue_url,
                     'team_1': team_1_url,
                     'team_1_goals': randint(0, 100),
                     'team_1_behinds': randint(0, 100),
                     'team_2': team_2_url,
                     'team_2_goals': randint(0, 100),
                     'team_2_behinds': randint(0, 100)}
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league_id,
                                                       season.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        url_regex = '/v1/leagues/{}/seasons/{}/games/(\d+)$'.format(
            season.league_id, season.id)
        url_match = re.search(url_regex, response['Location'])
        self.assertIsNotNone(url_match)
        game_id = int(url_match.group(1))
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], game_id)
        self.assertEqual(dateutil.parser.parse(response_data['start']),
                         post_data['start'])
        venue_regex = '/v1/venues/{}$'.format(venue.id)
        self.assertRegex(response_data['venue'], venue_regex)
        team_1_regex = '/v1/leagues/{}/teams/{}$'.format(team_1.league_id,
                                                         team_1.id)
        self.assertRegex(response_data['team_1'], team_1_regex)
        team_1_score = response_data['team_1_goals'] * 6 \
            + response_data['team_1_behinds']
        self.assertEqual(response_data['team_1_score'], team_1_score)
        self.assertEqual(response_data['team_1_goals'],
                         post_data['team_1_goals'])
        self.assertEqual(response_data['team_1_behinds'],
                         post_data['team_1_behinds'])
        team_2_regex = '/v1/leagues/{}/teams/{}$'.format(team_2.league_id,
                                                         team_2.id)
        self.assertRegex(response_data['team_2'], team_2_regex)
        team_2_score = response_data['team_2_goals'] * 6 \
            + response_data['team_2_behinds']
        self.assertEqual(response_data['team_2_score'], team_2_score)
        self.assertEqual(response_data['team_2_goals'],
                         post_data['team_2_goals'])
        self.assertEqual(response_data['team_2_behinds'],
                         post_data['team_2_behinds'])
        url_regex = '/v1/leagues/{}/seasons/{}/games/{}$'.format(
            season.league_id, season.id, game_id)
        self.assertRegex(response_data['url'], url_regex)
        game = Game.objects.get(pk=game_id)
        self.assertEqual(game.start, post_data['start'])
        self.assertEqual(game.venue_id, venue.id)
        self.assertRegex(game.team_1_id, team_1.id)
        self.assertEqual(game.team_1_score, team_1_score)
        self.assertEqual(game.team_1_goals, post_data['team_1_goals'])
        self.assertEqual(game.team_1_behinds, post_data['team_1_behinds'])
        self.assertRegex(game.team_2_id, team_2.id)
        self.assertEqual(game.team_2_score, team_2_score)
        self.assertEqual(game.team_2_goals, post_data['team_2_goals'])
        self.assertEqual(game.team_2_behinds, post_data['team_2_behinds'])
        self.assertEqual(game.season_id, season.id)

    def test_existing_game(self):
        """Test creating a game which already exists."""
        existing_game = create_game()
        team_1 = existing_game.team_1
        team_2 = existing_game.team_2
        season = existing_game.season
        venue_url = '/v1/venues/{}'.format(existing_game.venue_id)
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        post_data = {'start': existing_game.start,
                     'venue': venue_url,
                     'team_1': team_1_url,
                     'team_1_goals': randint(0, 100),
                     'team_1_behinds': randint(0, 100),
                     'team_2': team_2_url,
                     'team_2_goals': randint(0, 100),
                     'team_2_behinds': randint(0, 100)}
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league_id,
                                                       season.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

    def test_no_venue_or_scores(self):
        """Create a game with no venue or scores."""
        season = create_season()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        post_data = {'start': random_datetime(),
                     'team_1': team_1_url,
                     'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league_id,
                                                       season.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        url_regex = '/v1/leagues/{}/seasons/{}/games/(\d+)$'.format(
            season.league_id, season.id)
        url_match = re.search(url_regex, response['Location'])
        self.assertIsNotNone(url_match)
        game_id = int(url_match.group(1))
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], game_id)
        self.assertEqual(dateutil.parser.parse(response_data['start']),
                         post_data['start'])
        self.assertIsNone(response_data['venue'])
        team_1_regex = '/v1/leagues/{}/teams/{}$'.format(team_1.league_id,
                                                         team_1.id)
        self.assertRegex(response_data['team_1'], team_1_regex)
        self.assertEqual(response_data['team_1_score'], 0)
        self.assertEqual(response_data['team_1_goals'], 0)
        self.assertEqual(response_data['team_1_behinds'], 0)
        team_2_regex = '/v1/leagues/{}/teams/{}$'.format(team_2.league_id,
                                                         team_2.id)
        self.assertRegex(response_data['team_2'], team_2_regex)
        self.assertEqual(response_data['team_2_score'], 0)
        self.assertEqual(response_data['team_2_goals'], 0)
        self.assertEqual(response_data['team_2_behinds'], 0)
        url_regex = '/v1/leagues/{}/seasons/{}/games/{}$'.format(
            season.league_id, season.id, game_id)
        self.assertRegex(response_data['url'], url_regex)
        game = Game.objects.get(pk=game_id)
        self.assertEqual(game.start, post_data['start'])
        self.assertIsNone(game.venue)
        self.assertRegex(game.team_1_id, team_1.id)
        self.assertEqual(game.team_1_score, 0)
        self.assertEqual(game.team_1_goals, 0)
        self.assertEqual(game.team_1_behinds, 0)
        self.assertRegex(game.team_2_id, team_2.id)
        self.assertEqual(game.team_2_score, 0)
        self.assertEqual(game.team_2_goals, 0)
        self.assertEqual(game.team_2_behinds, 0)
        self.assertEqual(game.season_id, season.id)

    def test_missing_start(self):
        """Create a game without a start time"""
        season = create_season()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        post_data = {'team_1': team_1_url,
                     'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league_id,
                                                       season.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

    def test_invalid_start(self):
        """Create a game with an invalid start time"""
        season = create_season()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league_id,
                                                       season.id)
        invalid_starts = (random_string(), randint(0, 999), None, '')
        for invalid_start in invalid_starts:
            post_data = {'start': invalid_start,
                         'team_1': team_1_url,
                         'team_2': team_2_url}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)

    def test_invalid_venue(self):
        """Create a game with an invalid venue"""
        season = create_season()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league_id,
                                                       season.id)
        invalid_venues = (random_string(),
                          randint(0, 999),
                          '/v1/venues/nosuchvenue')
        for invalid_venue in invalid_venues:
            post_data = {'start': random_datetime(),
                         'team_1': team_1_url,
                         'team_2': team_2_url,
                         'venue': invalid_venue}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)

    def test_missing_teams(self):
        """Create a game without a team"""
        season = create_season()
        team = create_team()
        team_url = '/v1/leagues/{}/teams/{}'.format(team.league_id,
                                                    team.id)
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league_id,
                                                       season.id)
        post_data = {'start': random_datetime(),
                     'team_1': team_url}
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)
        post_data = {'start': random_datetime(),
                     'team_2': team_url}
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

    def test_invalid_teams(self):
        """Create a game with an invalid team"""
        season = create_season()
        team = create_team()
        team_url = '/v1/leagues/{}/teams/{}'.format(team.league_id,
                                                    team.id)
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league_id,
                                                       season.id)
        invalid = (random_string(),
                   randint(0, 999),
                   '',
                   None,
                   '/v1/leagues/{}/teams/nosuchteam'.format(create_league().id),
                   '/v1/leagues/nosuchleague/teams/{}'.format(create_team().id))
        for invalid_team in invalid:
            post_data = {'start': random_datetime(),
                         'team_1': team_url,
                         'team_2': invalid_team}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)
            post_data = {'start': random_datetime(),
                         'team_1': invalid_team,
                         'team_2': team_url}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)

    def test_invalid_score(self):
        """Create a game with invalid scores"""
        season = create_season()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league_id,
                                                       season.id)
        invalid_scores = (random_string(), None)
        for invalid_score in invalid_scores:
            post_data = {'start': random_datetime(),
                         'team_1': team_1_url,
                         'team_2': team_2_url,
                         'team_1_goals': invalid_score}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)
            post_data = {'start': random_datetime(),
                         'team_1': team_1_url,
                         'team_2': team_2_url,
                         'team_1_behinds': invalid_score}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)
            post_data = {'start': random_datetime(),
                         'team_1': team_1_url,
                         'team_2': team_2_url,
                         'team_2_goals': invalid_score}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)
            post_data = {'start': random_datetime(),
                         'team_1': team_1_url,
                         'team_2': team_2_url,
                         'team_2_behinds': invalid_score}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)

    def test_invalid_season(self):
        """Create a game with an invalid season"""
        league = create_league()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        invalid_seasons = (random_string())
        for invalid_season in invalid_seasons:
            url = '/v1/leagues/{}/seasons/{}/games'.format(league.id,
                                                           invalid_season)
            post_data = {'start': random_datetime(),
                         'team_1': team_1_url,
                         'team_2': team_2_url}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)

class GameEditTest(TestCase):
    def test_edit_game(self):
        """Edit a game"""
        game = create_game()
        start = random_datetime()
        venue = create_venue()
        venue_url = '/v1/venues/{}'.format(venue.id)
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        put_data = {'start': str(start),
                    'venue': venue_url,
                    'team_1': team_1_url,
                    'team_1_goals': randint(0, 100),
                    'team_1_behinds': randint(0, 100),
                    'team_2': team_2_url,
                    'team_2_goals': randint(0, 100),
                    'team_2_behinds': randint(0, 100)}
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league_id,
                                                          game.season_id,
                                                          game.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], game.id)
        self.assertEqual(dateutil.parser.parse(response_data['start']), start)
        venue_url_regex = '/v1/venues/{}$'.format(venue.id)
        self.assertRegex(response_data['venue'], venue_url_regex)
        team_1_regex = '/v1/leagues/{}/teams/{}$'.format(team_1.league_id,
                                                         team_1.id)
        self.assertRegex(response_data['team_1'], team_1_regex)
        team_1_score = put_data['team_1_goals'] * 6 + put_data['team_1_behinds']
        self.assertEqual(response_data['team_1_score'], team_1_score)
        self.assertEqual(response_data['team_1_goals'],
                         put_data['team_1_goals'])
        self.assertEqual(response_data['team_1_behinds'],
                         put_data['team_1_behinds'])
        team_2_regex = '/v1/leagues/{}/teams/{}$'.format(team_2.league_id,
                                                         team_2.id)
        self.assertRegex(response_data['team_2'], team_2_regex)
        team_2_score = put_data['team_2_goals'] * 6 + put_data['team_2_behinds']
        self.assertEqual(response_data['team_2_score'], team_2_score)
        self.assertEqual(response_data['team_2_goals'],
                         put_data['team_2_goals'])
        self.assertEqual(response_data['team_2_behinds'],
                         put_data['team_2_behinds'])
        game.refresh_from_db()
        self.assertEqual(game.start, start)
        self.assertEqual(game.venue_id, venue.id)
        self.assertEqual(game.team_1_id, team_1.id)
        self.assertEqual(game.team_1_score, team_1_score)
        self.assertEqual(game.team_1_goals, put_data['team_1_goals'])
        self.assertEqual(game.team_1_behinds, put_data['team_1_behinds'])
        self.assertEqual(game.team_2_id, team_2.id)
        self.assertEqual(game.team_2_score, team_2_score)
        self.assertEqual(game.team_2_goals, put_data['team_2_goals'])
        self.assertEqual(game.team_2_behinds, put_data['team_2_behinds'])

    def test_no_venue_or_scores(self):
        """Edit a game with no venue or scores"""
        game = create_game()
        start = random_datetime()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        put_data = {'start': str(start),
                    'team_1': team_1_url,
                    'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league_id,
                                                          game.season_id,
                                                          game.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], game.id)
        self.assertEqual(dateutil.parser.parse(response_data['start']), start)
        venue_url_regex = '/v1/venues/{}$'.format(game.venue_id)
        self.assertRegex(response_data['venue'], venue_url_regex)
        team_1_regex = '/v1/leagues/{}/teams/{}$'.format(team_1.league_id,
                                                         team_1.id)
        self.assertRegex(response_data['team_1'], team_1_regex)
        self.assertEqual(response_data['team_1_score'], game.team_1_score)
        self.assertEqual(response_data['team_1_goals'], game.team_1_goals)
        self.assertEqual(response_data['team_1_behinds'], game.team_1_behinds)
        team_2_regex = '/v1/leagues/{}/teams/{}$'.format(team_2.league_id,
                                                         team_2.id)
        self.assertRegex(response_data['team_2'], team_2_regex)
        self.assertEqual(response_data['team_2_score'], game.team_2_score)
        self.assertEqual(response_data['team_2_goals'], game.team_2_goals)
        self.assertEqual(response_data['team_2_behinds'], game.team_2_behinds)
        game.refresh_from_db()
        self.assertEqual(game.start, start)
        self.assertEqual(game.team_1_id, team_1.id)
        self.assertEqual(game.team_2_id, team_2.id)

    def test_no_such_game(self):
        """Edit a non-existent game"""
        season = create_season()
        put_data = {'start': str(random_datetime())}
        url = '/v1/leagues/{}/seasons/{}/games/nogame'.format(season.league_id,
                                                              season.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_no_such_season(self):
        """Edit a game in a non-existent season"""
        game = create_game()
        start = random_datetime()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        put_data = {'start': str(start),
                    'team_1': team_1_url,
                    'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/no/games/{}'.format(game.season.league_id,
                                                          game.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_game_not_in_season(self):
        """Edit a game from a season it doesn't exist in"""
        game = create_game()
        season = create_season()
        start = random_datetime()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        put_data = {'start': str(start),
                    'team_1': team_1_url,
                    'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league_id,
                                                          season.id,
                                                          game.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_no_such_league(self):
        """Edit a game in a non-existent league"""
        game = create_game()
        start = random_datetime()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        put_data = {'start': str(start),
                    'team_1': team_1_url,
                    'team_2': team_2_url}
        url = '/v1/leagues/noleague/seasons/{}/games/{}'.format(game.season_id,
                                                                game.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_game_not_in_league(self):
        """Edit a game from a league it doesn't exist in"""
        game = create_game()
        league = create_league()
        start = random_datetime()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        put_data = {'start': str(start),
                    'team_1': team_1_url,
                    'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(league.id,
                                                          game.season_id,
                                                          game.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_missing_start(self):
        """Edit a game without a start time"""
        game = create_game()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        put_data = {'team_1': team_1_url,
                    'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league_id,
                                                          game.season_id,
                                                          game.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_start(self):
        """Edit a game with an invalid start time"""
        game = create_game()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league_id,
                                                          game.season_id,
                                                          game.id)
        invalid_starts = (random_string(), randint(0, 999), None, '')
        for invalid_start in invalid_starts:
            put_data = {'start': invalid_start,
                        'team_1': team_1_url,
                        'team_2': team_2_url}
            response = self.client.put(url,
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_invalid_venue(self):
        """Edit a game with an invalid venue"""
        game = create_game()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league_id,
                                                          game.season_id,
                                                          game.id)
        invalid_venues = (random_string(),
                          randint(0, 999),
                          '/v1/venues/nosuchvenue')
        for invalid_venue in invalid_venues:
            put_data = {'start': str(random_datetime()),
                        'team_1': team_1_url,
                        'team_2': team_2_url,
                        'venue': invalid_venue}
            response = self.client.put(url,
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_missing_teams(self):
        """Edit a game without any teams"""
        game = create_game()
        team = create_team()
        team_url = '/v1/leagues/{}/teams/{}'.format(team.league_id, team.id)
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league_id,
                                                          game.season_id,
                                                          game.id)
        put_data = {'start': str(random_datetime),
                    'team_1': team_url}
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        put_data = {'start': str(random_datetime),
                    'team_2': team_url}
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_teams(self):
        """Edit a game with an invalid team"""
        game = create_game()
        team = create_team()
        team_url = '/v1/leagues/{}/teams/{}'.format(team.league_id,
                                                    team.id)
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league_id,
                                                          game.season_id,
                                                          game.id)
        invalid = (random_string(),
                   randint(0, 999),
                   '',
                   None,
                   '/v1/leagues/{}/teams/nosuchteam'.format(create_league().id),
                   '/v1/leagues/nosuchleague/teams/{}'.format(create_team().id))
        for invalid_team in invalid:
            put_data = {'start': str(random_datetime()),
                        'team_1': team_url,
                        'team_2': invalid_team}
            response = self.client.put(url,
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)
            put_data = {'start': str(random_datetime()),
                        'team_1': invalid_team,
                        'team_2': team_url}
            response = self.client.put(url,
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_invalid_score(self):
        """Edit a game with invalid scores"""
        game = create_game()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league_id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league_id,
                                                      team_2.id)
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league_id,
                                                          game.season_id,
                                                          game.id)
        invalid_scores = (random_string(), None)
        for invalid_score in invalid_scores:
            put_data = {'start': str(random_datetime()),
                        'team_1': team_1_url,
                        'team_2': team_2_url,
                        'team_1_goals': invalid_score}
            response = self.client.put(url,
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)
            put_data = {'start': str(random_datetime()),
                        'team_1': team_1_url,
                        'team_2': team_2_url,
                        'team_1_behinds': invalid_score}
            response = self.client.put(url,
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)
            put_data = {'start': str(random_datetime()),
                        'team_1': team_1_url,
                        'team_2': team_2_url,
                        'team_2_goals': invalid_score}
            response = self.client.put(url,
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)
            put_data = {'start': str(random_datetime()),
                        'team_1': team_1_url,
                        'team_2': team_2_url,
                        'team_2_behinds': invalid_score}
            response = self.client.put(url,
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)

class GameDeleteTest(DeleteTestCase):
    def test_delete(self):
        """Test deleting games."""
        game = create_game()
        other_season = create_season()
        other_league = create_league()
        self.assertSuccess('leagues', game.season.league_id,
                           'seasons', game.season_id,
                           'games', game.id)
        self.assertNotFound('leagues', game.season.league_id,
                            'seasons', game.season_id,
                            'games', 'no_such_game')
        self.assertNotFound('leagues', game.season.league_id,
                            'seasons', 'no_such_season',
                            'games', game.id)
        self.assertNotFound('leagues', 'no_such_league',
                            'seasons', game.season_id,
                            'games', game.id)
        self.assertNotFound('leagues', game.season.league_id,
                            'seasons', other_season.id,
                            'games', game.id)
        self.assertNotFound('leagues', other_league.id,
                            'seasons', game.season_id,
                            'games', game.id)

