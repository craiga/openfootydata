import json
import re

from django.test import TestCase

from models.models import VenueAlternativeName
from .helpers import (create_venue_alternative_name,
                      create_venue,
                      random_string,
                      DeleteTestCase,
                      GetTestCase)


class VenueAlternativeNameTestCase:
    """Base class for all venue alternative name tests."""

    def assertVenueAlternativeName(self, json, alt_name):
        """
        Assert that the given parsed JSON data is the same as the given venue
        alternative name.
        """
        self.assertEqual(json['id'], alt_name.id)
        self.assertEqual(json['name'], alt_name.name)
        self.assertVenueAlternativeNameUrl(json['url'], alt_name)
        self.assertEqual(json['venue'], alt_name.venue_id)

    def assertVenueAlternativeNames(self, json, alt_names):
        """
        Assert that the given list of parsed JSON data is the same as the given
        list of alternative names.
        """
        self.assertEqual(len(json), len(alt_names))
        alt_names = {alt_name.id:alt_name for alt_name in alt_names}
        for json_item in json:
            self.assertVenueAlternativeName(json_item,
                                           alt_names[json_item['id']])
            del alt_names[json_item['id']]
        self.assertEqual(0, len(alt_names))

    def assertVenueAlternativeNameUrl(self, url, alt_name):
        """
        Assert that the given URL relates to the given venue alternative
        name.
        """
        url_regex = '/v1/venues/{}/alternative_names/{}$'.format(
            alt_name.venue_id, alt_name.id)
        self.assertRegex(url, url_regex)


class VenueAlternativeNameDetailTest(GetTestCase, VenueAlternativeNameTestCase):
    def test_alt_name_detail(self):
        """Get alternative name detail."""
        alt_name = create_venue_alternative_name()
        self.assertSuccess('venues', alt_name.venue_id,
                           'alternative_names', alt_name.id)
        json = self.assertJson()
        self.assertVenueAlternativeName(json, alt_name)

    def test_no_such_alternative_name(self):
        """Test when no alternative_name exists."""
        alt_name = create_venue_alternative_name()
        other_venue = create_venue()
        self.assertNotFound('venues', alt_name.venue_id,
                            'alternative_names', 'no_such_alt_name')
        self.assertNotFound('venues', 'no_such_venue',
                            'alternative_names', alt_name.id)
        self.assertNotFound('venues', other_venue.id,
                            'alternative_names', alt_name.id)


class AlternativeNameListTest(GetTestCase, VenueAlternativeNameTestCase):
    def test_list_alternative_names(self):
        """Get a list of alternative_names."""
        venue = create_venue(num_alternative_names=0)
        alt_names = (create_venue_alternative_name(venue),
                     create_venue_alternative_name(venue))
        other_venue_alt_name = create_venue_alternative_name()
        self.assertSuccess('venues', venue.id, 'alternative_names')
        json = self.assertJson()
        self.assertVenueAlternativeNames(json['results'], alt_names)

    def test_no_alternative_names_in_venue(self):
        """
        Get a list of alternative names when none exist in the given venue.
        """
        venue = create_venue(num_alternative_names=0)
        other_venue_alt_name = create_venue_alternative_name()
        self.assertSuccess('venues', venue.id, 'alternative_names')
        json = self.assertJson()
        self.assertEqual(len(json['results']), 0)

    def test_no_such_venue(self):
        """Test when no matching venue exists."""
        self.assertNotFound('venues', 'no_such_venue', 'alternative_names')

class AlternativeNameCreateTest(TestCase):
    def test_create_venue_alternative_name(self):
        """Create an alternative name."""
        venue = create_venue()
        post_data = {'name': random_string()}
        url = '/v1/venues/{}/alternative_names'.format(venue.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        url_regex = '/v1/venues/{}/alternative_names/(\d+)$'.format(venue.id)
        url_match = re.search(url_regex, response['Location'])
        self.assertIsNotNone(url_match)
        venue_id = int(url_match.group(1))
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], venue_id)
        self.assertEqual(response_data['name'], post_data['name'])
        self.assertEqual(response_data['venue'], venue.id)
        self.assertRegex(response_data['url'], url_regex)
        alternative_name = VenueAlternativeName.objects.get(pk=venue_id)
        self.assertEqual(alternative_name.name, post_data['name'])
        self.assertEqual(alternative_name.venue_id, venue.id)

    def test_missing_name(self):
        """Create an alternative name without a name"""
        venue = create_venue()
        post_data = {}
        url = '/v1/venues/{}/alternative_names'.format(venue.id)
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 400)

class AlternativeNameEditTest(TestCase):
    def test_edit_alternative_name(self):
        """Edit an alternative name"""
        alt_name = create_venue_alternative_name()
        put_data = {'name': random_string()}
        url = '/v1/venues/{}/alternative_names/{}'.format(alt_name.venue_id,
                                                          alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], alt_name.id)
        self.assertEqual(response_data['name'], put_data['name'])
        self.assertEqual(response_data['venue'], alt_name.venue_id)
        url_regex = r'/v1/venues/{}/alternative_names/{}$'.format(
            alt_name.venue_id, alt_name.id)
        self.assertRegex(response_data['url'], url_regex)
        alt_name.refresh_from_db()
        self.assertEqual(alt_name.name, put_data['name'])

    def test_no_such_alternative_name(self):
        """Edit a non-existent alternative name"""
        venue = create_venue()
        put_data = {'name': random_string()}
        url = '/v1/venues/{}/alternative_names/none'.format(venue.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_no_such_venue(self):
        """Edit an alternative name in a non-existent venue"""
        alt_name = create_venue_alternative_name()
        put_data = {'name': random_string()}
        url = '/v1/venues/none/alternative_names/{}'.format(alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_alt_name_not_in_venue(self):
        """Edit an alternative name from a venue it doesn't exist in"""
        venue = create_venue()
        alt_name = create_venue_alternative_name()
        put_data = {'name': random_string()}
        url = '/v1/venues/{}/alternative_names/{}'.format(venue.id, alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_missing_name(self):
        """Edit an alternative name without a name"""
        alt_name = create_venue_alternative_name()
        put_data = {}
        url = '/v1/venues/{}/alternative_names/{}'.format(alt_name.venue_id,
                                                          alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

class AlternativeNameDeleteTest(DeleteTestCase):
    def test_delete(self):
        """Test deleting venue alternative names."""
        alt_name = create_venue_alternative_name()
        other_venue = create_venue()
        self.assertSuccess('venues', alt_name.venue_id,
                           'alternative_names', alt_name.id)
        self.assertNotFound('venues', alt_name.venue_id,
                            'alternative_names', 'no_such_alt_name')
        self.assertNotFound('venues', 'no_such_venue',
                            'alternative_names', alt_name.id)
        self.assertNotFound('venues', other_venue.id,
                            'alternative_names', alt_name.id)
