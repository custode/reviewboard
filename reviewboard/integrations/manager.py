from __future__ import unicode_literals

import logging

from reviewboard.integrations.integration import (get_integrations,
                                                  get_integration)

from reviewboard.integrations.models import ConfiguredIntegration

class IntegrationManager(object):
    """A manager for all integrations."""
    def __init__(self):
        self._config_instances = {}

    def _initialize_configs(self):
        configs = ConfiguredIntegration.objects.all()

        for config in configs:
            self.register_config(config)

    def load(self):
        self._initialize_configs()

    def register_config(self, config, reregister=False):
        """Register the configured integration.

        If the item is already registered, reregister must be set to True in
        in order to change the config.
        """
        if config.id in self._config_instances and not reregister:
            raise KeyError('config "%s" is already a registered configured '
                           'integration' % config.id)
        else:
            if config.integration:
                self._config_instances[config.id] = config
            else:
                logging.error('Failed to register config with id "%s" due '
                              'to unknown integration "%s"'
                              % (config.id, config.integration_id))
                raise KeyError('"%s" is not a registered integration class'
                               % config.integration_id)

    def unregister_config(self, config_id):
        """Unregister the configured integration

        Look for the config instance and do a proper shutdown on its
        integration instance.
        """
        config_instance = self.get_config_instance(config_id)

        if not config_instance:
            raise KeyError('config with id "%s" is not a registered '
                           'configured integration' % config_id)

        # config_instance.integration.shutdown()
        del self._config_instances[config_instance.id]

    def update_config(self, config_id):
        """Update the configured integration"""
        config = ConfiguredIntegration.objects.get(pk=config_id)
        self.register_config(config, reregister=True)

    def delete_config(self, config_id):
        """Delete the configurated integration

        Unregister the config and do a proper shutdown before deleting.
        """
        if config_id in self._config_instances:
            self.unregister_config(config_id)
            ConfiguredIntegration.objects.get(pk=config_id).delete()
        else:
            raise KeyError('config with id "%s" is not a registered '
                           'configured integration' % config_id)

    def _toggle_config(self, config_id, is_enabled):
        """Toggle a configured integration

        Update the configured integration object and reregister it
        """
        config = ConfiguredIntegration.objects.get(pk=config_id)
        config.is_enabled = is_enabled
        config.save(update_fields=['is_enabled'])

        self.register_config(config, reregister=True)

    def disable_config(self, config_id):
        """Disable a configured integration"""
        self._toggle_config(config_id, False)

    def enable_config(self, config_id):
        """Enable a configured integration"""
        self._toggle_config(config_id, True)

    def get_integrations(self):
        """Return all registered integrations"""
        return get_integrations()

    def get_integration(self, integration_id):
        """Return the specific integration"""
        return get_integration(integration_id)

    def get_config_instances(self):
        """Return all configured integration instances"""
        return list(self._config_instances.values())

    def get_config_instance(self, config_id):
        """Return the specfic configured integration instance"""
        return self._config_instances.get(config_id, None)


_integration_manager = None


def get_integration_manager():
    global _integration_manager

    if not _integration_manager:
        _integration_manager = IntegrationManager()

    return _integration_manager
