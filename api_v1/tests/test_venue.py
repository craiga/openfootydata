import json
from pprint import pprint

from django.test import TestCase

from models.models import Venue
from .helpers import create_venue, create_venue_alternative_name, random_string

class VenueDetailTest(TestCase):
    def test_venue_detail(self):
        """Get venue detail."""
        venue = create_venue()
        response = self.client.get('/v1/venues/{}'.format(venue.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['id'], venue.id)
        self.assertEqual(data['name'], venue.name)
        self.assertRegex(data['url'], '/v1/venues/{}$'.format(venue.id))
        self.assertEqual(set(data['alternative_names']),
                         {n.name for n in venue.alternative_names.all()})

    def test_no_alternative_names(self):
        """Get venue details with no alternative names."""
        venue = create_venue(num_alternative_names=0)
        response = self.client.get('/v1/venues/{}'.format(venue.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['id'], venue.id)
        self.assertEqual(data['name'], venue.name)
        self.assertRegex(data['url'], '/v1/venues/{}$'.format(venue.id))
        self.assertEqual(data['alternative_names'], [])

    def test_no_such_venue(self):
        """Test when no venue exists."""
        response = self.client.get('/v1/venues/no_such_venue')
        self.assertEqual(response.status_code, 404)

class VenueListTest(TestCase):
    def test_list_venues(self):
        """Get a list of venues."""
        venue1 = create_venue()
        venue2 = create_venue()
        response = self.client.get('/v1/venues')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 2)
        seen_venue1 = False
        seen_venue2 = False
        for venue in data['results']:
            if venue['id'] == venue1.id:
                seen_venue1 = True
                test_venue = venue1
            else:
                seen_venue2 = True
                test_venue = venue2
            self.assertEqual(venue['id'], test_venue.id)
            self.assertEqual(venue['name'], test_venue.name)
            url_regex = r'/v1/venues/{}$'.format(test_venue.id)
            self.assertRegex(venue['url'], url_regex)
            alt_names = {n.name for n in test_venue.alternative_names.all()}
            self.assertEqual(set(venue['alternative_names']), alt_names)
        self.assertTrue(seen_venue1)
        self.assertTrue(seen_venue2)

    def test_filter_venues(self):
        """Get a list of venues filtered by name."""
        venue1 = create_venue()
        venue2 = create_venue()
        response = self.client.get('/v1/venues?name=' + venue1.name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], venue1.id)
        self.assertEqual(data['results'][0]['name'], venue1.name)
        url_regex = r'/v1/venues/{}$'.format(venue1.id)
        self.assertRegex(data['results'][0]['url'], url_regex)
        self.assertEqual(set(data['results'][0]['alternative_names']),
                         {n.name for n in venue1.alternative_names.all()})
        response = self.client.get('/v1/venues?name=' + venue2.name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], venue2.id)
        self.assertEqual(data['results'][0]['name'], venue2.name)
        url_regex = r'/v1/venues/{}$'.format(venue2.id)
        self.assertRegex(data['results'][0]['url'], url_regex)
        self.assertEqual(set(data['results'][0]['alternative_names']),
                         {n.name for n in venue2.alternative_names.all()})

    def test_filter_venues_by_alternative_name(self):
        """Get a list of venues filtered by an alternative name."""
        venue1 = create_venue(num_alternative_names=2)
        venue2 = create_venue()
        response = self.client.get('/v1/venues?alternative_names__name=' \
            + venue1.alternative_names.all()[0].name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], venue1.id)
        self.assertEqual(data['results'][0]['name'], venue1.name)
        url_regex = r'/v1/venues/{}$'.format(venue1.id)
        self.assertRegex(data['results'][0]['url'], url_regex)
        self.assertEqual(set(data['results'][0]['alternative_names']),
                         {n.name for n in venue1.alternative_names.all()})

    def test_no_venues(self):
        """Get a list of venues when none exist."""
        response = self.client.get('/v1/venues')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 0)

class VenueCreateTest(TestCase):
    def test_create_venue(self):
        """Create a venue."""
        post_data = {'id': random_string(),
                     'name': random_string()}
        response = self.client.post('/v1/venues', post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        url_regex = r'/v1/venues/{}$'.format(post_data['id'])
        self.assertRegex(response['Location'], url_regex)
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], post_data['id'])
        self.assertEqual(response_data['name'], post_data['name'])
        self.assertRegex(response_data['url'], url_regex)
        self.assertEqual(response_data['alternative_names'], [])
        venue = Venue.objects.get(pk=post_data['id'])
        self.assertEqual(venue.id, post_data['id'])
        self.assertEqual(venue.name, post_data['name'])
        self.assertEqual(venue.alternative_names.count(), 0)

    def test_missing_id(self):
        """Create a venue without an ID"""
        response = self.client.post('/v1/venues', {'name': random_string()})
        self.assertEqual(response.status_code, 400)

    def test_invalid_id(self):
        """Create a venue with an invalid ID"""
        invalid_ids = ('', random_string(length=201), 'hello-world')
        for invalid_id in invalid_ids:
            post_data = {'id': invalid_id, 'name': random_string()}
            response = self.client.post('/v1/venues', post_data)
            self.assertEqual(response.status_code, 400)

    def test_existing_id(self):
        """Create a venue with an ID that alrady exists"""
        venue = create_venue()
        post_data = {'id': venue.id, 'name': random_string()}
        response = self.client.post('/v1/venues', post_data)
        self.assertEqual(response.status_code, 400)

    def test_missing_name(self):
        """Create a venue without a name"""
        response = self.client.post('/v1/venues', {'id': random_string()})
        self.assertEqual(response.status_code, 400)

class VenueEditTest(TestCase):
    def test_edit_venue(self):
        """Edit a venue"""
        venue = create_venue()
        put_data = {'id': venue.id, 'name': random_string()}
        response = self.client.put('/v1/venues/{}'.format(venue.id),
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], venue.id)
        self.assertEqual(response_data['name'], put_data['name'])
        url_regex = r'/v1/venues/{}$'.format(venue.id)
        self.assertRegex(response_data['url'], url_regex)
        self.assertEqual(set(response_data['alternative_names']),
                         {n.name for n in venue.alternative_names.all()})
        venue.refresh_from_db()
        self.assertEqual(venue.name, put_data['name'])

    def test_missing_name(self):
        """Edit a venue without a name"""
        venue = create_venue()
        put_data = {'id': venue.id}
        response = self.client.put('/v1/venues/{}'.format(venue.id),
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_no_such_venue(self):
        """Edit a non-existent venue"""
        put_data = {'id': random_string(), 'name': random_string()}
        response = self.client.put('/v1/venues/no_such_venue',
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

class VenueDeleteTest(TestCase):
    def test_delete_venue(self):
        """Delete a venue"""
        venue = create_venue()
        response = self.client.delete('/v1/venues/{}'.format(venue.id))
        self.assertEqual(response.status_code, 204)

    def test_no_such_venue(self):
        """Delete a non-existent venue"""
        response = self.client.delete('/v1/venues/no_such_venue')
        self.assertEqual(response.status_code, 404)
