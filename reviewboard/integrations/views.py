from __future__ import unicode_literals

from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_protect

from reviewboard.integrations.integration import get_integration
from reviewboard.integrations.manager import get_integration_manager


manager = get_integration_manager()


@csrf_protect
@staff_member_required
def integration_list(request,
                     template_name='integrations/integration_list.html'):
    """Display a list of integrations class and its instances.

    This page handles both the creation and configuration of integration.
    """
    return render_to_response(template_name, RequestContext(request))


@csrf_protect
@staff_member_required
def configure_integration(request, integration_class=None, config_id=None,
                          template_name='integrations/configure_integration'
                                        '.html'):
    """Display the configuration of a single integration instance.

    This page handles the configuration of a specific integration instance.
    """
    integration = None

    if config_id:
        config_instance = manager.get_config_instance(int(config_id))
        integration_class = config_instance.integration.integration_id

    if integration_class:
        integration = get_integration(integration_class)

    if not integration:
        raise Http404
    else:
        form_class = integration.config_form

    if request.method == 'POST':
        form = form_class(integration, request.POST, request.FILES)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(request.path + '?save=1')
    else:
        form = form_class(integration, config=config_instance)

    return render_to_response(template_name, RequestContext(request, {
        'integration_name': integration.name,
        'form': form,
    }))
