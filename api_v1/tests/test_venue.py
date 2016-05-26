import json
from decimal import Decimal

from django.test import TestCase

from models.models import Venue
from . import (create_venue,
               create_venue_alternative_name,
               random_string,
               random_decimal,
               DeleteTestCase,
               GetTestCase)


class VenueTestCase(TestCase):
    """Base class for venue tests."""

    def assertVenue(self, json, venue):
        """
        Assert that the given parsed venue JSON data is the same as the given
        venue.
        """
        self.assertEqual(json['id'], venue.id)
        self.assertEqual(json['name'], venue.name)
        self.assertEqual(Decimal(json['latitude']), venue.latitude)
        self.assertEqual(Decimal(json['longitude']), venue.longitude)
        self.assertEqual(json['timezone'], venue.timezone)
        self.assertVenueUrl(json['url'], venue)
        self.assertEqual(set(json['alternative_names']),
                         {n.name for n in venue.alternative_names.all()})

    def assertVenues(self, json, venues):
        """
        Assert that the given list of parsed venue JSON data is the same as
        the given list of venues.
        """
        self.assertEqual(len(json), len(venues))
        venues = {venue.id:venue for venue in venues}
        for json_item in json:
            self.assertVenue(json_item, venues[json_item['id']])
            del venues[json_item['id']]
        self.assertEqual(0, len(venues))


    def assertVenueUrl(self, url, venue):
        """Assert that the given URL relates to the given venue."""
        self.assertRegex(url, '/v1/venues/{}$'.format(venue.id))

class VenueDetailTest(GetTestCase, VenueTestCase):
    def test_venue_detail(self):
        """Get venue detail."""
        venues = (create_venue(), create_venue(num_alternative_names=0))
        for venue in venues:
            self.assertSuccess('venues', venue.id)
            json = self.assertJson()
            self.assertVenue(json, venue)

    def test_no_such_venue(self):
        """Test when no venue exists."""
        self.assertNotFound('venues', 'no_such_venue')


class VenueListTest(GetTestCase, VenueTestCase):
    def test_list_venues(self):
        """Get a list of venues."""
        venues = (create_venue(), create_venue())
        self.assertSuccess('venues')
        json = self.assertJson()
        self.assertVenues(json['results'], venues)

    def test_filter_venues(self):
        """Get a list of venues filtered by name."""
        venues = (create_venue(), create_venue())
        for venue in venues:
            self.assertSuccess('venues?name=' + venue.name)
            json = self.assertJson()
            self.assertVenues(json['results'], (venue,))
            self.assertGreater(venue.alternative_names.count(), 0)
            for alt_name in venue.alternative_names.all():
                self.assertSuccess(
                    'venues?alternative_names__name=' + alt_name.name)
                json = self.assertJson()
                self.assertVenues(json['results'], (venue,))

    def test_no_venues(self):
        """Get a list of venues when none exist."""
        self.assertSuccess('venues')
        json = self.assertJson()
        self.assertEqual(len(json['results']), 0)

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
