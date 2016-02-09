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
        """String representation of a League."""
        return self.name

class Team(models.Model):
    id = models.CharField(max_length=200, primary_key=True, validators=[
        validators.MinLengthValidator(1),
        validators.RegexValidator('^\w+$')
    ])
    league = models.ForeignKey(League, on_delete=models.PROTECT)
    name = models.TextField()
    primary_colour = RGBColorField()
    secondary_colour = RGBColorField(blank=True, null=True)
    tertiary_colour = RGBColorField(blank=True, null=True)

    def __str__(self):
        """String representation of a League."""
        return self.name
