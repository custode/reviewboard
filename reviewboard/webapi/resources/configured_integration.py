from __future__ import unicode_literals

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse

from djblets.util.decorators import augment_method_from
from djblets.webapi.decorators import (webapi_login_required,
                                       webapi_request_fields)
from djblets.webapi.errors import DOES_NOT_EXIST

from reviewboard.integrations.models import ConfiguredIntegration
from reviewboard.integrations.manager import get_integration_manager
from reviewboard.webapi.base import WebAPIResource


class ConfiguredIntegrationResource(WebAPIResource):
    """Provides information on configuredIntegration resources."""

    model = ConfiguredIntegration
    name = 'configured_integration'

    fields = {
        'id': {
            'type': int,
            'description': 'The numeric ID of the integration.'
        },
        'name': {
            'type': str,
            'description': 'The name of the integration this resource belongs.'
        },
        'integration_description': {
            'type': str,
            'description': 'The description of the integration class.'
        },
        'integration_id': {
            'type': str,
            'description': 'The integration type that the resource belongs to.'
        },
        'integration_icon': {
            'type': str,
            'description': 'The icon path for the integration.'
        },
        'description': {
            'type': str,
            'description': 'Optional description for this resource.'
        },
        'is_enabled': {
            'type': bool,
            'description': 'Whether or not the integration is enabled.'
        },
        'configuration': {
            'type': str,
            'description': 'The configuration of the integration.'
        },
        'configure_link': {
            'type': str,
            'description': 'The URL for configurating this resource'
        }
    }

    uri_object_key = 'integration_id'
    allowed_methods = ('GET', 'PUT', 'DELETE')

    def __init__(self, integration_manager):
        super(ConfiguredIntegrationResource, self).__init__()
        self._integration_manager = integration_manager

    def serialize_name_field(self, config, *args, **kwargs):
        if not config or not config.integration:
            return None
        else:
            return config.integration.name

    def serialize_integration_description_field(self, config, *args, **kwargs):
        if not config or not config.integration:
            return None
        else:
            return config.integration.description

    def serialize_integration_icon_field(self, config, *args, **kwargs):
        if not config or not config.integration:
            return None
        else:
            return static('ext/%s/%s' % (config.integration.extension.id,
                                         config.integration.icon_path))

    def serialize_configure_link_field(self, config, *args, **kwargs):
        if not config:
            return None
        else:
            return reverse('configure-integration', args=(config.pk,))

    def has_access_permissions(self, *args, **kwargs):
        return True

    def has_list_access_permissions(self, *args, **kwargs):
        return True

    def get_queryset(self, request, is_list=False, *args, **kwargs):
        """Returns a queryset for the configuredIntegration models.

        This will returns all the model object by default. However, it accepts
        additional query paramater "integrationID" to filter down the list
        for each integration class.
        """
        queryset = self.model.objects.all()

        if is_list:
            if 'integrationID' in request.GET:
                queryset = queryset.filter(
                    integration_id=request.GET.get('integrationID'))

        return queryset

    @webapi_login_required
    @augment_method_from(WebAPIResource)
    def get(self, request, *args, **kwargs):
        pass

    @webapi_login_required
    @augment_method_from(WebAPIResource)
    def get_list(self, request, *args, **kwargs):
        pass

    @webapi_login_required
    @webapi_request_fields(
        required={
            'enabled': {
                'type': bool,
                'description': 'Whether or not to make the extension active.'
            },
        },
    )
    def update(self, request, *args, **kwargs):
        """Update the state of the ConfiguredIntegration.

        This will enable or disable the ConfiguredIntegration instance
        with the initilize or shutdown method from the Integration class.
        """
        try:
            config = self.get_object(request, *args, **kwargs)
        except:
            return DOES_NOT_EXIST

        if kwargs.get('enabled'):
            self._integration_manager.enable_config(config.pk)
        else:
            self._integration_manager.disable_config(config.pk)

        config = ConfiguredIntegration.objects.get(pk=config.pk)

        return 200, {
            self.item_result_key: config
        }

    @webapi_login_required
    def delete(self, request, *args, **kwargs):
        """Handle DELETE of configured integration with integration manager.

        This is used to delete a configured integration object if the user
        has permissions to do so.
        """
        try:
            config = self.get_object(request, *args, **kwargs)
        except:
            return DOES_NOT_EXIST

        if not self.has_access_permissions(request, config, *args, **kwargs):
            return self.get_no_access_error(request, obj=config, *args,
                                            **kwargs)

        self._integration_manager.delete_config(config.pk)

        return 204, {}


configured_integration_resource = ConfiguredIntegrationResource(
    get_integration_manager())
