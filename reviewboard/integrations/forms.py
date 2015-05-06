from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from djblets.siteconfig.forms import SiteSettingsForm

from reviewboard.site.models import LocalSite


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

    local_site = forms.ModelChoiceField(
        label=_('Local Site'),
        queryset=LocalSite.objects,
        required=False,
        help_text=_('The name of the local site to receive review request'
                    'from.'))

    def __init__(self, config, *args, **kwargs):
        self.config = config
        self.configuration = config.integration.config

        blacklist = ('description', 'local_site')
        if hasattr(self.Meta, 'save_blacklist'):
            self.Meta.save_blacklist += blacklist
        else:
            self.Meta.save_blacklist = blacklist

        super(IntegrationSettingsForm, self).__init__(self.configuration,
                                                      *args, **kwargs)

    def load(self):
        """Load attributes from model and configuration."""
        super(IntegrationSettingsForm, self).load()

        self.fields['description'].initial = self.config.description

        if self.config.integration.allows_local_sites:
            self.fields['local_site'].initial = self.config.local_site

    def save(self):
        """Save attributes to model and configuration."""
        super(IntegrationSettingsForm, self).save()

        if not self.errors:
            self.config.description = self.cleaned_data['description']

            if self.config.integration.allows_local_sites:
                self.config.local_site = self.cleaned_data['local_site']

            self.config.save()
