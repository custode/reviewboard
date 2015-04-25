from __future__ import unicode_literals

from djblets.util.decorators import augment_method_from
from djblets.webapi.responses import WebAPIResponse

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse

from reviewboard.integrations.integration import get_integrations
from reviewboard.integrations.manager import get_integration_manager
from reviewboard.webapi.base import WebAPIResource


class IntegrationResource(WebAPIResource):
    """Provide information on a integration."""

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
        'allows_local_sites': {
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

    allowed_methods = ('GET',)

    def __init__(self):
        super(IntegrationResource, self).__init__()
        self._integration_manager = get_integration_manager()

    def serialize_icon_path_field(self, integration, *args, **kwargs):
        if not integration.static_path or not integration.icon_path:
            return None
        else:
            return static('ext/%s/%s' % (integration.static_path,
                                         integration.icon_path))

    def serialize_new_link_field(self, integration, *args, **kwargs):
        if not integration:
            return None
        else:
            return reverse('new-integration',
                           args=(integration.integration_id,))

    def get_queryset(self, request, is_list=False, local_site_name=None,
                     *args, **kwargs):
        return list(map(lambda obj:
                        self.serialize_object(obj, request=request),
                        get_integrations()))

    @augment_method_from(WebAPIResource)
    def get_list(self, request, *args, **kwargs):
        pass

    def _get_list_impl(self, request, *args, **kwargs):
        response_args = self.build_response_args(request)
        integrations = self.get_queryset(request, *args, **kwargs)

        return WebAPIResponse(request, {'integrations': integrations},
                              **response_args)


integration_resource = IntegrationResource()
