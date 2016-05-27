from random import randint, choice
import string
from decimal import Decimal
from unittest import mock

from django.test import TestCase

from .models import Game, Venue


class GameScoreTest(TestCase):
    def test_game_score(self):
        """Test calculation of game scores."""
        game = Game()
        self.assertEqual(0, game.team_1_score)
        self.assertEqual(0, game.team_2_score)
        game.team_1_goals = 0
        game.team_1_behinds = 0
        game.team_2_goals = randint(1, 100)
        game.team_2_behinds = randint(1, 100)
        self.assertEqual(0, game.team_1_score)
        self.assertEqual((game.team_2_goals * 6) + game.team_2_behinds,
                         game.team_2_score)
        game.team_1_goals = randint(1, 100)
        game.team_1_behinds = randint(1, 100)
        game.team_2_goals = 0
        game.team_2_behinds = 0
        self.assertEqual((game.team_1_goals * 6) + game.team_1_behinds,
                         game.team_1_score)
        self.assertEqual(0, game.team_2_score)
        game.team_1_goals = 0
        game.team_1_behinds = randint(1, 100)
        game.team_2_goals = randint(1, 100)
        game.team_2_behinds = 0
        self.assertEqual(game.team_1_behinds, game.team_1_score)
        self.assertEqual(game.team_2_goals * 6, game.team_2_score)


class VenueTimezoneTest(TestCase):
    @mock.patch('timezonefinder.TimezoneFinder.timezone_at')
    def test_time_zone(self, mock_timezone_at):
        """Test getting a time zone based on a venue's latitude and
        longitude.
        """
        tz = ''.join(choice(string.ascii_letters) for i in range(10))
        lat = Decimal('{}.{}'.format(randint(-90, 90), randint(0, 999999)))
        lon = Decimal('{}.{}'.format(randint(-180, 180), randint(0, 999999)))
        mock_timezone_at.return_value = tz
        venue = Venue()
        venue.latitude = lat
        venue.longitude = lon
        self.assertEqual(tz, venue.timezone)
        mock_timezone_at.assert_called_with(lat=lat, lng=lon)
