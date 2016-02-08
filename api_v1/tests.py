import json
import uuid
import random
import string
from pprint import pprint

from django.test import TestCase
from django.core import urlresolvers

from models import models

class LeagueDetailTest(TestCase):
    def test_league_detail(self):
        """Get league detail."""
        league = models.League(id='afl', name='Australian Football League')
        league.save()
        response = self.client.get('/v1/leagues/afl')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['id'], league.id)
        self.assertEqual(data['name'], league.name)
        self.assertRegex(data['url'], '/v1/leagues/afl$')

    def test_no_such_league(self):
        """Test when no league exists."""
        response = self.client.get('/v1/leagues/no_such_league')
        self.assertEqual(response.status_code, 404)

class LeagueListTest(TestCase):
    def test_list_leagues(self):
        """Get a list of leagues."""
        league1 = League(id='afl', name='Australian Football League')
        league1.save()
        league2 = League(id='vfl', name='Victorian Football League')
        league2.save()
        response = self.client.get('/v1/leagues')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 2)
        # TODO: Shouldn't rely on the ordering being as declared here.
        self.assertEqual(data['results'][0]['id'], 'afl')
        self.assertEqual(data['results'][0]['name'], league1.name)
        self.assertRegex(data['results'][0]['url'], '/v1/leagues/afl$')
        self.assertEqual(data['results'][1]['id'], 'vfl')
        self.assertEqual(data['results'][1]['name'], league2.name)
        self.assertRegex(data['results'][1]['url'], '/v1/leagues/vfl$')

    def test_no_leagues(self):
        """Get a list of leagues when none exist."""
        self.assertEqual(League.objects.all().count(), 0)
        response = self.client.get('/v1/leagues')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 0)

class LeagueCreateTest(TestCase):
    def test_create_league(self):
        """Create a league."""
        post_data = {'id': 'AFL', 'name': 'Australian Football League'}
        response = self.client.post('/v1/leagues', post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertRegex(response['Location'], '/v1/leagues/AFL$')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], 'AFL')
        self.assertEqual(response_data['name'], 'Australian Football League')
        self.assertRegex(response_data['url'], '/v1/leagues/AFL$')
        league = models.League.objects.get(pk='AFL')
        self.assertEqual(league.id, 'AFL')
        self.assertEqual(league.name, 'Australian Football League')

    def test_missing_id(self):
        """Create a league without an ID"""
        response = self.client.post('/v1/leagues', {'name': 'blah'})
        self.assertEqual(response.status_code, 400)

    def test_invalid_id(self):
        """Create a league with an invalid ID"""
        response = self.client.post('/v1/leagues', {'id': '', 'name': 'blah'})
        self.assertEqual(response.status_code, 400)
        invalid_post_data = {'id': 'x' * 201, 'name': 'blah'}
        response = self.client.post('/v1/leagues', invalid_post_data)
        self.assertEqual(response.status_code, 400)

    def test_existing_id(self):
        """Create a league with an ID that alrady exists"""
        league = models.League(id='AFL', name='Australian Football League')
        league.save()
        post_data = {'id': 'AFL', 'name': 'Australian Football League'}
        response = self.client.post('/v1/leagues', post_data)
        self.assertEqual(response.status_code, 400)

    def test_missing_name(self):
        """Create a league without a name"""
        response = self.client.post('/v1/leagues', {'id': 'blah'})
        self.assertEqual(response.status_code, 400)

