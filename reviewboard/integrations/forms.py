from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from djblets.siteconfig.forms import SiteSettingsForm


class IntegrationSettingsForm(SiteSettingsForm):
    """Settings form for integration configuration.

    A base form for loading/saving configuration for an integration.
    Integration should subclass this form to provide custom configuration page.
    The description field should be added to the meta's fieldsets if the
    integration allows the user to provide their own description for each
    ConfiguredIntegration.
    """

    description = forms.CharField(
        label=_('Description'),
        required=False,
        help_text=_('The optional description for the integration.'),
        widget=forms.TextInput(attrs={
            'size': 40,
        }))

    def __init__(self, config, *args, **kwargs):
        self.config = config
        self.configuration = config.integration.config

        super(IntegrationSettingsForm, self).__init__(self.configuration,
                                                      *args, **kwargs)
