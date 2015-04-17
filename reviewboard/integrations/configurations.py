from __future__ import unicode_literals

from django.utils.translation import ugettext as _


class Configurations(dict):
    """Setting data for integration."""

    def __init__(self, config):
        dict.__init__(self)
        self.config = config
        self.load()

    def __getitem__(self, key):
        """Retrieve an item from the dictionary.

        This will attempt to return a default value from
        integration.default_settings if the setting has not
        been set.
        """
        if super(Configurations, self).__contains__(key):
            return super(Configurations, self).__getitem__(key)

        if key in self.config.integration.default_configurations:
            return self.config.integration.default_configurations[key]

        raise KeyError(
            _('The settings key "%(key)s" was not found in integration')
            % {
                'key': key,
            })

    def __contains__(self, key):
        """Indicate if the setting is present.

        If the key is not present in the settings dictionary
        check the default settings as well.
        """
        if super(Configurations, self).__contains__(key):
            return True

        return key in self.config.integration.default_configurations

    def set(self, key, value):
        """Set a setting's value.

        This is equivalent to setting the value through standard dictionary
        attribute storage.
        """
        self[key] = value

    def load(self):
        """Load the settings from the database."""
        try:
            self.update(self.config.configuration)
        except ValueError:
            pass

    def save(self):
        """Save all current settings to the database."""
        self.config.configuration = dict(self)
        self.config.save()
