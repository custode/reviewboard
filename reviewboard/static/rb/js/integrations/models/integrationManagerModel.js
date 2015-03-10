/*
This represent an integration model
*/
Integration = Backbone.Model.extend({
  defaults: {
/*
This represent an configured integration model
*/
ConfiguredIntegration = Backbone.Model.extend({
  defaults: {
    id: null,
    integration: null,
    enabled: null,
    configuration: null
  },

  url: function() {
    return SITE_ROOT + 'api/configured-integrations/' + this.id + '/';
  },

  parse: function(rsp) {
    return {
      id: rsp.id,
      integration: rsp.integration_id,
      enabled: rsp.is_enabled,
      configuration: rsp.configuration
    };
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