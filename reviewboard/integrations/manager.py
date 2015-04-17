from __future__ import unicode_literals

from six import itervalues

from reviewboard.integrations.models import ConfiguredIntegration


class IntegrationManager(object):
    """A manager for all integrations."""

    def __init__(self):
        self._config_instances = {}
        self._initialize_configs()

    def load(self):
        self._initialize_configs()

    def register_config(self, config, reregister=False):
        """Register the configured integration.

        If the item is already registered, reregister must be set to True in
        in order to change the config.
        """
        if config.pk in self._config_instances and not reregister:
            raise KeyError('This configuration is already registered.')
        elif config.integration:
            self._config_instances[config.pk] = config

            if config.is_enabled:
                config.integration.initialize()
            else:
                config.integration.shutdown()

    def unregister_config(self, config_id):
        """Unregister the configured integration.

        Look for the config instance and do a proper shutdown on its
        integration instance.
        """
        config_instance = self.get_config_instance(config_id)

        try:
            del self._config_instances[config_instance.pk]
        except (KeyError, AttributeError):
            raise KeyError('This configuration is not registered.')

        if config_instance.integration:
            config_instance.integration.shutdown()

    def update_config(self, config_id):
        """Update the configured integration."""
        config = ConfiguredIntegration.objects.get(pk=config_id)
        self.register_config(config, reregister=True)

    def delete_config(self, config_id):
        """Delete the configurated integration.

        Unregister the config and do a proper shutdown before deleting.
        """
        if config_id in self._config_instances:
            self.unregister_config(config_id)
            ConfiguredIntegration.objects.filter(pk=config_id).delete()
        else:
            raise KeyError('This configuration is not registered.')

    def disable_config(self, config_id):
        """Disable a configured integration."""
        self._toggle_config(config_id, False)

    def enable_config(self, config_id):
        """Enable a configured integration."""
        self._toggle_config(config_id, True)

    def get_config_instances(self):
        """Returns all configured integration instances."""
        self._initialize_configs()
        return list(itervalues(self._config_instances))

    def get_config_instance(self, config_id):
        """Returns the specfic configured integration instance."""
        if config_id not in self._config_instances:
            self.register_config(ConfiguredIntegration.objects.get(
                pk=config_id))

        return self._config_instances.get(config_id)

    def _initialize_configs(self):
        for config in ConfiguredIntegration.objects.all():
            if config.pk not in self._config_instances:
                self.register_config(config)

    def _toggle_config(self, config_id, is_enabled):
        """Toggle a configured integration.

        Update the configured integration object and reregister it.
        """
        config = self.get_config_instance(config_id)
        config.is_enabled = is_enabled
        config.save(update_fields=['is_enabled'])

        self.register_config(config, reregister=True)


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
