from __future__ import unicode_literals

from reviewboard.integrations.integration import (Integration,
                                                  register_integration,
                                                  unregister_integration)
from reviewboard.integrations.models import ConfiguredIntegration
from reviewboard.integrations.manager import IntegrationManager
from reviewboard.testing.testcase import TestCase


class TestIntegration(Integration):
    integration_id = 'TestIntegration'

    def shutdown(self):
        pass


class IntegrationManagerTest(TestCase):
    """Testing Integration Manager."""

    def create_configured_integration(self, integration_id="TestIntegration",
                                      is_enabled=False,
                                      configuration={},
                                      description="Test description",
                                      local_site=None):
        """Creates a configured integration for testing.

        The configured integration is populated with the default data that can
        be overridden by the caller. It may optionally be attached to a
        LocalSite.
        """
        return ConfiguredIntegration.objects.create(
            integration_id=integration_id,
            is_enabled=is_enabled,
            configuration={},
            description=description,
            local_site=local_site
            )

    def setUp(self):
        register_integration(TestIntegration)
        self.manager = IntegrationManager()

    def tearDown(self):
        super(IntegrationManagerTest, self).tearDown()
        unregister_integration(TestIntegration)

    def test_start_with_existing_configs(self):
        """Testing integration manager initializing with existing configured
        integrations."""
        config1 = self.create_configured_integration()
        config2 = self.create_configured_integration(is_enabled=True)
        self.manager.register_config(config1)
        self.manager.register_config(config2)

        configs = self.manager.get_config_instances()
        config = ConfiguredIntegration.objects.get(pk=1)

        self.assertEqual(len(configs), 2)
        self.assertIn(config, configs)

    def test_start_with_empty_configs(self):
        """Testing integration manager initializing with no configured
        integrations."""
        configs = self.manager.get_config_instances()
        self.assertEqual(len(configs), 0)

    def test_register_duplicate_config(self):
        """Testing integration manager registering duplicate configured
        integration."""
        config1 = self.create_configured_integration()
        self.manager.register_config(config1)

        self.assertRaises(KeyError, self.manager.register_config, config1)

    def test_register_duplicate_config_with_reregister(self):
        """Testing integration manager updating registered configured
        integration."""
        config1 = self.create_configured_integration()
        config2 = self.create_configured_integration(is_enabled=True)
        self.manager.register_config(config1)
        self.manager.register_config(config2)
        self.manager.update_config(1)

        self.assertEqual(len(self.manager.get_config_instances()), 2)

    def test_unregister_exisiting_config(self):
        """Testing integration manager unregistering registered configured
        integration."""
        config1 = self.create_configured_integration()
        config2 = self.create_configured_integration(is_enabled=True)
        self.manager.register_config(config1)
        self.manager.register_config(config2)

        self.manager.unregister_config(1)

        self.assertEqual(len(self.manager.get_config_instances()), 1)
        self.assertNotIn(config1, self.manager.get_config_instances())

    def test_unregister_non_existent_config(self):
        """Testing integration manager unregistering nonexistent configured
        integration."""
        self.assertRaises(KeyError, self.manager.unregister_config, 3)

    def test_toggle_config(self):
        """Testing integration manager toggling of configured integration."""
        config1 = self.create_configured_integration()
        self.manager.register_config(config1)

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
