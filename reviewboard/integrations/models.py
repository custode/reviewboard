from __future__ import unicode_literals

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from djblets.db.fields import JSONField

from reviewboard.integrations.integration import get_integration
from reviewboard.site.models import LocalSite


class ConfiguredIntegration(models.Model):
    """Configuration of an intgration."""

    integration_id = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    is_enabled = models.BooleanField(default=False)
    configuration = JSONField(blank=True)
    local_site = models.ForeignKey(LocalSite,
                                   related_name='integration_configurations',
                                   verbose_name=_('Local site'),
                                   blank=True,
                                   null=True)

    @cached_property
    def integration(self):
        """The integration instance for this configuration."""
        cls = get_integration(self.integration_id)

        if cls:
            return cls(self)
        else:
            return None

    def is_accessible_by(self, user):
        """Returns whether or not the user has access to the integration.

        The integration can be access by the user if it is set to global or if
        the user has access to the LocalSite.
        """
        return not self.local_site or self.local_site.is_accessible_by(user)

    def is_mutable_by(self, user):
        """Returns whether the user can modify this configuration.

        The integration can be change by an administrator of the global site
        with the proper permission or the administrator of the LocalSite.
        """
        pass
