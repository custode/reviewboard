from __future__ import unicode_literals

import logging


class Integration(object):
    """Base class for an intergration.

    Integration provided by an extension must be subclass of this
    class. This provides the setting for setting up, authenticating
    and shutting down of the integration.
    """

    # The unique identifier of the integration.
    #
    # This identifier will be use in retrieving and registering of the
    # integration, and thus will have to be unique among the integrations.
    integration_id = None

    # The display name of the integration.
    name = None

    # A short description on the functionalities of the integration.
    description = None

    # A flag that describe whether the integration is global.
    #
    # If this is set to True, the services provided by the integration will be
    # global, and no LocalSite configuration will be allowed.
    allows_localsites = False

    # A flag that describe whether the integrations support repositories.
    supports_repositories = False

    # A flag that describe whether the integration has to be authenticated.
    needs_authentication = False

    # The path for the icon file of the integration.
    #
    # The icon file should be placed in the "static" folder within the
    # extension package. The given path will then be the relative path of the
    # icon within the "static" folder.
    icon_path = None

    # The form class of the integration.
    #
    # The given form class should be a set class of the
    # IntegrationSettingsForm.
    form = None

    # The config template for the integration.
    #
    # The given template should extends IntegrationConfigTemplate.
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
        """Returns the authentication URL for the integration."""
        raise NotImplementedError


_integrations = {}


def register_integration(integration):
    """Register a given integration."""
    if integration.integration_id in _integrations:
        raise KeyError('"%s" is already a registered integration'
                       % integration.integration_id)

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
    """Return the list of integrations."""
    return list(_integrations.values())


def get_integration(integration_id):
    """Returns the integration with the given integration ID."""
    return _integrations.get(integration_id, None)
