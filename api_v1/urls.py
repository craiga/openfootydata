from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    url(r'^leagues$', views.LeagueList.as_view(), name='league_list'),
    url(r'^leagues/(?P<id>\w+)$', views.LeagueDetail.as_view(),
        name='league_detail'),
    url(r'^leagues/(?P<league_id>\w+)/teams$',
        views.TeamList.as_view(),
        name='team_list'),
    url(r'^leagues/(?P<league_id>\w+)/teams/(?P<id>\w+)$',
        views.TeamDetail.as_view(),
        name='team_detail'),
    url(r'^leagues/(?P<league_id>\w+)/seasons$',
        views.SeasonList.as_view(),
        name='season_list'),
    url(r'^leagues/(?P<league_id>\w+)/seasons/(?P<id>\w+)$',
        views.SeasonDetail.as_view(),
        name='season_detail'),
    url(r'^venues$', views.VenueList.as_view(), name='venue_list'),
    url(r'^venues/(?P<id>\w+)$', views.VenueDetail.as_view(),
        name='venue_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
