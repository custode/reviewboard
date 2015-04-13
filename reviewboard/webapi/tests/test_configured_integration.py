from __future__ import unicode_literals

from django.utils import six

from reviewboard.integrations.integration import (register_integration,
                                                  unregister_integration)
from reviewboard.integrations.manager import (get_integration_manager,
                                              IntegrationManager)
from reviewboard.integrations.models import ConfiguredIntegration
from reviewboard.integrations.tests import TestIntegration
from reviewboard.webapi.resources import resources
from reviewboard.webapi.tests.base import BaseWebAPITestCase
from reviewboard.webapi.tests.mimetypes import (
    configured_integration_item_mimetype,
    configured_integration_list_mimetype)
from reviewboard.webapi.tests.mixins import BasicTestsMetaclass
from reviewboard.webapi.tests.urls import (get_configured_integration_list_url,
                                           get_configured_integration_item_url)


@six.add_metaclass(BasicTestsMetaclass)
class ResourceListTests(BaseWebAPITestCase):
    """Testing the ConfiguredIntegrationResource APIs."""

    fixtures = ['test_users']
    sample_api_url = 'configured-integrations/'
    resource = resources.configured_integration
    test_http_methods = ('GET',)

    @classmethod
    def setUpClass(cls):
        register_integration(TestIntegration)

    @classmethod
    def tearDownClass(cls):
        unregister_integration(TestIntegration)

    def compare_item(self, item_rsp, config):
        self.assertEqual(item_rsp['id'], config.pk)
        self.assertEqual(item_rsp['integration_id'], config.integration_id)
        self.assertEqual(item_rsp['is_enabled'], config.is_enabled)
        self.assertEqual(item_rsp['description'], config.description)
        self.assertEqual(item_rsp['configuration'], config.configuration)

    #
    # HTTP GET tests
    #

    def setup_basic_get_test(self, user, with_local_site, local_site_name,
                             populate_items):
        config = self.create_configured_integration(
            integration_id='TestIntegration')

        if populate_items:
            manager = IntegrationManager()
            manager.register_config(config, reregister=True)
            items = manager.get_config_instances()
        else:
            items = []

        return (get_configured_integration_list_url(local_site_name),
                configured_integration_list_mimetype, items)


@six.add_metaclass(BasicTestsMetaclass)
class ResourceItemTests(BaseWebAPITestCase):
    """Testing the ConfiguredIntegration item APIs."""

    fixtures = ['test_users']
    sample_api_url = 'configured-integrations/<id>/'
    resource = resources.configured_integration
    basic_delete_use_admin = True
    basic_put_use_admin = True

    @classmethod
    def setUpClass(cls):
        register_integration(TestIntegration)

    @classmethod
    def tearDownClass(cls):
        unregister_integration(TestIntegration)

    def compare_item(self, item_rsp, config):
        self.assertEqual(item_rsp['id'], config.pk)
        self.assertEqual(item_rsp['integration_id'], config.integration_id)
        self.assertEqual(item_rsp['is_enabled'], config.is_enabled)
        self.assertEqual(item_rsp['description'], config.description)
        self.assertEqual(item_rsp['configuration'], config.configuration)

    def check_delete_result(self, user, config):
        manager = get_integration_manager()
        configs = manager.get_config_instances()
        self.assertNotIn(config, configs)

    def check_put_result(self, user, item_rsp, config):
        self.assertEqual(item_rsp['id'], config.pk)

        config = ConfiguredIntegration.objects.get(pk=config.pk)
        self.compare_item(item_rsp, config)

    #
    # HTTP GET tests
    #

    def setup_basic_get_test(self, user, with_local_site, local_site_name):
        config = self.create_configured_integration(
            integration_id='TestIntegration')

        return (get_configured_integration_item_url(config, local_site_name),
                configured_integration_item_mimetype, config)

    #
    # HTTP PUT tests
    #

    def setup_basic_put_test(self, user, with_local_site, local_site_name,
                             put_valid_data):
        if with_local_site:
            local_site = self.get_local_site(name=local_site_name)
        else:
            local_site = None

        config = self.create_configured_integration(
            integration_id='TestIntegration',
            local_site=local_site)

        return (get_configured_integration_item_url(config, local_site_name),
                configured_integration_item_mimetype,
                {'enabled': True},
                config, [])

    #
    # HTTP DELETE tests
    #

    def setup_basic_delete_test(self, user, with_local_site, local_site_name):
        if with_local_site:
            local_site = self.get_local_site(name=local_site_name)
        else:
            local_site = None

        config = self.create_configured_integration(
            integration_id='TestIntegration',
            local_site=local_site)
        manager = get_integration_manager()
        config.save()
        manager.register_config(config, True)

        return (get_configured_integration_item_url(config, local_site_name),
                [config])
