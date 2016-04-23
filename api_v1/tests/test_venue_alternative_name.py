import json
import re

from django.test import TestCase

from models.models import VenueAlternativeName
from .helpers import create_venue_alternative_name, create_venue, random_string

class VenueAlternativeNameDetailTest(TestCase):
    def test_alt_name_detail(self):
        """Get alternative name detail."""
        alternative_name = create_venue_alternative_name()
        url = '/v1/venues/{}/alternative_names/{}'.format(
            alternative_name.venue.id, alternative_name.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(data['id'], alternative_name.id)
        self.assertEqual(data['name'], alternative_name.name)
        url_regex = r'/v1/venues/{}/alternative_names/{}$'.format(
            alternative_name.venue.id, alternative_name.id)
        self.assertRegex(data['url'], url_regex)
        self.assertEqual(data['venue'], alternative_name.venue.id)

    def test_no_such_alternative_name(self):
        """Test when no alternative_name exists."""
        venue = create_venue()
        url = '/v1/venues/{}/alternative_names/none'.format(venue.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_no_such_venue(self):
        """Test when no venue exists."""
        alternative_name = create_venue_alternative_name()
        url = '/v1/venues/none/alternative_names/{}'.format(alternative_name.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_alt_name_not_in_venue(self):
        """Test when alternative name not in venue."""
        venue = create_venue()
        alternative_name = create_venue_alternative_name()
        url = '/v1/venues/{}/alternative_names/{}'.format(venue.id,
                                                          alternative_name.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class AlternativeNameListTest(TestCase):
    def test_list_alternative_names(self):
        """Get a list of alternative_names."""
        venue = create_venue()
        alt_name_1 = create_venue_alternative_name(venue)
        alt_name_2 = create_venue_alternative_name(venue)
        alt_name_3 = create_venue_alternative_name()
        response = self.client.get('/v1/venues/{}/alternative_names'.format(
            venue.id))
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
            url_regex = r'/v1/venues/{}/alternative_names/{}$'.format(
                test_alt_name.venue.id, test_alt_name.id)
            self.assertRegex(alt_name['url'], url_regex)
            self.assertEqual(alt_name['venue'], test_alt_name.venue.id)
        self.assertTrue(seen_alt_name_1)
        self.assertTrue(seen_alt_name_2)

    def test_no_alternative_names_in_venue(self):
        """Get a list of alternative names when none exist in the given
        venue.
        """
        venue1 = create_venue()
        alt_name_1 = create_venue_alternative_name(venue1)
        alt_name_2 = create_venue_alternative_name(venue1)
        venue2 = create_venue()
        response = self.client.get('/v1/venues/{}/alternative_names'.format(
            venue2.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content.decode(response.charset))
        self.assertEqual(len(data['results']), 0)

    def test_no_such_venue(self):
        """Test when no matching venue exists."""
        response = self.client.get('/v1/venues/no_such_venue/alternative_names')
        self.assertEqual(response.status_code, 404)

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
        self.assertEqual(alternative_name.venue.id, venue.id)

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
        url = '/v1/venues/{}/alternative_names/{}'.format(alt_name.venue.id,
                                                          alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content.decode(response.charset))
        self.assertEqual(response_data['id'], alt_name.id)
        self.assertEqual(response_data['name'], put_data['name'])
        self.assertEqual(response_data['venue'], alt_name.venue.id)
        url_regex = r'/v1/venues/{}/alternative_names/{}$'.format(
            alt_name.venue.id, alt_name.id)
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
        url = '/v1/venues/{}/alternative_names/{}'.format(alt_name.venue.id,
                                                          alt_name.id)
        response = self.client.put(url,
                                   json.dumps(put_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

class AlternativeNameDeleteTest(TestCase):
    def test_delete_alternative_name(self):
        """Delete an alternative name"""
        alt_name = create_venue_alternative_name()
        url = '/v1/venues/{}/alternative_names/{}'.format(alt_name.venue.id,
                                                          alt_name.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_no_such_alternative_name(self):
        """Delete a non-existent alternative name"""
        venue = create_venue()
        url = '/v1/venues/{}/alternative_names/none'.format(venue.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_no_such_venue(self):
        """Delete an alternative name in a non-existent venue"""
        alt_name = create_venue_alternative_name()
        url = '/v1/venues/none/alternative_names/{}'.format(alt_name.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_alt_name_not_in_venue(self):
        """Delete an alternative name from a venue it doesn't exist in"""
        venue = create_venue()
        alt_name = create_venue_alternative_name()
        url = '/v1/venues/{}/alternative_names/{}'.format(venue.id, alt_name.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
