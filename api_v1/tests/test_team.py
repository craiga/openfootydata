import json

from django.test import TestCase

from models.models import Team
from .helpers import (create_team,
                      create_team_alternative_name,
                      create_league,
                      random_string,
                      random_colour,
                      DeleteTestCase,
                      GetTestCase)

class TeamTestCase(TestCase):
    """Base class for team tests."""

    def assertTeam(self, json, team):
        """
        Assert that the given parsed team JSON data is the same as the given
        team.
        """
        self.assertEqual(json['id'], team.id)
        self.assertEqual(json['name'], team.name)
        self.assertEqual(json['primary_colour'], team.primary_colour)
        self.assertEqual(json['secondary_colour'], team.secondary_colour)
        self.assertEqual(json['tertiary_colour'], team.tertiary_colour)
        self.assertTeamUrl(json['url'], team)
        self.assertEqual(json['league'], team.league.id)
        self.assertEqual(set(json['alternative_names']),
                         {n.name for n in team.alternative_names.all()})

    def assertTeamUrl(self, url, team):
        """Assert that the given URL relates to the given team."""
        url_regex = '/v1/leagues/{}/teams/{}$'.format(team.league.id, team.id)
        self.assertRegex(url, url_regex)


class TeamDetailTest(GetTestCase, TeamTestCase):
    def test_team_detail(self):
        """Get team detail."""
        teams = (create_team(), create_team(num_alternative_names=0))
        for team in teams:
            self.assertSuccess('leagues', team.league.id,
                               'teams', team.id)
            json = self.assertJson()
            self.assertTeam(json, team)

    def test_no_such_team(self):
        """Test when no team exists."""
        team = create_team()
        other_league = create_league()
        self.assertNotFound('leagues', team.league.id,
                            'teams', 'no_such_team')
        self.assertNotFound('leagues', 'no_such_league',
                            'teams', team.id)
        self.assertNotFound('leagues', other_league.id,
                            'teams', team.id)


