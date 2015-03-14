from __future__ import unicode_literals

from django.contrib import admin

from reviewboard.integrations.models import ConfiguredIntegration


class ConfiguredIntegrationAdmin(admin.ModelAdmin):
    list_display = ('integration_id', 'description', 'is_enabled',)
    raw_id_fields = ('local_site',)


admin.site.register(ConfiguredIntegration, ConfiguredIntegrationAdmin)
