from __future__ import unicode_literals

import logging


class Integration(object):
    """ An interface to third-party services"""

    integration_id = None
    name = None
    allows_localsites = False
    supports_repositories = False
    needs_authentication = False

    icon_path = None
    form = None
    config_template = None

    def __init__(self, config):
        self.integration_id = ".".join([self.__module__, self.__name__])
        self.config = config

    def shutdown(self):
        """
        Shut down the config and deregister all the services provided by the integration
        """
        raise NotImplementedError

    def get_authentication_url(self):
        """
        Return the authentication url for the integration
        """
        raise NotImplementedError

_integrations = {}


def register_integration(integration):
    """Register a given integration"""

    if integration.id in _integrations:
        raise KeyError('"%s" is already a registered integration' % integration.name)

    _integrations[integration.id] = integration


def unregister_integration(integration):
    """Deregister a given integration"""

    try:
        del _integrations[integration.id]
    except KeyError:
        logging.error('Failed to unregister unknown integration "%s"' % integration.name)
        raise KeyError('"%s" is not a registered integration' % integration.id)


def get_integrations():
    """Gets the list of integrations."""
    return _integrations.values()


def get_integration(idx):
    """Retrieves the integration with the given integration id"""
    return _integrations.get(idx, None)
