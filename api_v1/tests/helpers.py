import random
import string
import datetime
from decimal import Decimal

from django.test import TestCase

from models import models

def random_string(length=5):
   return ''.join(random.choice(string.ascii_letters) for i in range(length))

def random_colour():
    return '#%02X%02X%02X' % (random.randint(0,255),
                              random.randint(0,255),
                              random.randint(0,255))

def random_datetime():
    timedelta = datetime.timedelta(seconds=random.randint(-720, 720) * 60)
    return datetime.datetime(year=random.randint(datetime.MINYEAR,
                                                 datetime.MAXYEAR),
                             month=random.randint(1, 12),
                             day=random.randint(1, 28),
                             hour=random.randint(0, 23),
                             minute=random.randint(0, 59),
                             second=random.randint(0, 59),
                             microsecond=random.randint(0, 1000000 - 1),
                             tzinfo=datetime.timezone(timedelta))

def random_float(min=-100, max=100):
    return random.random() * (max - min) + min

def random_decimal(min=-100, max=100, precision=6):
    float_string = str(random_float(min, max))
    try:
        decimal_location = float_string.index('.')
    except ValueError:
        decimal_location = len(float_string)
    return Decimal(float_string[:decimal_location + 1 + precision])

def create_league():
    league = models.League(id=random_string(),
                           name=random_string())
    league.save()
    return league

def create_team(league=None, num_alternative_names=None):
    if league is None:
        league = create_league()
    if num_alternative_names is None:
        num_alternative_names = random.randint(1, 20)
    team = models.Team(id=random_string(),
                       league=league,
                       name=random_string(),
                       primary_colour=random_colour(),
                       secondary_colour=random_colour(),
                       tertiary_colour=random_colour())
    team.save()
    for i in range(0, num_alternative_names):
        create_team_alternative_name(team=team)
    return team

def create_team_alternative_name(team=None):
    if team is None:
        team = create_team()
    alt_name = models.TeamAlternativeName(team=team, name=random_string())
    alt_name.save()
    return alt_name

def create_season(league=None):
    if league is None:
        league = create_league()
    season = models.Season(id=random_string(),
                           league=league,
                           name=random_string())
    season.save()
    return season

def create_venue(num_alternative_names=None):
    if num_alternative_names is None:
        num_alternative_names = random.randint(1, 20)
    venue = models.Venue(id=random_string(),
                         name=random_string(),
                         latitude=random_decimal(-90, 90),
                         longitude=random_decimal(-180, 180))
    venue.save()
    for i in range(0, num_alternative_names):
        create_venue_alternative_name(venue=venue)
    return venue

def create_venue_alternative_name(venue=None):
    if venue is None:
        venue = create_venue()
    alt_name = models.VenueAlternativeName(venue=venue, name=random_string())
    alt_name.save()
    return alt_name

def create_game(league=None,
                season=None,
                venue=None,
                team_1=None,
                team_2=None,
                start=None):
    if league is None:
        league = create_league()
    if season is None:
        season = create_season(league=league)
    if venue is None:
        venue = create_venue()
    if team_1 is None:
        team_1 = create_team(league=league)
    if team_2 is None:
        team_2 = create_team(league=league)
    if start is None:
        start = random_datetime()
    game = models.Game(season=season,
                       start=start,
                       venue=venue,
                       team_1=team_1,
                       team_1_goals=random.randint(0, 100),
                       team_1_behinds=random.randint(0, 100),
                       team_2=team_2,
                       team_2_goals=random.randint(0, 100),
                       team_2_behinds=random.randint(0, 100))
    game.save()
    return game


def normalise_path(path):
    """Takes a list or tuple and turns it into an API v1 URL."""
    return '/v1/' + '/'.join(str(x) for x in path)


class DeleteTestCase(TestCase):
    """Base for API v1 deletion tests."""
    def assertStatusCode(self, path, status_code):
        """
        Assert that a delete request responds with the expected status code
        with the given URL parts.
        """
        path = normalise_path(path)
        response = self.client.delete(path)
        self.assertEqual(response.status_code, status_code)

    def assertSuccess(self, *args):
        """Assert that a delete request is successful."""
        self.assertStatusCode(args, 204)

    def assertNotFound(self, *args):
        """Assert that a delete request results in a 404 response."""
        self.assertStatusCode(args, 404)
