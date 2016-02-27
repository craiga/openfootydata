import random
import string

from models import models

def random_string(length=5):
   return ''.join(random.choice(string.ascii_letters) for i in range(length))

def random_colour():
    return '#%02X%02X%02X' % (random.randint(0,255),
                              random.randint(0,255),
                              random.randint(0,255))

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