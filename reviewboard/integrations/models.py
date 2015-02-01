from __future__ import unicode_literals

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from djblets.db.fields import JSONField

from reviewboard.site.models import LocalSite

class ConfiguredIntegration(models.Model):
    integration_id = models.CharField(max_length=255)
    description = models.CharField(blank=True)
    is_enabled = models.BooleanField(default=False)
    configuration = JSONField(blank=True)
    local_site = models.ForeignKey(LocalSite,
                                    related_name='integration_configurations',
                                    verbose_name=_('Local site'),
                                    blank=True,
                                    null=True)

    def is_accessible_by(self, user):
        # TODO: Implements permission
        return True

    def is_mutable_by(self, user):
        # TODO: Implements permission
        # return user.has_perm('integrations.change_configuredIntegration', self.local_site)
        return True