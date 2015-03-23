/*
 * Display an integration class in the Manage Integration list.
 *
 * This will show information about the Integration, and also
 * ConfiguredIntegration which belongs to this integration class.
 * It will also provide link to create new instance of this.
 */
IntegrationView = Backbone.View.extend({
    className: 'integration',
    tagName: 'li',

    events: {
        'click .add-new': '_addNewIntegration'
    },

    template: _.template([
        '<div class="integration-header">',
        '<img class="integration-icon" src="<%-iconPath%>">',
        ' <div class="integration-content"><h1><%- name %></h1>',
        ' <div class="description"><%- description %></div>',
        ' <ul class="add">',
        '   <li><a href="<%- newLink %>">Add</a></li>',
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

        this._loadConfiguredIntegrations();
    },

    /*
     * Load all the configured integrations that belongs to this integration.
     *
     * This will load an configured integration manager view which will
     * display all the ConfiguredIntegration object that belongs to this
     * Integration class.
     */
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
 * Displays an configured integration in Manage Integration list.
 *
 * This wil show all the information about the ConfiguredIntegration object,
 * and provide enabling/disabling/deleting of instance. It will also
 * provide links for configuring it.
 */
ConfiguredIntegrationView = Backbone.View.extend({
    className: 'configured-integration',
    tagName: 'li',

    events: {
        'click .configure-integration': '_configureIntegration',
        'click .enable-toggle': '_toggleEnableState',
        'click .delete-integration': '_deleteIntegration'
    },

    template: _.template([
        '<div class="configured-header">',
        '  <div class="description"><%- description %></div>',
        '  <ul class="options">',
        '    <li class="option"><a href="#" class="enable-toggle"></a></li>',
        '    <li class="option">',
        '      <a href="<%- configureLink %>" class="configure-integration">',
        '        Configure',
        '      </a>',
        '    </li>',
        '    <li class="option">',
        '      <a href="#" class="delete-integration">',
        '        <span class="ui-icon ui-icon-trash"></span>',
        '      </a></li>',
        ' </ul>',
        '</div>'
    ].join('')),

    render: function() {
        this.$el.html(this.template(this.model.attributes));

        this._$enableToggle = this.$('.enable-toggle');
        this.listenTo(this.model, 'change:enabled', this._showEnabledState);
        this._showEnabledState();
    },

    /*
     * Updates the view to reflect the current enabled state.
     *
     * The Enable/Disable linke will change to reflect the state.
     */
    _showEnabledState: function() {
        var enabled = this.model.get('enabled');

        this.$el
            .removeClass(enabled ? 'disabled' : 'enabled')
            .addClass(enabled ? 'enabled' : 'disabled');

        this._$enableToggle
            .text(enabled ? gettext('Disable') : gettext('Enable'));
    },

    /*
     * Toggle the enabled state of the ConfiguredIntegration.
     */
    _toggleEnableState: function() {
        if (this.model.get('enabled')) {
            this.model.disable();
        } else {
            this.model.enable();
        }

        return false;
    },

    /*
     * Delete the ConfiguredIntegration object.
     *
     * This destory the ConfiguredIntegration by call HTTP DELETE
     * through the destory method. The ConfiguredIntegration will be removed
     * from the list if the response from the server is a success. If not,
     * it will alert the user of the error in deleting.
     */
    _deleteIntegration: function() {
        var response = confirm("This action will delete the configured"
                             + " integration.");

        if (response) {
            this.model.destroy({
                success: _.bind(function() {
                    this.remove();
                }, this),
                error: function(model, xhr) {
                    alert(gettext('Failed to delete integration. ') +
                          xhr.errorText + '.');
                }
            });
        }

        return false;
    }
});


/*
 * Display the interface showing all Integrations.
 *
 * This loads the list of Integrations and display each in a list.
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
 * Display the interface showing all the ConfiguredIntegrations.
 *
 * This is used by the IntegrationView to generate all the
 * ConfiguredIntegration that belongs to the integration class.
 * It will render each ConfiguredIntegration in the list.
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