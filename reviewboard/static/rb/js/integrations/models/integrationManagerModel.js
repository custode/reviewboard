/*
This represent an integration model
*/
Integration = Backbone.Model.extend({
  defaults: {

  },

  url: function() {
    return SITE_ROOT + 'api/integrations/' + this.id + '/';
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