/*
*/
IntegrationView = Backbone.View.extend({
  className: 'integration',
  tagName: 'li',

  events: {

  },

  render: function() {
    this.$el.html(this.integrationTemplate());
  }

});

/*
*/
IntegrationManagerView = Backbone.View.extend({
  initialize: function() {
    this._$integrations = null;
  },

  render: function() {
    this._$integrations = this.$('.integrations');

    this.listenTo(this.model, 'loaded', this._onLoaded);

    this.model.load();

    return this;
  },

  _onLoaded: function() {
    this.model.integrations.each(function(integration) {
      var view = new IntegrationView({
        model: integration
      });

      this._$integrations.append(view.$el);
      // odd or even, enable or not enable
      view.render();

      this._$integrations.appendTo(this.$el);
    }, this);
  }

});