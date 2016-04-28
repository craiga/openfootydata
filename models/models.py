from datetime import datetime

from django.db import models
from django.core import validators
import pytz
import timezonefinder

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
    primary_colour = RGBColorField(blank=True, null=True)
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
    latitude = models.DecimalField(max_digits=8,
                                   decimal_places=6,
                                   validators=[
                                       validators.MinValueValidator(-90),
                                       validators.MaxValueValidator(90)])
    longitude = models.DecimalField(max_digits=9,
                                    decimal_places=6,
                                    validators=[
                                        validators.MinValueValidator(-180),
                                        validators.MaxValueValidator(180)])

    def __str__(self):
        """String representation of a venue."""
        return self.name

    @property
    def timezone(self):
        """Get the timezone of this venue based on its latitude and
        longitude.
        """
        tf = timezonefinder.TimezoneFinder()
        return tf.timezone_at(lat=self.latitude, lng=self.longitude)

class VenueAlternativeName(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    venue = models.ForeignKey(Venue,
                              on_delete=models.CASCADE,
                              related_name='alternative_names')

    def __str__(self):
        """String representation of a venue's alternative name."""
        return '{} (alternative name of {})'.format(self.name, self.venue.name)

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

    class Meta:
        unique_together = ('start', 'season', 'team_1', 'team_2')

    def __str__(self):
        """String representation of a game."""
        now = datetime.now(pytz.utc)
        if self.start < now:
            return '{} ({}.{} {}) vs. {} ({}.{} {}) at {}'.format(
                self.team_1, self.team_1_goals, self.team_1_behinds,
                self.team_1_score, self.team_2, self.team_2_goals,
                self.team_2_behinds, self.team_2_score,
                self.start.strftime('%c'))
        else:
            return '{} vs. {} at {}'.format(self.team_1,
                                            self.team_2,
                                            self.start.strftime('%c'))

    @property
    def team_1_score(self):
        """Calculate the score for team_1."""
        return self.team_1_goals * 6 + self.team_1_behinds

    @property
    def team_2_score(self):
        """Calculate the score for team_2."""
        return self.team_2_goals * 6 + self.team_2_behinds
