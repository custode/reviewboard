from __future__ import unicode_literals

from reviewboard.extensions.base import Extension
from reviewboard.integrations.integration import (Integration,
                                                  register_integration,
                                                  unregister_integration)
from reviewboard.integrations.manager import IntegrationManager
from reviewboard.integrations.models import ConfiguredIntegration
from reviewboard.testing.testcase import TestCase


class TestExtension(Extension):
    id = 'TestExtension'


class TestIntegration(Integration):
    integration_id = 'TestIntegration'
    name = 'Test Integration'
    description = 'Add test integration for your review.'
    static_path = "test"
    extension = TestExtension

    def initialize(self):
        self.init = True

    def shutdown(self):
        self.init = False


class IntegrationManagerTest(TestCase):
    """Testing Integration Manager."""

    def setUp(self):
        register_integration(TestIntegration)
        self.manager = IntegrationManager()

    def tearDown(self):
        super(IntegrationManagerTest, self).tearDown()
        unregister_integration(TestIntegration)

    def test_start_with_existing_configs(self):
        """Testing integration manager initializing with existing configured
        integrations.
        """
        config1 = self.create_configured_integration(
            integration_id='TestIntegration',
        )
        config2 = self.create_configured_integration(
            integration_id='TestIntegration',
            is_enabled=True
        )
        self.manager.reload_config(config1)
        self.manager.reload_config(config2)

        configs = self.manager.get_config_instances()
        config = ConfiguredIntegration.objects.get(pk=1)

        self.assertEqual(len(configs), 2)
        self.assertIn(config, configs)

    def test_start_with_empty_configs(self):
        """Testing integration manager initializing with no configured
        integrations.
        """
        configs = self.manager.get_config_instances()
        self.assertEqual(len(configs), 0)

    def test_shutdown_unknown_config(self):
        """Testing integration manager unregistering nonexistent configured
        integration.
        """
        self.assertRaises(KeyError, self.manager.shutdown_config, 3)

    def test_delete_config(self):
        """Testing integration manager deleting configured integration."""
        config1 = self.create_configured_integration(
            integration_id='TestIntegration',
        )

        self.manager.reload_config(config1)
        self.manager.delete_config(1)

        configs = self.manager.get_config_instances()
        self.assertEqual(len(configs), 0)

    def test_delete_unknown_config(self):
        """Testing integration manager deleting unknown config"""
        self.assertRaises(KeyError, self.manager.delete_config, 3)

    def test_toggle_config(self):
        """Testing integration manager toggling of configured integration."""
        config1 = self.create_configured_integration(
            integration_id='TestIntegration'
        )
        self.manager.reload_config(config1)

        config = ConfiguredIntegration.objects.get(pk=1)
        self.assertFalse(config.is_enabled)

        self.manager._toggle_config(1, True)
        config = ConfiguredIntegration.objects.get(pk=1)
        self.assertTrue(config.is_enabled)
        self.assertTrue(self.manager.get_config_instance(1).is_enabled)

        self.manager._toggle_config(1, False)
        config = ConfiguredIntegration.objects.get(pk=1)
        self.assertFalse(config.is_enabled)
        self.assertFalse(self.manager.get_config_instance(1).is_enabled)
