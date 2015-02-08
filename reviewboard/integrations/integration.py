from __future__ import unicode_literals

import logging


class Integration(object):
    """Base class for an intergration.

    Integration provided by an extension must be subclass of this
    class. This provides the setting for setting up, authenticating
    and shutting down of the integration.
    """

    integration_id = None
    name = None
    allows_localsites = False
    supports_repositories = False
    needs_authentication = False

    icon_path = None
    form = None
    config_template = None

    def __init__(self, config):
        if not self.integration_id:
            self.integration_id = ".".join(
                [self.__module__, self.__class__.__name__])
        self.config = config

        self.initialize()

    def initialize(self):
        """Initialize the integration.

        This provides custom initialization for the subclass.
        """
        pass

    def shutdown(self):
        """Shut down the integration.

        Subclass should override this to shut down the config and
        deregister all the services provided by the integration.
        """
        raise NotImplementedError

    def get_authentication_url(self):
        """Return the authentication url for the integration."""
        raise NotImplementedError

_integrations = {}


def register_integration(integration):
    """Register a given integration."""

    if integration.integration_id in _integrations:
        raise KeyError('"%s" is already a registered integration'
                       % integration.name)

    _integrations[integration.integration_id] = integration


def unregister_integration(integration):
    """Unregister a given integration."""

    try:
        del _integrations[integration.integration_id]
    except KeyError:
        logging.error('Failed to unregister unknown integration'
                      ' "%s"' % integration.name)
        raise KeyError('"%s" is not a registered integration'
                       % integration.integration_id)


def get_integrations():
    """Gets the list of integrations."""
    return list(_integrations.values())


def get_integration(integration_id):
    """Retrieves the integration with the given integration id"""
    return _integrations.get(integration_id, None)
