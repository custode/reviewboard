from __future__ import unicode_literals

from djblets.siteconfig.forms import SiteSettingsForm


class IntegrationSettingsForm(SiteSettingsForm):
    """Settings form for integration configuration."""

    def __init__(self, config, *args, **kwargs):
        self.config = config
        self.configuration = config.integration.config

        super(IntegrationSettingsForm, self).__init__(self.configuration, *args, **kwargs)
