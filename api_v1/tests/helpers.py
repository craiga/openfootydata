import random
import string
import datetime

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

def create_league():
    league = models.League(id=random_string(),
                           name=random_string())
    league.save()
    return league

def create_team(league=None):
    if league is None:
        league = create_league()
    team = models.Team(id=random_string(),
                       league=league,
                       name=random_string(),
                       primary_colour=random_colour(),
                       secondary_colour=random_colour(),
                       tertiary_colour=random_colour())
    team.save()
    return team

def create_season(league=None):
    if league is None:
        league = create_league()
    season = models.Season(id=random_string(),
                           league=league,
                           name=random_string())
    season.save()
    return season

def create_venue():
    venue = models.Venue(id=random_string(),
                          name=random_string())
    venue.save()
    return venue

def create_game(league=None, season=None, venue=None, team_1=None, team_2=None):
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
    game = models.Game(season=season,
                       start=random_datetime(),
                       venue=venue,
                       team_1=team_1,
                       team_1_goals=random.randint(0, 100),
                       team_1_behinds=random.randint(0, 100),
                       team_2=team_2,
                       team_2_goals=random.randint(0, 100),
                       team_2_behinds=random.randint(0, 100))
    game.save()
    return game
