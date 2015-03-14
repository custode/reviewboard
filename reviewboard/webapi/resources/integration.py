from __future__ import unicode_literals

from djblets.webapi.decorators import webapi_login_required
from djblets.webapi.core import WebAPIResponse

from django.core.urlresolvers import reverse
from django.contrib.staticfiles.templatetags.staticfiles import static

from reviewboard.integrations.manager import get_integration_manager
from reviewboard.webapi.base import WebAPIResource


class IntegrationResource(WebAPIResource):
    """Provides information on Integration resources."""

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
            'description': 'The url for the icon.'
        },
        'new_link': {
            'type': str,
            'description': "The url for adding new integration."
        }
    }

    allowed_methods = ('GET')

    def __init__(self, integration_manager):
        super(IntegrationResource, self).__init__()
        self._integration_manager = integration_manager

    def serialize_icon_path_field(self, integration, *args, **kwargs):
        if not integration.extension or not integration.icon_path:
            return None
        else:
            return static('ext/%s/%s' % (integration.extension.id,
                                         integration.icon_path))

    def serialize_new_link_field(self, integration, *args, **kwargs):
        if not integration:
            return None
        else:
            return reverse('new-integration',
                           args=(integration.integration_id,))

    def has_access_permissions(self, *args, **kwargs):
        return True

    def has_list_access_permission(self, *args, **kwargs):
        return True

    @webapi_login_required
    def get_list(self, request, *args, **kwargs):
        data = list(map(lambda obj: self.serialize_object(obj, request=request), self._integration_manager.get_integrations()))

        return WebAPIResponse(request, {'integrations': data})

integration_resource = IntegrationResource(get_integration_manager())
