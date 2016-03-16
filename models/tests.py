from random import randint

from django.test import TestCase

from .models import Game

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
