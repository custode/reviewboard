from __future__ import unicode_literals

from djblets.testing.decorators import add_fixtures

from reviewboard.testing.testcase import TestCase
from reviewboard.integrations.models import ConfiguredIntegration
from reviewboard.integrations.integration import (Integration,
                                                  _integrations)
from reviewboard.integrations.manager import IntegrationManager


class TestIntegration(Integration):
    integration_id = 'TestIntegration'


class IntegrationManagerTest(TestCase):
    """Testing Integration Manager"""

    def setUp(self):
        _integrations['TestIntegration'] = TestIntegration
        self.manager = IntegrationManager()

    @add_fixtures(['test_configs'])
    def test_start_with_existing_configs(self):
        """
        Testing integration manager initializing with existing configured
        integrations"""
        configs = self.manager.get_config_instances()
        config = ConfiguredIntegration.objects.get(pk=1)

        self.assertEqual(len(configs), 2)
        self.assertIn(config, configs)

    def test_start_with_empty_configs(self):
        """
        Testing integration manager initializing with no configured
        integrations
        """
        configs = self.manager.get_config_instances()
        self.assertEqual(len(configs), 0)

    @add_fixtures(['test_configs'])
    def test_register_duplicate_config(self):
        """
        Testing integration manager registering duplicate configured
        integration
        """
        config = ConfiguredIntegration.objects.get(pk=1)
        self.assertRaises(KeyError, self.manager.register_config, config)

    @add_fixtures(['test_configs'])
    def test_register_duplicate_config_with_reregister(self):
        """
        Testing integration manager updating registered configured integration
        """
        self.manager.update_config(1)

        self.assertEqual(len(self.manager.get_config_instances()), 2)

    @add_fixtures(['test_configs'])
    def test_unregister_exisiting_config(self):
        """
        Testing integration manager unregistering registered configured
        integration
        """
        config = ConfiguredIntegration.objects.get(pk=1)
        self.manager.unregister_config(1)

        self.assertEqual(len(self.manager.get_config_instances()), 1)
        self.assertNotIn(config, self.manager.get_config_instances())

    @add_fixtures(['test_configs'])
    def test_unregister_non_existent_config(self):
        """
        Testing integration manager unregistering nonexistent configured
        integration
        """
        self.assertRaises(KeyError, self.manager.unregister_config, 3)

    @add_fixtures(['test_configs'])
    def test_toggle_config(self):
        """Testing integration manager toggling of configured integration"""

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
