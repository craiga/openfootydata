import json
import re

from django.test import TestCase

from models.models import TeamAlternativeName
from .helpers import (create_team_alternative_name,
                      create_league,
                      create_team,
                      random_string,
                      DeleteTestCase,
                      GetTestCase)

class TeamAlternativeNameTestCase:
    """Base class for all team alternative name tests."""

    def assertTeamAlternativeName(self, json, alt_name):
        """
        Assert that the given parsed JSON data is the same as the given team
        alternative name.
        """
        self.assertEqual(json['id'], alt_name.id)
        self.assertEqual(json['name'], alt_name.name)
        self.assertTeamAlternativeNameUrl(json['url'], alt_name)
        self.assertEqual(json['team'], alt_name.team_id)

    def assertTeamAlternativeNames(self, json, alt_names):
        """
        Assert that the given list of parsed JSON data is the same as the given
        list of alternative names.
        """
        self.assertEqual(len(json), len(alt_names))
        alt_names = {alt_name.id:alt_name for alt_name in alt_names}
        for json_item in json:
            self.assertTeamAlternativeName(json_item,
                                           alt_names[json_item['id']])
            del alt_names[json_item['id']]
        self.assertEqual(0, len(alt_names))

    def assertTeamAlternativeNameUrl(self, url, alt_name):
        """
        Assert that the given URL relates to the given team alternative name.
        """
        url_regex = '/v1/leagues/{}/teams/{}/alternative_names/{}$'.format(
            alt_name.team.league_id, alt_name.team_id, alt_name.id)
        self.assertRegex(url, url_regex)


class TeamAlternativeNameDetailTest(GetTestCase, TeamAlternativeNameTestCase):
    def test_alt_name_detail(self):
        """Get alternative name detail."""
        alt_name = create_team_alternative_name()
        self.assertSuccess('leagues', alt_name.team.league_id,
                           'teams', alt_name.team_id,
                           'alternative_names', alt_name.id)
        json = self.assertJson()
        self.assertTeamAlternativeName(json, alt_name)

    def test_no_such_alternative_name(self):
        """Test when no alternative_name exists."""
        alt_name = create_team_alternative_name()
        other_team = create_team()
        other_league = create_league()
        self.assertNotFound('leagues', alt_name.team.league_id,
                            'teams', alt_name.team_id,
                            'alternative_names', 'no_such_alt_name')
        self.assertNotFound('leagues', alt_name.team.league_id,
                            'teams', 'no_such_team',
                            'alternative_names', alt_name.id)
        self.assertNotFound('leagues', 'no_such_league',
                            'teams', alt_name.team_id,
                            'alternative_names', alt_name.id)
        self.assertNotFound('leagues', alt_name.team.league_id,
                            'teams', other_team.id,
                            'alternative_names', alt_name.id)
        self.assertNotFound('leagues', other_league.id,
                            'teams', alt_name.team_id,
                            'alternative_names', alt_name.id)


class AlternativeNameListTest(GetTestCase, TeamAlternativeNameTestCase):
    def test_list_alternative_names(self):
        """Get a list of alternative names."""
        league = create_league()
        team = create_team(league=league, num_alternative_names=0)
        alt_names = (create_team_alternative_name(team),
                     create_team_alternative_name(team))
        other_team = create_team(league=league)
        other_team_alt_name = create_team_alternative_name(team=other_team)
        other_league_alt_name = create_team_alternative_name()
        self.assertSuccess('leagues', league.id,
                           'teams', team.id,
                           'alternative_names')
        json = self.assertJson()
        self.assertTeamAlternativeNames(json['results'], alt_names)

    def test_no_alternative_names_in_team(self):
        """
        Get a list of alternative names when none exist in the given team.
        """
        team = create_team(num_alternative_names=0)
        self.assertSuccess('leagues', team.league_id,
                           'teams', team.id,
                           'alternative_names')
        json = self.assertJson()
        self.assertEqual(len(json['results']), 0)

    def test_no_such_team(self):
        """Test when no matching team exists."""
        league = create_league()
        self.assertNotFound('leagues', league.id,
                            'teams', 'no_such_team',
                            'alternative_names')

