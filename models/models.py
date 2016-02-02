from django.db import models
from django.core import validators

# Create your models here.
class League(models.Model):
    id = models.CharField(max_length=200, primary_key=True, validators=[
        validators.MinLengthValidator(1)
    ])
    name = models.TextField()

    def __str__(self):
        """String representation of a League."""
        return self.name
