from django.contrib import admin

from . import models

admin.site.register(models.League)
admin.site.register(models.Team)
admin.site.register(models.Season)
admin.site.register(models.Game)
admin.site.register(models.Venue)
admin.site.register(models.VenueAlternativeName)
