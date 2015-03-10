from __future__ import unicode_literals

from djblets.util.decorators import augment_method_from
from djblets.webapi.decorators import webapi_login_required
from djblets.webapi.core import WebAPIResponse

from reviewboard.webapi.base import WebAPIResource
from reviewboard.integrations.models import ConfiguredIntegration
from reviewboard.integrations.manager import get_integration_manager


class IntegrationResource(WebAPIResource):
    name = 'integration'

    fields = {
        'integration_id': {
            'type': str,
            'description': 'The unique id of the integration.'
        },
        'name': {
            'type': str,
            'description': 'The name of the integration.'
        },
        'description': {
            'type': str,
            'description': 'The description of the integration.'
        },
        'allows_localsites': {
            'type': bool,
            'description': 'Whether or not the integration can be configure\
                            for a local site individually'
        },
        'needs_authentication': {
            'type': bool,
            'description': 'If the integration need to be authenticate.'
        },
        'icon_path': {
            'type': str,
            'description': 'The url for the icon'
        },
        'form': {
            'type': str,
            'description': 'The default form for the integration'
        },
        'config_template': {
            'type': str,
            'description': 'The template for the configuration page of the\
                            integration'
        },
    }

    allowed_methods = ('GET')

    def __init__(self, integration_manager):
        super(IntegrationResource, self).__init__()
        self._integration_manager = integration_manager

    def has_access_permissions(self, *args, **kwargs):
        return True

    def has_list_access_permission(self, *args, **kwargs):
        return True

    @webapi_login_required
    def get_list(self, request, *args, **kwargs):
        data = list(map(lambda obj: self.serialize_object(obj, request=request), self._integration_manager.get_integrations()))

        return WebAPIResponse(request, {'integrations': data})

integration_resource = IntegrationResource(get_integration_manager())
