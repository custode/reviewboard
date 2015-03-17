/*
Provide the view for each integration
*/
IntegrationView = Backbone.View.extend({
  className: 'integration',
  tagName: 'li',

  events: {
    'click .manage-integration': '_toggleManage',
    'click .add-new': '_addNewIntegration'
  },

  template: _.template([
    '<div class="integration-header">',
    '<img class="integration-icon" src="<%-iconPath%>">',
    ' <div class="integration-content"><h1><%- name %></h1>',
    ' <div class="description"><%- description %></div>',
    ' <ul class="expand">',
    '   <li class="manage-integration"><a href="#">Add</a></li>',
    ' </ul></div>',
    '</div>',
    '<ul class="configured-integrations">',
    '</ul>'
  ].join('')),

  initialize: function() {
    this._$configuredIntegrationsView = null;
    this.toggle = false;
  },

  render: function() {
    this.$el.html(this.template(this.model.attributes));

    this._toggleManage();
  },

  _toggleManage: function() {
    if (this._$configuredIntegrationsView === null) {
      this._loadConfiguredIntegrations();
    }

    this.$('.configured-integrations').toggle('fast');

    this.$('.manage-integration div')
      .removeClass(this.toggle ? 'down' : 'right')
      .addClass(this.toggle ? 'right' : 'down');

    this.toggle = this.toggle ? false : true;
  },

  _loadConfiguredIntegrations: function() {
    this._$configuredIntegrationsView = new ConfiguredIntegrationManagerView({
      el: this.$el,
      model: new ConfiguredIntegrationManager({
        integrationID: this.model.attributes.integrationID
      })
    });

    this._$configuredIntegrationsView.render();
  }
});

/*
Provide the view for each configured integration
*/
ConfiguredIntegrationView = Backbone.View.extend({
  className: 'configured-integration',
  tagName: 'li',

  events: {
    'click .configure-integration': '_configureIntegration',
    'click .enable-toggle': '_toggleEnableState'
  },

  template: _.template([
    '<div class="configured-header">',
    ' <div class="description"><%- description %></div>',
    ' <ul class="options">',
    '   <li class="option"><a href="#" class="enable-toggle"></a></li>',
    '   <li class="option">',
    '     <a href="<%- configureLink %>" class="configure-integration">',
    '        Configure',
    '     </a>',
    '   </li>',
    ' </ul>',
    '</div>'
  ].join('')),

  render: function() {
    this.$el.html(this.template(this.model.attributes));

    this._$enableToggle = this.$('.enable-toggle');
    this.listenTo(this.model, 'change:enabled', this._showEnabledState);
    this._showEnabledState();
  },

  _showEnabledState: function() {
    var enabled = this.model.get('enabled');

    this.$el
      .removeClass(enabled ? 'disabled' : 'enabled')
      .addClass(enabled ? 'enabled' : 'disabled');

    this._$enableToggle
      .text(enabled ? gettext('Disable') : gettext('Enable'));
  },

  _toggleEnableState: function() {
    if (this.model.get('enabled')) {
      this.model.disable();
    } else {
      this.model.enable();
    }

    return false;
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
      view.render();
    }, this);
  }
});

/*
Provide the view to manage all the integrations
*/
ConfiguredIntegrationManagerView = Backbone.View.extend({
  initialize: function(options) {
    this._$configuredIntegrations = null;
    this.integrationID = options.integrationID;
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
        model: configuredIntegration,
        integrationID: this.integrationID
      });

      this._$configuredIntegrations.prepend(view.$el);
      view.render();
    }, this);
  }
});