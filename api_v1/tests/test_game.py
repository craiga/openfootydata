import json
import re
from random import randint
from urllib.parse import quote as urlencode

from django.test import TestCase
import dateutil.parser

from models.models import Game
from .helpers import create_game, create_season, create_league, create_venue, \
    create_team, random_string, random_datetime

class GameDetailTest(TestCase):
    def test_game_detail(self):
        """Get game detail."""
        game = create_game()
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league.id,
                                                         game.season.id,
                                                         game.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['id'], game.id)
        self.assertEqual(dateutil.parser.parse(data['start']), game.start)
        self.assertRegex(data['venue'], '/v1/venues/{}$'.format(game.venue.id))
        team_1_regex = '/v1/leagues/{}/teams/{}$'.format(game.season.league.id,
                                                       game.team_1.id)
        self.assertRegex(data['team_1'], team_1_regex)
        self.assertEqual(data['team_1_score'], game.team_1_score)
        self.assertEqual(data['team_1_goals'], game.team_1_goals)
        self.assertEqual(data['team_1_behinds'], game.team_1_behinds)
        team_2_regex = '/v1/leagues/{}/teams/{}$'.format(game.season.league.id,
                                                       game.team_2.id)
        self.assertRegex(data['team_2'], team_2_regex)
        self.assertEqual(data['team_2_score'], game.team_2_score)
        self.assertEqual(data['team_2_goals'], game.team_2_goals)
        self.assertEqual(data['team_2_behinds'], game.team_2_behinds)

    def test_no_such_game(self):
        """Test when no game exists."""
        season = create_season()
        url = '/v1/leagues/{}/seasons/{}/games/nogame'.format(season.league.id,
                                                              season.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_no_such_season(self):
        """Test when no season exists."""
        game = create_game()
        game.save()
        url = '/v1/leagues/{}/seasons/no-such-season/games/{}'.format(
            game.season.league.id, game.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_game_not_in_season(self):
        """Test when game not in season."""
        season = create_season()
        game = create_game()
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league.id,
                                                          season.id,
                                                          game.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_no_such_league(self):
        """Test when no league exists."""
        game = create_game()
        url = '/v1/leagues/no-such-league/seasons/{}/games/{}'.format(
            game.season.id, game.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_game_not_in_league(self):
        """Test when game not in league."""
        league = create_league()
        game = create_game()
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(league.id,
                                                          game.season.id,
                                                          game.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class GameListTest(TestCase):
    def test_list_games(self):
        """Get a list of games."""
        league = create_league()
        season = create_season(league=league)
        game1 = create_game(season=season, league=league)
        game2 = create_game(season=season, league=league)
        game3 = create_game()
        game4 = create_game(league=league)
        if game1.start > game2.start:
            tmp = game2
            game2 = game1
            game1= tmp
        response = self.client.get('/v1/leagues/{}/seasons/{}/games'.format(
            league.id, season.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 2)
        self.assertEqual(data['results'][0]['id'], game1.id)
        self.assertEqual(dateutil.parser.parse(data['results'][0]['start']),
                         game1.start)
        self.assertRegex(data['results'][0]['venue'],
                         '/v1/venues/{}$'.format(game1.venue.id))
        team_1_regex = '/v1/leagues/{}/teams/{}$'.format(game1.season.league.id,
                                                         game1.team_1.id)
        self.assertRegex(data['results'][0]['team_1'], team_1_regex)
        self.assertEqual(data['results'][0]['team_1_score'], game1.team_1_score)
        self.assertEqual(data['results'][0]['team_1_goals'], game1.team_1_goals)
        self.assertEqual(data['results'][0]['team_1_behinds'],
                         game1.team_1_behinds)
        team_2_regex = '/v1/leagues/{}/teams/{}$'.format(game1.season.league.id,
                                                         game1.team_2.id)
        self.assertRegex(data['results'][0]['team_2'], team_2_regex)
        self.assertEqual(data['results'][0]['team_2_score'], game1.team_2_score)
        self.assertEqual(data['results'][0]['team_2_goals'], game1.team_2_goals)
        self.assertEqual(data['results'][0]['team_2_behinds'],
                         game1.team_2_behinds)
        url_regex = '/v1/leagues/{}/seasons/{}/games/{}$'.format(
            game1.season.league.id, game1.season.id, game1.id)
        self.assertRegex(data['results'][0]['url'], url_regex)
        self.assertEqual(data['results'][1]['id'], game2.id)
        self.assertEqual(dateutil.parser.parse(data['results'][1]['start']),
                         game2.start)
        self.assertRegex(data['results'][1]['venue'],
                         '/v1/venues/{}$'.format(game2.venue.id))
        team_1_regex = '/v1/leagues/{}/teams/{}$'.format(game2.season.league.id,
                                                         game2.team_1.id)
        self.assertRegex(data['results'][1]['team_1'], team_1_regex)
        self.assertEqual(data['results'][1]['team_1_score'], game2.team_1_score)
        self.assertEqual(data['results'][1]['team_1_goals'], game2.team_1_goals)
        self.assertEqual(data['results'][1]['team_1_behinds'],
                         game2.team_1_behinds)
        team_2_regex = '/v1/leagues/{}/teams/{}$'.format(game2.season.league.id,
                                                         game2.team_2.id)
        self.assertRegex(data['results'][1]['team_2'], team_2_regex)
        self.assertEqual(data['results'][1]['team_2_score'], game2.team_2_score)
        self.assertEqual(data['results'][1]['team_2_goals'], game2.team_2_goals)
        self.assertEqual(data['results'][1]['team_2_behinds'],
                         game2.team_2_behinds)
        url_regex = '/v1/leagues/{}/seasons/{}/games/{}$'.format(
            game2.season.league.id, game2.season.id, game2.id)
        self.assertRegex(data['results'][1]['url'], url_regex)

    def test_filter_by_team_1(self):
        """Test filtering by team 1."""
        league = create_league()
        season = create_season(league=league)
        game1 = create_game(season=season, league=league)
        game2 = create_game(season=season, league=league)
        game3 = create_game(team_1=game1.team_1)
        game4 = create_game(league=league)
        response = self.client.get('/v1/leagues/{}/seasons/{}/games?team_1={}'\
            .format(league.id, season.id, game1.team_1.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], game1.id)

    def test_filter_by_team_2(self):
        """Test filtering by team 2."""
        league = create_league()
        season = create_season(league=league)
        game1 = create_game(season=season, league=league)
        game2 = create_game(season=season, league=league)
        game3 = create_game(team_2=game1.team_2)
        game4 = create_game(league=league)
        response = self.client.get('/v1/leagues/{}/seasons/{}/games?team_2={}'\
            .format(league.id, season.id, game1.team_2.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], game1.id)

    def test_no_games_in_season(self):
        """Get a list of games when non exist in the given season."""
        season = create_season()
        game1 = create_game()
        game2 = create_game()
        response = self.client.get('/v1/leagues/{}/seasons/{}/games'.format(
            season.league.id, season.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 0)

    def test_no_such_season(self):
        """Test when no matching season exists."""
        league = create_league()
        game1 = create_game(league=league)
        game2 = create_game()
        response = self.client.get('/v1/leagues/{}/seasons/nope/games'.format(
            league.id))
        self.assertEqual(response.status_code, 404)

class GameCreateTest(TestCase):
    def test_create_game(self):
        """Create a game."""
        season = create_season()
        venue = create_venue()
        venue_url = '/v1/venues/{}'.format(venue.id)
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        post_data = {'start': random_datetime(),
                     'venue': venue_url,
                     'team_1': team_1_url,
                     'team_1_goals': randint(0, 100),
                     'team_1_behinds': randint(0, 100),
                     'team_2': team_2_url,
                     'team_2_goals': randint(0, 100),
                     'team_2_behinds': randint(0, 100)}
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league.id,
                                                       season.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        url_regex = '/v1/leagues/{}/seasons/{}/games/(\d+)$'.format(
            season.league.id, season.id)
        url_match = re.search(url_regex, response['Location'])
        self.assertIsNotNone(url_match)
        game_id = int(url_match.group(1))
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], game_id)
        self.assertEqual(dateutil.parser.parse(response_data['start']),
                         post_data['start'])
        venue_regex = '/v1/venues/{}$'.format(venue.id)
        self.assertRegex(response_data['venue'], venue_regex)
        team_1_regex = '/v1/leagues/{}/teams/{}$'.format(team_1.league.id,
                                                         team_1.id)
        self.assertRegex(response_data['team_1'], team_1_regex)
        team_1_score = response_data['team_1_goals'] * 6 \
            + response_data['team_1_behinds']
        self.assertEqual(response_data['team_1_score'], team_1_score)
        self.assertEqual(response_data['team_1_goals'],
                         post_data['team_1_goals'])
        self.assertEqual(response_data['team_1_behinds'],
                         post_data['team_1_behinds'])
        team_2_regex = '/v1/leagues/{}/teams/{}$'.format(team_2.league.id,
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
            season.league.id, season.id, game_id)
        self.assertRegex(response_data['url'], url_regex)
        game = Game.objects.get(pk=game_id)
        self.assertEqual(game.start, post_data['start'])
        self.assertEqual(game.venue.id, venue.id)
        self.assertRegex(game.team_1.id, team_1.id)
        self.assertEqual(game.team_1_score, team_1_score)
        self.assertEqual(game.team_1_goals, post_data['team_1_goals'])
        self.assertEqual(game.team_1_behinds, post_data['team_1_behinds'])
        self.assertRegex(game.team_2.id, team_2.id)
        self.assertEqual(game.team_2_score, team_2_score)
        self.assertEqual(game.team_2_goals, post_data['team_2_goals'])
        self.assertEqual(game.team_2_behinds, post_data['team_2_behinds'])
        self.assertEqual(game.season.id, season.id)

    def test_existing_game(self):
        """Test creating a game which already exists."""
        existing_game = create_game()
        team_1 = existing_game.team_1
        team_2 = existing_game.team_2
        season = existing_game.season
        venue_url = '/v1/venues/{}'.format(existing_game.venue.id)
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        post_data = {'start': existing_game.start,
                     'venue': venue_url,
                     'team_1': team_1_url,
                     'team_1_goals': randint(0, 100),
                     'team_1_behinds': randint(0, 100),
                     'team_2': team_2_url,
                     'team_2_goals': randint(0, 100),
                     'team_2_behinds': randint(0, 100)}
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league.id,
                                                       season.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

    def test_no_venue_or_scores(self):
        """Create a game with no venue or scores."""
        season = create_season()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        post_data = {'start': random_datetime(),
                     'team_1': team_1_url,
                     'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league.id,
                                                       season.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        url_regex = '/v1/leagues/{}/seasons/{}/games/(\d+)$'.format(
            season.league.id, season.id)
        url_match = re.search(url_regex, response['Location'])
        self.assertIsNotNone(url_match)
        game_id = int(url_match.group(1))
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], game_id)
        self.assertEqual(dateutil.parser.parse(response_data['start']),
                         post_data['start'])
        self.assertIsNone(response_data['venue'])
        team_1_regex = '/v1/leagues/{}/teams/{}$'.format(team_1.league.id,
                                                         team_1.id)
        self.assertRegex(response_data['team_1'], team_1_regex)
        self.assertEqual(response_data['team_1_score'], 0)
        self.assertEqual(response_data['team_1_goals'], 0)
        self.assertEqual(response_data['team_1_behinds'], 0)
        team_2_regex = '/v1/leagues/{}/teams/{}$'.format(team_2.league.id,
                                                         team_2.id)
        self.assertRegex(response_data['team_2'], team_2_regex)
        self.assertEqual(response_data['team_2_score'], 0)
        self.assertEqual(response_data['team_2_goals'], 0)
        self.assertEqual(response_data['team_2_behinds'], 0)
        url_regex = '/v1/leagues/{}/seasons/{}/games/{}$'.format(
            season.league.id, season.id, game_id)
        self.assertRegex(response_data['url'], url_regex)
        game = Game.objects.get(pk=game_id)
        self.assertEqual(game.start, post_data['start'])
        self.assertIsNone(game.venue)
        self.assertRegex(game.team_1.id, team_1.id)
        self.assertEqual(game.team_1_score, 0)
        self.assertEqual(game.team_1_goals, 0)
        self.assertEqual(game.team_1_behinds, 0)
        self.assertRegex(game.team_2.id, team_2.id)
        self.assertEqual(game.team_2_score, 0)
        self.assertEqual(game.team_2_goals, 0)
        self.assertEqual(game.team_2_behinds, 0)
        self.assertEqual(game.season.id, season.id)

    def test_missing_start(self):
        """Create a game without a start time"""
        season = create_season()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        post_data = {'team_1': team_1_url,
                     'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league.id,
                                                       season.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

    def test_invalid_start(self):
        """Create a game with an invalid start time"""
        season = create_season()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league.id,
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
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league.id,
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
        team_url = '/v1/leagues/{}/teams/{}'.format(team.league.id,
                                                    team.id)
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league.id,
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
        team_url = '/v1/leagues/{}/teams/{}'.format(team.league.id,
                                                    team.id)
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league.id,
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
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        url = '/v1/leagues/{}/seasons/{}/games'.format(season.league.id,
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
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
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
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        put_data = {'start': str(start),
                    'venue': venue_url,
                    'team_1': team_1_url,
                    'team_1_goals': randint(0, 100),
                    'team_1_behinds': randint(0, 100),
                    'team_2': team_2_url,
                    'team_2_goals': randint(0, 100),
                    'team_2_behinds': randint(0, 100)}
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league.id,
                                                          game.season.id,
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
        team_1_regex = '/v1/leagues/{}/teams/{}$'.format(team_1.league.id,
                                                         team_1.id)
        self.assertRegex(response_data['team_1'], team_1_regex)
        team_1_score = put_data['team_1_goals'] * 6 + put_data['team_1_behinds']
        self.assertEqual(response_data['team_1_score'], team_1_score)
        self.assertEqual(response_data['team_1_goals'],
                         put_data['team_1_goals'])
        self.assertEqual(response_data['team_1_behinds'],
                         put_data['team_1_behinds'])
        team_2_regex = '/v1/leagues/{}/teams/{}$'.format(team_2.league.id,
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
        self.assertEqual(game.venue.id, venue.id)
        self.assertEqual(game.team_1.id, team_1.id)
        self.assertEqual(game.team_1_score, team_1_score)
        self.assertEqual(game.team_1_goals, put_data['team_1_goals'])
        self.assertEqual(game.team_1_behinds, put_data['team_1_behinds'])
        self.assertEqual(game.team_2.id, team_2.id)
        self.assertEqual(game.team_2_score, team_2_score)
        self.assertEqual(game.team_2_goals, put_data['team_2_goals'])
        self.assertEqual(game.team_2_behinds, put_data['team_2_behinds'])

    def test_no_venue_or_scores(self):
        """Edit a game with no venue or scores"""
        game = create_game()
        start = random_datetime()
        team_1 = create_team()
        team_2 = create_team()
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        put_data = {'start': str(start),
                    'team_1': team_1_url,
                    'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league.id,
                                                          game.season.id,
                                                          game.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], game.id)
        self.assertEqual(dateutil.parser.parse(response_data['start']), start)
        venue_url_regex = '/v1/venues/{}$'.format(game.venue.id)
        self.assertRegex(response_data['venue'], venue_url_regex)
        team_1_regex = '/v1/leagues/{}/teams/{}$'.format(team_1.league.id,
                                                         team_1.id)
        self.assertRegex(response_data['team_1'], team_1_regex)
        self.assertEqual(response_data['team_1_score'], game.team_1_score)
        self.assertEqual(response_data['team_1_goals'], game.team_1_goals)
        self.assertEqual(response_data['team_1_behinds'], game.team_1_behinds)
        team_2_regex = '/v1/leagues/{}/teams/{}$'.format(team_2.league.id,
                                                         team_2.id)
        self.assertRegex(response_data['team_2'], team_2_regex)
        self.assertEqual(response_data['team_2_score'], game.team_2_score)
        self.assertEqual(response_data['team_2_goals'], game.team_2_goals)
        self.assertEqual(response_data['team_2_behinds'], game.team_2_behinds)
        game.refresh_from_db()
        self.assertEqual(game.start, start)
        self.assertEqual(game.team_1.id, team_1.id)
        self.assertEqual(game.team_2.id, team_2.id)

    def test_no_such_game(self):
        """Edit a non-existent game"""
        season = create_season()
        put_data = {'start': str(random_datetime())}
        url = '/v1/leagues/{}/seasons/{}/games/nogame'.format(season.league.id,
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
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        put_data = {'start': str(start),
                    'team_1': team_1_url,
                    'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/no/games/{}'.format(game.season.league.id,
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
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        put_data = {'start': str(start),
                    'team_1': team_1_url,
                    'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league.id,
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
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        put_data = {'start': str(start),
                    'team_1': team_1_url,
                    'team_2': team_2_url}
        url = '/v1/leagues/noleague/seasons/{}/games/{}'.format(game.season.id,
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
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        put_data = {'start': str(start),
                    'team_1': team_1_url,
                    'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(league.id,
                                                          game.season.id,
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
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        put_data = {'team_1': team_1_url,
                    'team_2': team_2_url}
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league.id,
                                                          game.season.id,
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
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league.id,
                                                          game.season.id,
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
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league.id,
                                                          game.season.id,
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
        team_url = '/v1/leagues/{}/teams/{}'.format(team.league.id, team.id)
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league.id,
                                                          game.season.id,
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
        team_url = '/v1/leagues/{}/teams/{}'.format(team.league.id,
                                                    team.id)
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league.id,
                                                          game.season.id,
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
        team_1_url = '/v1/leagues/{}/teams/{}'.format(team_1.league.id,
                                                      team_1.id)
        team_2_url = '/v1/leagues/{}/teams/{}'.format(team_2.league.id,
                                                      team_2.id)
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league.id,
                                                          game.season.id,
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

class GameDeleteTest(TestCase):
    def test_delete_game(self):
        """Delete a game"""
        game = create_game()
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(game.season.league.id,
                                                          game.season.id,
                                                          game.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_no_such_game(self):
        """Delete a non-existent game"""
        season = create_season()
        url = '/v1/leagues/{}/seasons/{}/games/nogame'.format(season.league.id,
                                                              season.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_no_such_season(self):
        """Delete a game from a non-existent season"""
        game = create_game()
        url = '/v1/leagues/{}/seasons/no/games/{}'.format(game.season.league.id,
                                                          game.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_game_not_in_season(self):
        """Delete a game which isn't in the given season."""
        game = create_game()
        season = create_season()
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(season.league.id,
                                                          season.id,
                                                          game.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_no_such_league(self):
        """Delete a game in a non-existent league"""
        game = create_game()
        url = '/v1/leagues/noleague/seasons/{}/games/{}'.format(game.season.id,
                                                                game.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_game_not_in_league(self):
        """Delete a game from a league it doesn't exist in"""
        league = create_league()
        game = create_game()
        url = '/v1/leagues/{}/seasons/{}/games/{}'.format(league.id,
                                                          game.season.id,
                                                          game.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