class TeamListTest(TestCase):
    def test_list_teams(self):
        """Get a list of teams."""
        league = create_league()
        team1 = create_team(league)
        team2 = create_team(league)
        team3 = create_team()
        response = self.client.get('/v1/leagues/{}/teams'.format(league.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 2)
        seen_team1 = False
        seen_team2 = False
        for team in data['results']:
            if team['id'] == team1.id:
                seen_team1 = True
                test_team = team1
            else:
                seen_team2 = True
                test_team = team2
            self.assertEqual(team['id'], test_team.id)
            self.assertEqual(team['name'], test_team.name)
            self.assertEqual(team['primary_colour'], test_team.primary_colour)
            self.assertEqual(team['secondary_colour'],
                             test_team.secondary_colour)
            self.assertEqual(team['tertiary_colour'], test_team.tertiary_colour)
            url_regex = r'/v1/leagues/{}/teams/{}$'.format(test_team.league.id,
                                                           test_team.id)
            self.assertRegex(team['url'], url_regex)
            self.assertEqual(team['league'], test_team.league.id)
            alt_names = {n.name for n in test_team.alternative_names.all()}
            self.assertEqual(set(team['alternative_names']), alt_names)
        self.assertTrue(seen_team1)
        self.assertTrue(seen_team2)

    def test_filter_teams(self):
        """Get a filtered list of teams."""
        league = create_league()
        team1 = create_team(league)
        team2 = create_team(league)
        response = self.client.get('/v1/leagues/{}/teams?name={}'.format(
            league.id, team1.name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], team1.id)
        self.assertEqual(data['results'][0]['name'], team1.name)
        self.assertEqual(data['results'][0]['primary_colour'],
                         team1.primary_colour)
        self.assertEqual(data['results'][0]['secondary_colour'],
                         team1.secondary_colour)
        self.assertEqual(data['results'][0]['tertiary_colour'],
                         team1.tertiary_colour)
        url_regex = r'/v1/leagues/{}/teams/{}$'.format(team1.league.id,
                                                       team1.id)
        self.assertRegex(data['results'][0]['url'], url_regex)
        self.assertEqual(data['results'][0]['league'], team1.league.id)

    def test_filter_teams_by_alternative_name(self):
        """Get a list of teams filtered by an alternative name."""
        league = create_league()
        team1 = create_team(league, num_alternative_names=2)
        team2 = create_team(league)
        url = '/v1/leagues/{}/teams?alternative_names__name={}'.format(
            league.id, team1.alternative_names.all()[0].name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], team1.id)

    def test_no_teams_in_league(self):
        """Get a list of teams when none exist in the given league."""
        league1 = create_league()
        team1 = create_team(league1)
        team2 = create_team(league1)
        league2 = create_league()
        response = self.client.get('/v1/leagues/{}/teams'.format(league2.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 0)

    def test_no_such_league(self):
        """Test when no matching league exists."""
        response = self.client.get('/v1/leagues/no_such_league/teams')
        self.assertEqual(response.status_code, 404)

class TeamCreateTest(TestCase):
    def test_create_team(self):
        """Create a team."""
        league = create_league()
        post_data = {'id': random_string(),
                     'name': random_string(),
                     'primary_colour': random_colour(),
                     'secondary_colour': random_colour(),
                     'tertiary_colour': random_colour()}
        url = '/v1/leagues/{}/teams'.format(league.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        url_regex = r'/v1/leagues/{}/teams/{}$'.format(league.id,
                                                       post_data['id'])
        self.assertRegex(response['Location'], url_regex)
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], post_data['id'])
        self.assertEqual(response_data['name'], post_data['name'])
        self.assertEqual(response_data['primary_colour'],
                         post_data['primary_colour'])
        self.assertEqual(response_data['secondary_colour'],
                         post_data['secondary_colour'])
        self.assertEqual(response_data['tertiary_colour'],
                         post_data['tertiary_colour'])
        self.assertEqual(response_data['league'], league.id)
        self.assertRegex(response_data['url'], url_regex)
        self.assertEqual(response_data['alternative_names'], [])
        team = Team.objects.get(pk=post_data['id'])
        self.assertEqual(team.id, post_data['id'])
        self.assertEqual(team.name, post_data['name'])
        self.assertEqual(team.primary_colour, post_data['primary_colour'])
        self.assertEqual(team.secondary_colour, post_data['secondary_colour'])
        self.assertEqual(team.tertiary_colour, post_data['tertiary_colour'])
        self.assertEqual(team.league.id, league.id)
        self.assertEqual(team.alternative_names.count(), 0)

    def test_no_colours(self):
        """Create a team without colours."""
        league = create_league()
        post_data = {'id': random_string(),
                     'name': random_string()}
        url = '/v1/leagues/{}/teams'.format(league.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], post_data['id'])
        self.assertEqual(response_data['name'], post_data['name'])
        self.assertEqual(response_data['primary_colour'], None)
        self.assertEqual(response_data['secondary_colour'], None)
        self.assertEqual(response_data['tertiary_colour'], None)
        team = Team.objects.get(pk=post_data['id'])
        self.assertEqual(team.id, post_data['id'])
        self.assertEqual(team.name, post_data['name'])
        self.assertEqual(team.primary_colour, None)
        self.assertEqual(team.secondary_colour, None)
        self.assertEqual(team.tertiary_colour, None)
        self.assertEqual(team.league.id, league.id)

    def test_missing_id(self):
        """Create a team without an ID"""
        league = create_league()
        post_data = {'name': random_string(),
                     'primary_colour': random_colour()}
        url = '/v1/leagues/{}/teams'.format(league.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

    def test_invalid_id(self):
        """Create a team with an invalid ID"""
        league = create_league()
        url = '/v1/leagues/{}/teams'.format(league.id)
        invalid_ids = ('', random_string(length=201), 'hello-world')
        for invalid_id in invalid_ids:
            post_data = {'id': invalid_id,
                         'name': random_string(),
                         'primary_colour': random_colour()}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)

    def test_existing_id(self):
        """Create a team with an ID that alrady exists"""
        team = create_team()
        post_data = {'id': team.id, 'name': random_string()}
        url = '/v1/leagues/{}/teams'.format(team.league.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

    def test_missing_name(self):
        """Create a team without a name"""
        league = create_league()
        post_data = {'id': random_string(),
                     'primary_colour': random_colour()}
        url = '/v1/leagues/{}/teams'.format(league.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

    def test_invalid_colours(self):
        """Create a team with invalid colours"""
        league = create_league()
        url = '/v1/leagues/{}/teams'.format(league.id)
        invalid_colours = (random_string())
        for invalid_colour in invalid_colours:
            post_data = {'id': random_string(),
                         'name': random_string(),
                         'primary_colour': invalid_colour}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)
            post_data = {'id': random_string(),
                         'name': random_string(),
                         'primary_colour': random_colour(),
                         'secondary_colour': invalid_colour,
                         'tertiary_colour': random_colour()}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)
            post_data = {'id': random_string(),
                         'name': random_string(),
                         'primary_colour': random_colour(),
                         'secondary_colour': random_colour(),
                         'tertiary_colour': invalid_colour}
            response = self.client.post(url, post_data)
            self.assertEqual(response.status_code, 400)

