from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from djblets.db.fields import JSONField

from reviewboard.site.models import LocalSite
from reviewboard.integrations.integration import get_integration


class ConfiguredIntegration(models.Model):
    integration_id = models.CharField(max_length=255)
    is_enabled = models.BooleanField(default=False)
    configuration = JSONField(blank=True)
    local_site = models.ForeignKey(LocalSite,
                                   related_name='integration_configurations',
                                   verbose_name=_('Local site'),
                                   blank=True,
                                   null=True)

    @property
    def integration(self):
        if not hasattr(self, '_integration'):
            cls = get_integration(self.integration_id)

            if cls:
                self._integration = cls(self)
            else:
                self._integration = None

        return self._integration

    def is_accessible_by(self, user):
        """Returns whether or not the user has access to the integration.

        The integration can be access by the user if it is set to global or if
        the user have access to the LocalSite.
        """
        return not self.local_site or self.local_site.is_accessible_by(user)

    def is_mutable_by(self, user):
        """Return whether or not the user can modify the configuration of
        the integration.

        The integration can be change by an administrator of the global site
        with the proper permission or the administrator of the LocalSite.
        """
        return True
