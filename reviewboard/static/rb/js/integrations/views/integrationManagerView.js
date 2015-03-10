/*
Provide the view for each integration
*/
IntegrationView = Backbone.View.extend({
  className: 'integration',
  tagName: 'li',

  events: {

  },

/*
Provide the view for each configured integration
*/
ConfiguredIntegrationView = Backbone.View.extend({
  className: 'configured-integration',
  tagName: 'li',

  events: {

  },

  template: _.template([
    '<div class="configured-integration">',
    '<h1><%- integration %></h1>',
    'Enabled: <%- enabled %>',
    'Description: <%- description %>',
    'Configuration: <%- configuration %>',
    '</div>'
  ].join('')),

  render: function() {
    this.$el.html(this.template(this.model.attributes));
  }

});

/*
Provide the view to manage all the integrations
*/
ConfiguredIntegrationManagerView = Backbone.View.extend({
  initialize: function() {
    this._$configuredIntegrations = null;
  },

  render: function() {
    this._$configuredIntegrations = this.$('.configured-integrations');

    this.listenTo(this.model, 'loaded', this._onLoaded);

    this.model.load();

    return this;
  },

  _onLoaded: function() {
    this.model.configuredIntegrations.each(function(configuredIntegration) {
      var view = new ConfiguredIntegrationView({
        model: configuredIntegration
      });

      this._$configuredIntegrations.append(view.$el);
      view.render();

      this._$configuredIntegrations.appendTo(this.$el);
    }, this);
  }

});