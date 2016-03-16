from django.db import models
from django.core import validators

from colorful.fields import RGBColorField

class League(models.Model):
    id = models.CharField(max_length=200, primary_key=True, validators=[
        validators.MinLengthValidator(1),
        validators.RegexValidator(r'^\w+$')
    ])
    name = models.TextField()

    def __str__(self):
        """String representation of a league."""
        return self.name

class Team(models.Model):
    id = models.CharField(max_length=200, primary_key=True, validators=[
        validators.MinLengthValidator(1),
        validators.RegexValidator(r'^\w+$')
    ])
    league = models.ForeignKey(League, on_delete=models.PROTECT)
    name = models.TextField()
    primary_colour = RGBColorField()
    secondary_colour = RGBColorField(blank=True, null=True)
    tertiary_colour = RGBColorField(blank=True, null=True)

    def __str__(self):
        """String representation of a team."""
        return self.name

class Season(models.Model):
    id = models.CharField(max_length=200, primary_key=True, validators=[
        validators.MinLengthValidator(1),
        validators.RegexValidator(r'^\w+$')
    ])
    league = models.ForeignKey(League, on_delete=models.PROTECT)
    name = models.TextField()

    def __str__(self):
        """String representation of a season."""
        return self.name

class Venue(models.Model):
    id = models.CharField(max_length=200, primary_key=True, validators=[
        validators.MinLengthValidator(1),
        validators.RegexValidator(r'^\w+$')
    ])
    name = models.TextField()

    def __str__(self):
        """String representation of a venue."""
        return self.name

class Game(models.Model):
    id = models.AutoField(primary_key=True)
    start = models.DateTimeField()
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    venue = models.ForeignKey(Venue,
                              on_delete=models.PROTECT,
                              blank=True,
                              null=True)
    team_1 = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='+')
    team_1_goals = models.PositiveIntegerField(default=0)
    team_1_behinds = models.PositiveIntegerField(default=0)
    team_2 = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='+')
    team_2_goals = models.PositiveIntegerField(default=0)
    team_2_behinds = models.PositiveIntegerField(default=0)

    def __str__(self):
        """String representation of a game."""
        return '{} vs. {}'.format(self.team_1, self.team_2)

    @property
    def team_1_score(self):
        """Calculate the score for team_1."""
        return self.team_1_goals * 6 + self.team_1_behinds

    @property
    def team_2_score(self):
        """Calculate the score for team_2."""
        return self.team_2_goals * 6 + self.team_2_behinds
