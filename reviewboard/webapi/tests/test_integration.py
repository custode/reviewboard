from __future__ import unicode_literals

from django.utils import six

from reviewboard.integrations.integration import (register_integration,
                                                  unregister_integration)
from reviewboard.integrations.manager import IntegrationManager
from reviewboard.integrations.tests import TestIntegration
from reviewboard.webapi.resources import resources
from reviewboard.webapi.tests.base import BaseWebAPITestCase
from reviewboard.webapi.tests.mimetypes import integration_list_mimetype
from reviewboard.webapi.tests.mixins import BasicTestsMetaclass
from reviewboard.webapi.tests.urls import get_integration_list_url


@six.add_metaclass(BasicTestsMetaclass)
class ResourceListTests(BaseWebAPITestCase):
    """Testing the IntegrationResource APIs."""

    fixtures = ['test_users']
    sample_api_url = 'integrations/'
    resource = resources.integration
    test_http_methods = ('GET',)

    @classmethod
    def setUpClass(cls):
        register_integration(TestIntegration)

    @classmethod
    def tearDownClass(cls):
        unregister_integration(TestIntegration)

    def compare_item(self, item_rsp, integration):
        self.assertEqual(item_rsp['integration_id'],
                         integration.integration_id)
        self.assertEqual(item_rsp['name'], integration.name)
        self.assertEqual(item_rsp['description'], integration.description)
        self.assertEqual(item_rsp['icon_path'], integration.icon_path)

    #
    # HTTP GET tests
    #

    def setup_basic_get_test(self, user, with_local_site, local_site_name,
                             populate_items):
        if populate_items:
            manager = IntegrationManager()
            items = manager.get_integrations()
        else:
            items = []

        return (get_integration_list_url(local_site_name),
                integration_list_mimetype, items)
