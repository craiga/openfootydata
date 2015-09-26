from django.db import models

# Create your models here.
class League(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    name = models.TextField()

    def __str__(self):
        """String representation of a League."""
        return self.name