class TeamEditTest(TestCase):
    def test_edit_team(self):
        """Edit a team"""
        team = create_team()
        put_data = {'id': team.id,
                    'name': random_string(),
                    'primary_colour': random_colour(),
                    'secondary_colour': random_colour(),
                    'tertiary_colour': random_colour()}
        url = '/v1/leagues/{}/teams/{}'.format(team.league.id, team.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], put_data['id'])
        self.assertEqual(response_data['name'], put_data['name'])
        self.assertEqual(response_data['primary_colour'],
                         put_data['primary_colour'])
        self.assertEqual(response_data['secondary_colour'],
                         put_data['secondary_colour'])
        self.assertEqual(response_data['tertiary_colour'],
                         put_data['tertiary_colour'])
        self.assertEqual(response_data['league'], team.league.id)
        url_regex = r'/v1/leagues/{}/teams/{}$'.format(team.league.id, team.id)
        self.assertRegex(response_data['url'], url_regex)
        team.refresh_from_db()
        self.assertEqual(team.name, put_data['name'])
        self.assertEqual(team.primary_colour, put_data['primary_colour'])
        self.assertEqual(team.secondary_colour, put_data['secondary_colour'])
        self.assertEqual(team.tertiary_colour, put_data['tertiary_colour'])
        self.assertEqual(team.league.id, team.league.id)

    def test_no_colours(self):
        """Edit a team with no colours."""
        team = create_team()
        put_data = {'id': team.id,
                    'name': random_string()}
        url = '/v1/leagues/{}/teams/{}'.format(team.league.id, team.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], put_data['id'])
        self.assertEqual(response_data['name'], put_data['name'])
        self.assertEqual(response_data['primary_colour'], team.primary_colour)
        self.assertEqual(response_data['secondary_colour'],
                                       team.secondary_colour)
        self.assertEqual(response_data['tertiary_colour'], team.tertiary_colour)
        team.refresh_from_db()
        self.assertEqual(team.name, put_data['name'])

    def test_unset_colours(self):
        """Edit a team setting all colours to None."""
        team = create_team()
        put_data = {'id': team.id,
                    'name': random_string(),
                    'primary_colour': None,
                    'secondary_colour': None,
                    'tertiary_colour': None}
        url = '/v1/leagues/{}/teams/{}'.format(team.league.id, team.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], put_data['id'])
        self.assertEqual(response_data['name'], put_data['name'])
        self.assertEqual(response_data['primary_colour'], None)
        self.assertEqual(response_data['secondary_colour'], None)
        self.assertEqual(response_data['tertiary_colour'], None)
        team.refresh_from_db()
        self.assertEqual(team.name, put_data['name'])
        self.assertEqual(team.primary_colour, None)
        self.assertEqual(team.secondary_colour, None)
        self.assertEqual(team.tertiary_colour, None)

    def test_no_such_team(self):
        """Edit a non-existent team"""
        league = create_league()
        put_data = {'id': random_string(),
                    'name': random_string(),
                    'primary_colour': random_colour()}
        url = '/v1/leagues/{}/teams/no_such_team'.format(league.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_no_such_league(self):
        """Edit a team in a non-existent league"""
        team = create_team()
        put_data = {'id': team.id,
                    'name': random_string(),
                    'primary_colour': random_colour()}
        url = '/v1/leagues/no_such_league/teams/{}'.format(team.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_team_not_in_league(self):
        """Edit a team from a league it doesn't exist in"""
        league = create_league()
        team = create_team()
        put_data = {'id': team.id,
                    'name': random_string(),
                    'primary_colour': random_colour()}
        url = '/v1/leagues/{}/teams/{}'.format(league.id, team.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_missing_name(self):
        """Edit a team without a name"""
        team = create_team()
        put_data = {'id': team.id,
                    'primary_colour': random_colour()}
        url = '/v1/leagues/{}/teams/{}'.format(team.league.id, team.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_colours(self):
        """Edit a team with invalid colours"""
        team = create_team()
        url = '/v1/leagues/{}/teams/{}'.format(team.league.id, team.id)
        invalid_colours = (random_string())
        for invalid_colour in invalid_colours:
            put_data = {'id': random_string(),
                        'name': random_string(),
                        'primary_colour': invalid_colour,
                        'secondary_colour': random_colour(),
                        'tertiary_colour': random_colour()}
            response = self.client.put(url,
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)
            put_data = {'id': random_string(),
                        'name': random_string(),
                        'primary_colour': random_colour(),
                        'secondary_colour': invalid_colour,
                        'tertiary_colour': random_colour()}
            response = self.client.put(url,
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)
            put_data = {'id': random_string(),
                        'name': random_string(),
                        'primary_colour': random_colour(),
                        'secondary_colour': random_colour(),
                        'tertiary_colour': invalid_colour}
            response = self.client.put(url,
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)

class TeamDeleteTest(DeleteTestCase):
    def test_delete(self):
        """Test deleting teams."""
        team = create_team()
        other_league = create_league()
        self.assertSuccess('leagues', team.league.id, 'teams', team.id)
        self.assertNotFound('leagues', team.league.id, 'teams', 'no_such_team')
        self.assertNotFound('leagues', 'no_such_league', 'teams', team.id)
        self.assertNotFound('leagues', other_league.id, 'teams', team.id)

