/*
This represent an integration model
*/
Integration = Backbone.Model.extend({
  defaults: {
    integrationID: null,
    name: null,
    description: null,
    iconPath: null,
    newLink: null
  },

  parse: function(rsp) {
    return {
      integrationID: rsp.integration_id,
      name: rsp.name,
      description: rsp.description,
      iconPath: rsp.icon_path,
      newLink: rsp.new_link
    };
  }
});

/*
This represent an configured integration model
*/
ConfiguredIntegration = Backbone.Model.extend({
  defaults: {
    id: null,
    name: null,
    integration: null,
    integrationDescription: null,
    integrationIcon: null,
    enabled: null,
    configuration: null
  },

  url: function() {
    return SITE_ROOT + 'api/configured-integrations/' + this.id + '/';
  },

  parse: function(rsp) {
    return {
      id: rsp.id,
      name: rsp.name,
      integration: rsp.integration_id,
      integrationDescription: rsp.integration_description,
      integrationIcon: rsp.integration_icon,
      description: rsp.description,
      enabled: rsp.is_enabled,
      configuration: rsp.configuration
    };
  }
});

IntegrationCollection = Backbone.Collection.extend({
  model: Integration,

  url: function() {
    return SITE_ROOT + 'api/integrations/';
  },

  parse: function(rsp) {
    return rsp.integrations;
  }
});

ConfiguredIntegrationCollection = Backbone.Collection.extend({
  model: ConfiguredIntegration,

  url: function() {
    return SITE_ROOT + 'api/configured-integrations/';
  },

  parse: function(rsp) {
    return rsp.configured_integrations;
  }
});

IntegrationManager = Backbone.Model.extend({
  initialize: function() {
    this.integrations = new IntegrationCollection();
  },

  load: function() {
    this.integrations.fetch({
      success: _.bind(function() {
        this.trigger('loaded');
      }, this)
    });
  }
});

ConfiguredIntegrationManager = Backbone.Model.extend({
  initialize: function() {
    this.configuredIntegrations = new ConfiguredIntegrationCollection();
  },

  load: function() {
    this.configuredIntegrations.fetch({
      success: _.bind(function() {
        this.trigger('loaded');
      }, this)
    });
  }
});