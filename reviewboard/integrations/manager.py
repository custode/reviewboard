from __future__ import unicode_literals

import logging

from reviewboard.integrations.integration import (get_integrations,
                                                    get_integration)

from reviewboard.integrations.models import ConfiguredIntegration

from django.dispatch import receiver
from reviewboard.signals import initializing


class IntegrationManager(object):
    configs = {}

    def __init__(self):
        self.start()


    def _initialise_configs(self):
        configs = ConfiguredIntegration.objects.filter(is_enabled=True)

        for config in configs:
            self.register_config(config)

    def start(self):
        self._initialise_configs()

    def register_config(self, config):
        if config.id in self.configs:
            pass
        else:
            cls = get_integration(config.integration_id)
            if cls:
                self.configs[config.id] = cls(config)
            else:
                pass

    def unregister_config(self, config):
        try:
            del self.configs[config.id]
        except TypeError:
            logging()
            raise TypeError("")

    def edit_config(self, config):
        pass

    def remove_config(self, config):
        pass

_integration_manager = None

def get_integration_manager():
    global _integration_manager

    if not _integration_manager:
        _integration_manager = IntegrationManager()

    return _integration_manager
