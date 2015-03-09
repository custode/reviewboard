from __future__ import unicode_literals

from django.conf.urls import patterns, include
from django.core.exceptions import ObjectDoesNotExist
from djblets.util.decorators import augment_method_from
from djblets.webapi.decorators import webapi_login_required

from reviewboard.webapi.base import WebAPIResource
from reviewboard.integrations.models import ConfiguredIntegration
from reviewboard.integrations.manager import get_integration_manager


class IntegrationResource(WebAPIResource):
    model = ConfiguredIntegration
    name = 'integration'

    fields = {
        'id': {
            'type': int,
            'description': 'The numeric ID of the integration.'
        },
        'integration_id': {
            'type': str,
            'description': 'The integration type that the resource belongs to.'
        },
        'description': {
            'type': str,
            'description': 'The description of the integration.'
        },
        'is_enabled': {
            'type': bool,
            'description': 'Whether or not the integration is enabled.'
        },
        # TODO: Need to pretty format it with the template
        'configuration': {
            'type': str,
            'description': 'The configuration of the integration.'
        },
    }

    # Name clash with one of the attribute
    # Link to the attribute name in the url
    uri_object_key = 'integration_id'
    allowed_methods = ('GET', 'PUT')

    def __init__(self, integration_manager):
        super(IntegrationResource, self).__init__()
        self._integration_manager = integration_manager


    def has_access_permissions(self, *args, **kwargs):
        return True

    def has_list_access_permissions(self, *args, **kwargs):
        return True

    @webapi_login_required
    @augment_method_from(WebAPIResource)
    def get(self, *args, **kwargs):
        pass

    @webapi_login_required
    @augment_method_from(WebAPIResource)
    def get_list(self, *args, **kwargs):
        pass

integration_resource = IntegrationResource(get_integration_manager())
