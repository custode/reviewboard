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
    if request.method == 'POST':
        if 'full-reload' in request.POST:
            # Reload both extension manager and integration manager
            return HttpResponseRedirect('.')
    else:
        # manager.load()
        return render_to_response(template_name, RequestContext(request))


@csrf_protect
@staff_member_required
def configure_integration(request, form_class,
                          template_name='integrations/configure_integration.html'):
    pass
