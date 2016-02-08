from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_nested import routers

from . import views

urlpatterns = [
    url(r'^leagues$', views.LeagueList.as_view(), name='league_list'),
    url(r'^leagues/(?P<id>\w+)$', views.LeagueDetail.as_view(),
        name='league_detail'),
    url(r'^leagues/(?P<league_id>\w+)/teams$',
        views.TeamList.as_view(),
        name='team_list'),
    url(r'^leagues/(?P<league_id>\w+)/teams/(?P<team_id>\w+)$',
        views.TeamDetail.as_view(),
        name='team_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
