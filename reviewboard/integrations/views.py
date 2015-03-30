from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from reviewboard.integrations.manager import get_integration_manager
from reviewboard.integrations.models import ConfiguredIntegration


manager = get_integration_manager()


@csrf_protect
@staff_member_required
def integration_list(request,
                     template_name='integrations/integration_list.html'):
    return render_to_response(template_name, RequestContext(request))


@csrf_protect
@staff_member_required
def configure_integration(request, integration_class=None, config_id=None,
                          template_name='integrations/configure_integration'
                                        '.html'):
    if not integration_class:
        integration_class = manager.get_config_instance(
            int(config_id)).integration_id

    integration = manager.get_integration(integration_class)

    if config_id:
        config_instance = manager.get_config_instance(int(config_id))
    else:
        config_instance = ConfiguredIntegration(
            integration_id=integration_class,
            is_enabled=False,
            configuration=integration.default_configurations,
            description=integration.description,
            local_site=None)

    integration = manager.get_integration(integration_class)

    if not integration:
        raise Http404
    else:
        form_class = integration.form

    if request.method == 'POST':
        if not config_instance.pk:
            manager.create_config(config_instance)
            redirect_path = reverse('configure-integration',
                                    args=(config_instance.pk,))
        else:
            redirect_path = request.path + '?save=1'

        form = form_class(config_instance, request.POST, request.FILES)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(redirect_path)
    else:
        form = form_class(config_instance)

    return render_to_response(template_name, RequestContext(request, {
        'integration_name': integration.name,
        'form': form,
    }))
