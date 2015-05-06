from __future__ import unicode_literals

import logging

from reviewboard.integrations.configurations import Configurations

class Integration(object):
    """Base class for an intergration.

    Integration provided by an extension must be subclass of this
    class. This provides the setting for setting up, authenticating
    and shutting down of the integration.
    """

    #: The unique identifier of the integration.
    #:
    #: This identifier will be use in retrieving and registering of the
    #: integration, and thus will have to be unique among the integrations.
    integration_id = None

    #: The display name of the integration.
    name = None

    #: A short description on the functionalities of the integration.
    description = None

    #: Flag is set to True if the integration allow LocalSite configuration.
    #:
    #: If this is set to False, the services provided by the integration will
    #: be global, and no LocalSite configuration will be allowed.
    allows_local_sites = False

    #: Flag is set to True if the integration support repositories.
    supports_repositories = False

    #: Flag is set to True if the integration needs authentication.
    needs_authentication = False

    #: The path for the icon file of the integration.
    #:
    #: The icon file should be placed in the "static" folder within the
    #: extension package. The given path will then be the relative path of the
    #: icon within the "static" folder.
    icon_path = None

    #: The form class of the integration.
    #:
    #: The given form class should be a subclass of the
    #: IntegrationSettingsForm.
    config_form = None

    #: The config template for the integration.
    #:
    #: The given template should extends IntegrationConfigTemplate.
    config_template = None

    # The default configurations for a new integration.
    default_configurations = {}

    def __init__(self, config):
        if not self.integration_id:
            self.integration_id = '%s.%s' % (
                [self.__module__, self.__class__.__name__])

        self.config = Configurations(config)
        self.hooks = set()

    def initialize(self):
        """Initialize the integration.

        This provides custom initialization for the subclass. All the processes
        that are required in initializing the service of the integration
        should be in this method. This will allow the integration to be toggled
        without the need to recreate a new instance of the object.
        """
        pass

    def shutdown(self):
        """Shut down the integration.

        Subclasses should override this to shut down the integration and
        deregister all the services provided by the integration. All the
        required processes should be in this method. This will allow the
        integration to be toggled without the need to recreate a new
        instance of the object.
        """
        self.shutdown_hooks()

    def shutdown_hooks(self):
        """Shuts down all hooks for the integration."""
        for hook in self.hooks:
            if hook.initialized:
                hook.shutdown()

        self.hooks = set()

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
    """Returns the list of integrations."""
    return list(_integrations.values())


def get_integration(integration_id):
    """Returns the integration with the given integration ID."""
    return _integrations.get(integration_id)