class LeagueEditTest(TestCase):
    def test_edit_league(self):
        """Edit a league"""
        league = models.League(id='AFL', name='Always Failing Law')
        league.save()
        put_data = {'id': 'AFL', 'name': 'Australian Football League'}
        response = self.client.put('/v1/leagues/AFL',
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], 'AFL')
        self.assertEqual(response_data['name'], 'Australian Football League')
        self.assertRegex(response_data['url'], '/v1/leagues/AFL$')
        league.refresh_from_db()
        self.assertEqual(league.id, 'AFL')
        self.assertEqual(league.name, 'Australian Football League')

    def test_missing_name(self):
        """Edit a league without a name"""
        league = models.League(id='AFL', name='Always Failing Law')
        league.save()
        put_data = {'id': 'AFL'}
        response = self.client.put('/v1/leagues/AFL',
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_no_such_league(self):
        """Edit a non-existent league"""
        put_data = {'id': 'AFL', 'name': 'Australian Football League'}
        response = self.client.put('/v1/leagues/no_such_league',
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

class LeagueDeleteTest(TestCase):
    def test_delete_league(self):
        """Delete a league"""
        league = models.League(id='AFL', name='Always Failing Law')
        league.save()
        response = self.client.delete('/v1/leagues/AFL')
        self.assertEqual(response.status_code, 204)

    def test_no_such_league(self):
        """Delete a non-existent league"""
        response = self.client.delete('/v1/leagues/no_such_league')
        self.assertEqual(response.status_code, 404)

class TeamDetailTest(TestCase):
    def test_team_detail(self):
        """Get team detail."""
        league = models.League(id='afl', name='Australian Football League')
        league.save()
        team = models.Team(id='western-bulldogs',
                           league=league,
                           name='Western Bulldogs',
                           primary_colour='red',
                           secondary_colour='white',
                           tertiary_colour='blue')
        team.save()
        response = self.client.get('/v1/leagues/afl/teams/western-bulldogs')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['id'], team.id)
        self.assertEqual(data['name'], team.name)
        self.fail('incomplete test')
        self.assertRegex(data['url'], '/v1/teams/afl$')

    def test_no_such_team(self):
        """Test when no team exists."""
        self.fail('no test')
        response = self.client.get('/v1/teams/no_such_team')
        self.assertEqual(response.status_code, 404)

    def test_no_such_league(self):
        """Test when no league exists."""
        self.fail('no test')
        response = self.client.get('/v1/teams/no_such_team')
        self.assertEqual(response.status_code, 404)

    def test_team_not_in_league(self):
        """Test when team not in league."""
        self.fail('no test')

class TeamListTest(TestCase):
    def test_list_teams(self):
        """Get a list of teams."""
        league = create_league()
        league.save()
        team1 = create_team(league)
        team1.save()
        team2 = create_team(league)
        team2.save()
        team3 = create_team()
        team3.save()
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
            # self.assertRegex(team['url'],
            #                  '/v1/leagues/afl/teams/north-melbourne$')
        self.assertTrue(seen_team1)
        self.assertTrue(seen_team2)

    def test_no_teams_in_league(self):
        """Get a list of teams when none exist in the given league."""
        league1 = create_league()
        league1.save()
        team1 = create_team(league1)
        team1.save()
        team2 = create_team(league1)
        team2.save()
        league2 = create_league()
        league2.save()
        response = self.client.get('/v1/leagues/{}/teams'.format(league2.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 0)

    def test_no_such_league(self):
        """Test when no matching league exists."""
        response = self.client.get('/v1/leagues/no_such_league/teams')
        pprint(response.content)
        self.assertEqual(response.status_code, 404)

class TeamCreateTest(TestCase):
    def test_create_team(self):
        """Create a team."""
        post_data = {'id': 'AFL', 'name': 'Australian Football Team'}
        response = self.client.post('/v1/teams', post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertRegex(response['Location'], '/v1/teams/AFL$')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], 'AFL')
        self.assertEqual(response_data['name'], 'Australian Football Team')
        self.assertRegex(response_data['url'], '/v1/teams/AFL$')
        team = models.Team.objects.get(pk='AFL')
        self.assertEqual(team.id, 'AFL')
        self.assertEqual(team.name, 'Australian Football Team')

    def test_missing_id(self):
        """Create a team without an ID"""
        response = self.client.post('/v1/teams', {'name': 'blah'})
        self.assertEqual(response.status_code, 400)

    def test_invalid_id(self):
        """Create a team with an invalid ID"""
        response = self.client.post('/v1/teams', {'id': '', 'name': 'blah'})
        self.assertEqual(response.status_code, 400)
        invalid_post_data = {'id': 'x' * 201, 'name': 'blah'}
        response = self.client.post('/v1/teams', invalid_post_data)
        self.assertEqual(response.status_code, 400)

    def test_existing_id(self):
        """Create a team with an ID that alrady exists"""
        team = models.Team(id='AFL', name='Australian Football Team')
        league.save()
        post_data = {'id': 'AFL', 'name': 'Australian Football Team'}
        response = self.client.post('/v1/teams', post_data)
        self.assertEqual(response.status_code, 400)

    def test_missing_name(self):
        """Create a team without a name"""
        response = self.client.post('/v1/teams', {'id': 'blah'})
        self.assertEqual(response.status_code, 400)

class TeamEditTest(TestCase):
    def test_edit_team(self):
        """Edit a team"""
        team = models.Team(id='AFL', name='Always Failing Law')
        league.save()
        put_data = {'id': 'AFL', 'name': 'Australian Football Team'}
        response = self.client.put('/v1/teams/AFL',
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], 'AFL')
        self.assertEqual(response_data['name'], 'Australian Football Team')
        self.assertRegex(response_data['url'], '/v1/teams/AFL$')
        team.refresh_from_db()
        self.assertEqual(team.id, 'AFL')
        self.assertEqual(team.name, 'Australian Football Team')

    def test_missing_name(self):
        """Edit a team without a name"""
        team = models.Team(id='AFL', name='Always Failing Law')
        league.save()
        put_data = {'id': 'AFL'}
        response = self.client.put('/v1/teams/AFL',
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_no_such_team(self):
        """Edit a non-existent team"""
        put_data = {'id': 'AFL', 'name': 'Australian Football Team'}
        response = self.client.put('/v1/teams/no_such_team',
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

class TeamDeleteTest(TestCase):
    def test_delete_team(self):
        """Delete a team"""
        team = models.Team(id='AFL', name='Always Failing Law')
        league.save()
        response = self.client.delete('/v1/teams/AFL')
        self.assertEqual(response.status_code, 204)

    def test_no_such_team(self):
        """Delete a non-existent team"""
        response = self.client.delete('/v1/teams/no_such_team')
        self.assertEqual(response.status_code, 404)

def create_league():
    return models.League(id=random_string(),
                         name=random_string())

def create_team(league=None):
    if league is None:
        league = create_league()
    primary_colour = random_colour()
    secondary_colour = random_colour() if random.randint(0,1) else None
    tertiary_colour = random_colour() if random.randint(0,1) else None
    return models.Team(id=random_string(),
                       league=league,
                       name=random_string(),
                       primary_colour=primary_colour,
                       secondary_colour=secondary_colour,
                       tertiary_colour=tertiary_colour)

def random_string(length=5):
   return ''.join(random.choice(string.ascii_letters) for i in range(length))

def random_colour():
    return '#%02X%02X%02X' % (random.randint(0,255),
                              random.randint(0,255),
                              random.randint(0,255))
