import json
from decimal import Decimal

from django.test import TestCase

from models.models import Venue
from .helpers import (create_venue,
                      create_venue_alternative_name,
                      random_string,
                      random_decimal,
                      DeleteTestCase)

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
        self.assertEqual(Decimal(data['latitude']), venue.latitude)
        self.assertEqual(Decimal(data['longitude']), venue.longitude)
        self.assertEqual(data['timezone'], venue.timezone)
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
        self.assertEqual(data['alternative_names'], [])

    def test_no_such_venue(self):
        """Test when no venue exists."""
        response = self.client.get('/v1/venues/no_such_venue')
        self.assertEqual(response.status_code, 404)

class VenueListTest(TestCase):
    def test_list_venues(self):
        """Get a list of venues."""
        venue_1 = create_venue()
        venue_2 = create_venue()
        response = self.client.get('/v1/venues')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 2)
        seen_venue_1 = False
        seen_venue_2 = False
        for venue in data['results']:
            if venue['id'] == venue_1.id:
                seen_venue_1 = True
            else:
                seen_venue_2 = True
        self.assertTrue(seen_venue_1)
        self.assertTrue(seen_venue_2)

    def test_filter_venues(self):
        """Get a list of venues filtered by name."""
        venue_1 = create_venue()
        venue_2 = create_venue()
        response = self.client.get('/v1/venues?name=' + venue_1.name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], venue_1.id)
        response = self.client.get('/v1/venues?name=' + venue_2.name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], venue_2.id)

    def test_filter_venues_by_alternative_name(self):
        """Get a list of venues filtered by an alternative name."""
        venue_1 = create_venue(num_alternative_names=2)
        venue_2 = create_venue()
        response = self.client.get('/v1/venues?alternative_names__name=' \
            + venue_1.alternative_names.all()[0].name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['id'], venue_1.id)

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
                     'name': random_string(),
                     'latitude': str(random_latitude()),
                     'longitude': str(random_longitude())}
        response = self.client.post('/v1/venues', post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        url_regex = r'/v1/venues/{}$'.format(post_data['id'])
        self.assertRegex(response['Location'], url_regex)
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], post_data['id'])
        self.assertEqual(response_data['name'], post_data['name'])
        self.assertEqual(response_data['latitude'], post_data['latitude'])
        self.assertEqual(response_data['longitude'], post_data['longitude'])
        self.assertRegex(response_data['url'], url_regex)
        self.assertEqual(response_data['alternative_names'], [])
        venue = Venue.objects.get(pk=post_data['id'])
        self.assertEqual(venue.id, post_data['id'])
        self.assertEqual(venue.name, post_data['name'])
        self.assertEqual(venue.latitude, Decimal(post_data['latitude']))
        self.assertEqual(venue.longitude, Decimal(post_data['longitude']))
        self.assertEqual(venue.alternative_names.count(), 0)

    def test_missing_id(self):
        """Create a venue without an ID"""
        post_data = {'name': random_string(),
                     'latitude': str(random_latitude()),
                     'longitude': str(random_longitude())}
        response = self.client.post('/v1/venues', post_data)
        self.assertEqual(response.status_code, 400)

    def test_invalid_id(self):
        """Create a venue with an invalid ID"""
        invalid_ids = ('', random_string(length=201), 'hello-world')
        for invalid_id in invalid_ids:
            post_data = {'id': invalid_id,
                         'name': random_string(),
                         'latitude': str(random_latitude()),
                         'longitude': str(random_longitude())}
            response = self.client.post('/v1/venues', post_data)
            self.assertEqual(response.status_code, 400)

    def test_existing_id(self):
        """Create a venue with an ID that alrady exists"""
        venue = create_venue()
        post_data = {'id': venue.id,
                     'name': random_string(),
                     'latitude': str(random_latitude()),
                     'longitude': str(random_longitude())}
        response = self.client.post('/v1/venues', post_data)
        self.assertEqual(response.status_code, 400)

    def test_missing_name(self):
        """Create a venue without a name"""
        post_data = {'id': random_string(),
                     'latitude': str(random_latitude()),
                     'longitude': str(random_longitude())}
        response = self.client.post('/v1/venues', post_data)
        self.assertEqual(response.status_code, 400)

    def test_missing_latitude(self):
        """Test creating a venue without a latitude."""
        post_data = {'id': random_string(),
                     'name': random_string(),
                     'longitude': str(random_longitude())}
        response = self.client.post('/v1/venues', post_data)
        self.assertEqual(response.status_code, 400)

    def test_invalid_latitude(self):
        """Test creating a venue with an invalid latitude."""
        invalid_latitudes = ('',
                             None,
                             'hello-world',
                             str(random_decimal(min=90, max=91)),
                             str(random_decimal(min=-91, max=-90)),
                             str(random_decimal(min=-90, max=90, precision=7)))
        for invalid_latitude in invalid_latitudes:
            post_data = {'id': random_string(),
                         'name': random_string(),
                         'latitude': invalid_latitude,
                         'longitude': str(random_longitude())}
            response = self.client.post('/v1/venues', post_data)
            self.assertEqual(response.status_code, 400)

    def test_missing_longitude(self):
        """Test creating a venue without a longitude."""
        post_data = {'id': random_string(),
                     'name': random_string(),
                     'latitude': str(random_latitude())}
        response = self.client.post('/v1/venues', post_data)
        self.assertEqual(response.status_code, 400)

    def test_invalid_longitude(self):
        """Test creating a venue with an invalid longitude."""
        invalid_longitudes = ('',
                              None,
                              'hello-world',
                              str(random_decimal(min=180, max=181)),
                              str(random_decimal(min=-181, max=-180)),
                              str(random_decimal(min=-180,
                                                 max=180,
                                                 precision=7)))
        for invalid_longitude in invalid_longitudes:
            post_data = {'id': random_string(),
                         'name': random_string(),
                         'latitude': str(random_latitude()),
                         'longitude': invalid_longitude}
            response = self.client.post('/v1/venues', post_data)
            self.assertEqual(response.status_code, 400)

