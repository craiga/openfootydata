import json
from pprint import pprint
import uuid

from django.test import TestCase

from models.models import League

class LeagueDetailTest(TestCase):
    def test_league_detail(self):
        """Get league detail."""
        league = League(id='afl', name='Australian Football League')
        league.save()
        response = self.client.get('/v1/leagues/afl')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['id'], league.id)
        self.assertEqual(data['name'], league.name)
        self.assertEqual(data['url'], '/v1/leagues/afl')

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
        self.assertEqual(len(data['leagues']), 2)
        self.assertEqual(data['leagues'][league1.id]['id'], league1.id)
        self.assertEqual(data['leagues'][league1.id]['name'], league1.name)
        self.assertEqual(data['leagues'][league1.id]['url'], '/v1/leagues/afl')
        self.assertEqual(data['leagues'][league2.id]['id'], league2.id)
        self.assertEqual(data['leagues'][league2.id]['name'], league2.name)
        self.assertEqual(data['leagues'][league2.id]['url'], '/v1/leagues/afl')

    def test_no_leagues(self):
        """Get a list of leagues when none exist."""
        self.assertEqual(League.objects.all().count(), 0)
        response = self.client.get('/v1/leagues')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['leagues']), 0)

    def test_pagination(self):
        """Test pagination."""
        for i in range(0, 30):
            league = League(id=uuid.uuid4(), name=uuid.uuid4())
            league.save()
        response = self.client.get('/v1/leagues')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['page_size'], 20)
        self.assertEqual(data['num_items'], 30)
        self.assertEqual(data['num_pages'], 2)
        self.assertEqual(len(data['leagues']), 20)

    def test_page_size(self):
        """Test setting page size."""
        for i in range(0, 30):
            league = League(id=uuid.uuid4(), name=uuid.uuid4())
            league.save()
        response = self.client.get('/v1/leagues?per_page=4')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['page_size'], 4)
        self.assertEqual(data['num_items'], 30)
        self.assertEqual(data['num_pages'], 8)
        self.assertEqual(len(data['leagues']), 4)

    def test_page_number(self):
        """Test setting page number."""
        for i in range(0, 30):
            league = League(id=uuid.uuid4(), name=uuid.uuid4())
            league.save()
        response = self.client.get('/v1/leagues?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['page'], 2)
        self.assertEqual(data['page_size'], 20)
        self.assertEqual(data['num_items'], 30)
        self.assertEqual(data['num_pages'], 2)
        self.assertEqual(len(data['leagues']), 10)
