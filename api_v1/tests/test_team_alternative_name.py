import json
import re

from django.test import TestCase

from models.models import TeamAlternativeName
from .helpers import (create_team_alternative_name,
                      create_league,
                      create_team,
                      random_string)

class TeamAlternativeNameDetailTest(TestCase):
    def test_alt_name_detail(self):
        """Get alternative name detail."""
        alternative_name = create_team_alternative_name()
        url = '/v1/leagues/{}/teams/{}/alternative_names/{}'.format(
            alternative_name.team.league.id,
            alternative_name.team.id,
            alternative_name.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['id'], alternative_name.id)
        self.assertEqual(data['name'], alternative_name.name)
        url_regex = r'/v1/leagues/{}/teams/{}/alternative_names/{}$'.format(
            alternative_name.team.league.id,
            alternative_name.team.id,
            alternative_name.id)
        self.assertRegex(data['url'], url_regex)
        self.assertEqual(data['team'], alternative_name.team.id)

    def test_no_such_alternative_name(self):
        """Test when no alternative_name exists."""
        team = create_team()
        url = '/v1/leagues/{}/teams/{}/alternative_names/none'.format(
            team.league.id, team.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_no_such_team(self):
        """Test when no team exists."""
        alternative_name = create_team_alternative_name()
        url = '/v1/leagues/{}/teams/none/alternative_names/{}'.format(
            alternative_name.team.league.id, alternative_name.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_alt_name_not_in_team(self):
        """Test when alternative name not in team."""
        team = create_team()
        alternative_name = create_team_alternative_name()
        url = '/v1/leagues/{}/teams/{}/alternative_names/{}'.format(
            team.league.id, team.id, alternative_name.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class AlternativeNameListTest(TestCase):
    def test_list_alternative_names(self):
        """Get a list of alternative_names."""
        team = create_team(num_alternative_names=0)
        alt_name_1 = create_team_alternative_name(team)
        alt_name_2 = create_team_alternative_name(team)
        alt_name_3 = create_team_alternative_name()
        url = '/v1/leagues/{}/teams/{}/alternative_names'.format(team.league.id,
                                                                 team.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 2)
        seen_alt_name_1 = False
        seen_alt_name_2 = False
        for alt_name in data['results']:
            if alt_name['id'] == alt_name_1.id:
                seen_alt_name_1 = True
                test_alt_name = alt_name_1
            else:
                seen_alt_name_2 = True
                test_alt_name = alt_name_2
            self.assertEqual(alt_name['id'], test_alt_name.id)
            self.assertEqual(alt_name['name'], test_alt_name.name)
            url_regex = r'/v1/leagues/{}/teams/{}/alternative_names/{}$'.format(
                test_alt_name.team.league.id,
                test_alt_name.team.id,
                test_alt_name.id)
            self.assertRegex(alt_name['url'], url_regex)
            self.assertEqual(alt_name['team'], test_alt_name.team.id)
        self.assertTrue(seen_alt_name_1)
        self.assertTrue(seen_alt_name_2)

    def test_no_alternative_names_in_team(self):
        """Get a list of alternative names when none exist in the given
        team.
        """
        team1 = create_team()
        team2 = create_team(num_alternative_names=0)
        url = '/v1/leagues/{}/teams/{}/alternative_names'.format(
            team2.league.id, team2.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 0)

    def test_no_such_team(self):
        """Test when no matching team exists."""
        league = create_league()
        url = '/v1/leagues/{}/teams/none/alternative_names'.format(league.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class AlternativeNameCreateTest(TestCase):
    def test_create_team_alternative_name(self):
        """Create an alternative name."""
        team = create_team()
        post_data = {'name': random_string()}
        url = '/v1/leagues/{}/teams/{}/alternative_names'.format(
            team.league.id, team.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        url_regex = '/v1/leagues/{}/teams/{}/alternative_names/(\d+)$'.format(
            team.league.id, team.id)
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
        self.assertEqual(alternative_name.team.id, team.id)

    def test_missing_name(self):
        """Create an alternative name without a name"""
        team = create_team()
        post_data = {}
        url = '/v1/leagues/{}/teams/{}/alternative_names'.format(
            team.league.id, team.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

class AlternativeNameEditTest(TestCase):
    def test_edit_alternative_name(self):
        """Edit an alternative name"""
        alt_name = create_team_alternative_name()
        put_data = {'name': random_string()}
        url = '/v1/leagues/{}/teams/{}/alternative_names/{}'.format(
            alt_name.team.league.id, alt_name.team.id, alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], alt_name.id)
        self.assertEqual(response_data['name'], put_data['name'])
        self.assertEqual(response_data['team'], alt_name.team.id)
        url_regex = r'/v1/leagues/{}/teams/{}/alternative_names/{}$'.format(
            alt_name.team.league.id, alt_name.team.id, alt_name.id)
        self.assertRegex(response_data['url'], url_regex)
        alt_name.refresh_from_db()
        self.assertEqual(alt_name.name, put_data['name'])

    def test_no_such_alternative_name(self):
        """Edit a non-existent alternative name"""
        team = create_team()
        put_data = {'name': random_string()}
        url = '/v1/leagues/{}/teams/{}/alternative_names/none'.format(
            team.league.id, team.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_no_such_team(self):
        """Edit an alternative name in a non-existent team"""
        alt_name = create_team_alternative_name()
        put_data = {'name': random_string()}
        url = '/v1/leagues{}/teams/none/alternative_names/{}'.format(
            alt_name.team.league.id, alt_name.id)
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
            team.league.id, team.id, alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_missing_name(self):
        """Edit an alternative name without a name"""
        alt_name = create_team_alternative_name()
        put_data = {}
        url = '/v1/leagues/{}/teams/{}/alternative_names/{}'.format(
            alt_name.team.league.id, alt_name.team.id, alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

class AlternativeNameDeleteTest(TestCase):
    def test_delete_alternative_name(self):
        """Delete an alternative name"""
        alt_name = create_team_alternative_name()
        url = '/v1/leagues/{}/teams/{}/alternative_names/{}'.format(
            alt_name.team.league.id, alt_name.team.id, alt_name.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_no_such_alternative_name(self):
        """Delete a non-existent alternative name"""
        team = create_team()
        url = '/v1/leagues/{}/teams/{}/alternative_names/none'.format(
            team.league.id, team.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_no_such_team(self):
        """Delete an alternative name in a non-existent team"""
        alt_name = create_team_alternative_name()
        url = '/v1/leagues/{}/teams/none/alternative_names/{}'.format(
            alt_name.team.league.id, alt_name.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_alt_name_not_in_team(self):
        """Delete an alternative name from a team it doesn't exist in"""
        team = create_team()
        alt_name = create_team_alternative_name()
        url = '/v1/leagues/{}/teams/{}/alternative_names/{}'.format(
            team.league.id, team.id, alt_name.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