class VenueEditTest(TestCase):
    def test_edit_venue(self):
        """Edit a venue"""
        venue = create_venue()
        put_data = {'id': venue.id,
                    'name': random_string(),
                    'latitude': str(random_latitude()),
                    'longitude': str(random_longitude())}
        response = self.client.put('/v1/venues/{}'.format(venue.id),
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], venue.id)
        self.assertEqual(response_data['name'], put_data['name'])
        self.assertEqual(response_data['latitude'], put_data['latitude'])
        self.assertEqual(response_data['longitude'], put_data['longitude'])
        url_regex = r'/v1/venues/{}$'.format(venue.id)
        self.assertRegex(response_data['url'], url_regex)
        self.assertEqual(set(response_data['alternative_names']),
                         {n.name for n in venue.alternative_names.all()})
        venue.refresh_from_db()
        self.assertEqual(venue.name, put_data['name'])

    def test_missing_name(self):
        """Edit a venue without a name"""
        venue = create_venue()
        put_data = {'id': venue.id,
                    'latitude': str(random_latitude()),
                    'longitude': str(random_longitude())}
        response = self.client.put('/v1/venues/{}'.format(venue.id),
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_missing_latitude(self):
        """Test editing a venue without a latitude."""
        venue = create_venue()
        put_data = {'id': venue.id,
                    'name': random_string(),
                    'longitude': str(random_longitude())}
        response = self.client.put('/v1/venues/{}'.format(venue.id),
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_latitude(self):
        """Test editing a venue with an invalid latitude."""
        venue = create_venue()
        invalid_longitudes = ('',
                              None,
                              'hello-world',
                              str(random_decimal(min=180, max=181)),
                              str(random_decimal(min=-181, max=-180)),
                              str(random_decimal(min=-180,
                                                 max=180,
                                                 precision=7)))
        for invalid_longitude in invalid_longitudes:
            put_data = {'id': venue.id,
                        'name': random_string(),
                        'latitude': str(random_latitude()),
                        'longitude': invalid_longitude}
            response = self.client.put('/v1/venues/{}'.format(venue.id),
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_missing_longitude(self):
        """Test editing a venue without a longitude."""
        venue = create_venue()
        put_data = {'id': venue.id,
                    'name': random_string(),
                    'latitude': str(random_latitude())}
        response = self.client.put('/v1/venues/{}'.format(venue.id),
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_longitude(self):
        """Test editing a venue with an invalid longitude."""
        venue = create_venue()
        invalid_latitudes = ('',
                             None,
                             'hello-world',
                             str(random_decimal(min=90, max=91)),
                             str(random_decimal(min=-91, max=-90)),
                             str(random_decimal(min=-90, max=90, precision=7)))
        for invalid_latitude in invalid_latitudes:
            put_data = {'id': venue.id,
                        'name': random_string(),
                        'latitude': invalid_latitude,
                        'longitude': str(random_longitude())}
            response = self.client.put('/v1/venues/{}'.format(venue.id),
                                       json.dumps(put_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_no_such_venue(self):
        """Edit a non-existent venue"""
        put_data = {'id': random_string(),
                    'name': random_string(),
                    'latitude': str(random_latitude()),
                    'longitude': str(random_longitude())}
        response = self.client.put('/v1/venues/no_such_venue',
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

class VenueDeleteTest(DeleteTestCase):
    def test_delete(self):
        """Test deleting venues."""
        venue = create_venue()
        self.assertSuccess('venues', venue.id)
        self.assertNotFound('venues', 'no_such_venue')

def random_latitude():
    return random_decimal(min=-90, max=90, precision=6)

def random_longitude():
    return random_decimal(min=-180, max=180, precision=6)
