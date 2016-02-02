from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    url(r'^leagues$', views.LeagueList.as_view()),
    url(r'^leagues/(?P<id>\w+)$', views.LeagueDetail.as_view(),
        name='league_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
