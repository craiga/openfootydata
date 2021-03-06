from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    url(r'^leagues$', views.LeagueList.as_view(), name='league_list'),
    url(r'^leagues/(?P<pk>\w+)$', views.LeagueDetail.as_view(),
        name='league_detail'),
    url(r'^leagues/(?P<league_id>\w+)/teams$',
        views.TeamList.as_view(),
        name='team_list'),
    url(r'^leagues/(?P<league_id>\w+)/teams/(?P<pk>\w+)$',
        views.TeamDetail.as_view(),
        name='team_detail'),
    url(r'^leagues/(?P<league_id>\w+)/teams/(?P<team_id>\w+)'
        '/alternative_names$',
        views.TeamAlternativeNameList.as_view(),
        name='team_alternative_name_list'),
    url(r'^leagues/(?P<league_id>\w+)/teams/(?P<team_id>\w+)'
        '/alternative_names/(?P<pk>\d+)$',
        views.TeamAlternativeNameDetail.as_view(),
        name='team_alternative_name_detail'),
    url(r'^leagues/(?P<league_id>\w+)/seasons$',
        views.SeasonList.as_view(),
        name='season_list'),
    url(r'^leagues/(?P<league_id>\w+)/seasons/(?P<pk>\w+)$',
        views.SeasonDetail.as_view(),
        name='season_detail'),
    url(r'^leagues/(?P<league_id>\w+)/seasons/(?P<season_id>\w+)/games$',
        views.GameList.as_view(),
        name='game_list'),
    url(r'^leagues/(?P<league_id>\w+)/seasons/(?P<season_id>\w+)'
        '/games/(?P<pk>\d+)$',
        views.GameDetail.as_view(),
        name='game_detail'),
    url(r'^venues$', views.VenueList.as_view(), name='venue_list'),
    url(r'^venues/(?P<pk>\w+)$',
        views.VenueDetail.as_view(),
        name='venue_detail'),
    url(r'^venues/(?P<venue_id>\w+)/alternative_names$',
        views.VenueAlternativeNameList.as_view(),
        name='venue_alternative_name_list'),
    url(r'^venues/(?P<venue_id>\w+)/alternative_names/(?P<pk>\d+)$',
        views.VenueAlternativeNameDetail.as_view(),
        name='venue_alternative_name_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
