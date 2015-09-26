from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^leagues$', views.league_list),
    url(r'^leagues/(?P<league_id>\w+)$', views.league_detail,
        name='league_detail'),
]
