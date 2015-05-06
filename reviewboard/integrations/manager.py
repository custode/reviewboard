from __future__ import unicode_literals

import logging

from six import itervalues

from reviewboard.integrations.models import ConfiguredIntegration


class IntegrationManager(object):
    """A manager for all integrations."""

    def __init__(self):
        self._config_instances = {}
        self._load_configs()

    def initialize_config(self, config_id):
        """Register the configured integration.

        Look for the config instance and do a proper initialization on its
        integration instance.
        """
        config = self.get_config_instance(config_id)

        if config.integration and config.is_enabled:
            config.integration.shutdown()
            config.integration.local_site = config.local_site
            config.integration.initialize()

    def shutdown_config(self, config_id):
        """Unregister the configured integration.

        Look for the config instance and do a proper shutdown on its
        integration instance.
        """
        config_instance = self.get_config_instance(config_id)

        if config_instance.integration:
            config_instance.integration.shutdown()

    def reload_config(self, config):
        """Update the configured integration."""
        self._config_instances[config.pk] = config

        if config.is_enabled:
            self.initialize_config(config.pk)
        else:
            self.shutdown_config(config.pk)

    def delete_config(self, config_id):
        """Delete the configurated integration.

        Shutdown the config before deleting the configured integration.
        """
        self.shutdown_config(config_id)
        ConfiguredIntegration.objects.filter(pk=config_id).delete()

        try:
            del self._config_instances[config_id]
        except:
            logging.error("Config instance %s was already deleted" % config_id)

    def disable_config(self, config_id):
        """Disable a configured integration."""
        self._toggle_config(config_id, False)

    def enable_config(self, config_id):
        """Enable a configured integration."""
        self._toggle_config(config_id, True)

    def create_config(self, config):
        """Create a new configured integration."""
        config.save()
        self.reload_config(config)

    def get_config_instances(self, integration_id=None):
        """Returns all configured integration instances.

        If an optional ``integration_id`` parameter is given, only instances
        belonging to paramter will be returned.
        """
        configs = itervalues(self._config_instances)

        if integration_id:
            configs = filter(lambda config: config.integration_id ==
                             integration_id, configs)

        return list(configs)

    def get_config_instance(self, config_id):
        """Returns the specfic configured integration instance."""
        try:
            return self._config_instances[config_id]
        except (KeyError, AttributeError):
            raise KeyError('This configuration is not registered.')

    def _load_configs(self):
        """Load and cache all configured integrations."""
        configs = ConfiguredIntegration.objects.all()

        for config in configs:
            self._config_instances[config.pk] = config

    def _toggle_config(self, config_id, is_enabled):
        """Toggle a configured integration.

        Update the configuration of configured integration object and
        the state of its integration instance.
        """
        config = self.get_config_instance(config_id)
        config.is_enabled = is_enabled
        config.save(update_fields=['is_enabled'])

        self.reload_config(config)


_integration_manager = None


def get_integration_manager():
    """Returns the integration manager.

    Instead of creating an integration manager directly, this method should be
    called to ensure that there is only one instance of the manager.
    """
    global _integration_manager

    if not _integration_manager:
        _integration_manager = IntegrationManager()

    return _integration_manager
