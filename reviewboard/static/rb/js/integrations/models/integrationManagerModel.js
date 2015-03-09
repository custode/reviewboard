/*
This represent an integration model
*/
Integration = Backbone.Model.extend({
  defaults: {
    id: null,
    integration: null,
    enabled: null,
    description: null,
    configuration: null
  },

  url: function() {
    return SITE_ROOT + 'api/integrations/' + this.id + '/';
  },

  parse: function(rsp) {
    return {
      id: rsp.id,
      integration: rsp.integration_id,
      enabled: rsp.is_enabled,
      description: rsp.description,
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