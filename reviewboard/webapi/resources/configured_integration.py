from __future__ import unicode_literals

from django.contrib.staticfiles.templatetags.staticfiles import static

from djblets.util.decorators import augment_method_from
from djblets.webapi.decorators import webapi_login_required

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
    }

    uri_object_key = 'integration_id'
    allowed_methods = ('GET', 'PUT')

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


configured_integration_resource = ConfiguredIntegrationResource(
    get_integration_manager())
