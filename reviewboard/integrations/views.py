from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from reviewboard.integrations.manager import get_integration_manager


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
    if config_id:
        config_instance = manager.get_config_instance(int(config_id))
        integration_class = config_instance.integration.integration_id

    if integration_class:
        integration = manager.get_integration(integration_class)

    if not integration:
        raise Http404
    else:
        form_class = integration.form

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