class AlternativeNameCreateTest(TestCase):
    def test_create_team_alternative_name(self):
        """Create an alternative name."""
        team = create_team()
        post_data = {'name': random_string()}
        url = '/v1/leagues/{}/teams/{}/alternative_names'.format(
            team.league_id, team.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        url_regex = '/v1/leagues/{}/teams/{}/alternative_names/(\d+)$'.format(
            team.league_id, team.id)
        url_match = re.search(url_regex, response['Location'])
        self.assertIsNotNone(url_match)
        team_id = int(url_match.group(1))
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], team_id)
        self.assertEqual(response_data['name'], post_data['name'])
        self.assertEqual(response_data['team'], team.id)
        self.assertRegex(response_data['url'], url_regex)
        alternative_name = TeamAlternativeName.objects.get(pk=team_id)
        self.assertEqual(alternative_name.name, post_data['name'])
        self.assertEqual(alternative_name.team_id, team.id)

    def test_missing_name(self):
        """Create an alternative name without a name"""
        team = create_team()
        post_data = {}
        url = '/v1/leagues/{}/teams/{}/alternative_names'.format(
            team.league_id, team.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

class AlternativeNameEditTest(TestCase):
    def test_edit_alternative_name(self):
        """Edit an alternative name"""
        alt_name = create_team_alternative_name()
        put_data = {'name': random_string()}
        url = '/v1/leagues/{}/teams/{}/alternative_names/{}'.format(
            alt_name.team.league_id, alt_name.team_id, alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], alt_name.id)
        self.assertEqual(response_data['name'], put_data['name'])
        self.assertEqual(response_data['team'], alt_name.team_id)
        url_regex = r'/v1/leagues/{}/teams/{}/alternative_names/{}$'.format(
            alt_name.team.league_id, alt_name.team_id, alt_name.id)
        self.assertRegex(response_data['url'], url_regex)
        alt_name.refresh_from_db()
        self.assertEqual(alt_name.name, put_data['name'])

    def test_no_such_alternative_name(self):
        """Edit a non-existent alternative name"""
        team = create_team()
        put_data = {'name': random_string()}
        url = '/v1/leagues/{}/teams/{}/alternative_names/none'.format(
            team.league_id, team.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_no_such_team(self):
        """Edit an alternative name in a non-existent team"""
        alt_name = create_team_alternative_name()
        put_data = {'name': random_string()}
        url = '/v1/leagues{}/teams/none/alternative_names/{}'.format(
            alt_name.team.league_id, alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_alt_name_not_in_team(self):
        """Edit an alternative name from a team it doesn't exist in"""
        team = create_team()
        alt_name = create_team_alternative_name()
        put_data = {'name': random_string()}
        url = '/v1/leagues/{}/teams/{}/alternative_names/{}'.format(
            team.league_id, team.id, alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_missing_name(self):
        """Edit an alternative name without a name"""
        alt_name = create_team_alternative_name()
        put_data = {}
        url = '/v1/leagues/{}/teams/{}/alternative_names/{}'.format(
            alt_name.team.league_id, alt_name.team_id, alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

class AlternativeNameDeleteTest(DeleteTestCase):
    def test_delete(self):
        """Test deleting team alternative names."""
        alt_name = create_team_alternative_name()
        other_team = create_team()
        other_league = create_league()
        self.assertSuccess('leagues', alt_name.team.league_id,
                           'teams', alt_name.team_id,
                           'alternative_names', alt_name.id)
        self.assertNotFound('leagues', alt_name.team.league_id,
                            'teams', alt_name.team_id,
                            'alternative_names', 'no_such_alt_name')
        self.assertNotFound('leagues', alt_name.team.league_id,
                            'teams', 'no_such_team',
                            'alternative_names', alt_name.id)
        self.assertNotFound('leagues', 'no_such_league',
                            'teams', alt_name.team_id,
                            'alternative_names', alt_name.id)
        self.assertNotFound('leagues', alt_name.team.league_id,
                            'teams', other_team.id,
                            'alternative_names', alt_name.id)
        self.assertNotFound('leagues', other_league.id,
                            'teams', alt_name.team_id,
                            'alternative_names', alt_name.id)
