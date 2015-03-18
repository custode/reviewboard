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
		configuration: null,
		configureLink: null
	},

	url: function() {
		return SITE_ROOT + 'api/configured-integrations/' + this.id + '/';
	},

	/*
	 * Enables the integration.
	 */
	enable: function() {
			this.save({
					enabled: true
			}, {
					wait: true,
					error: _.bind(function(model, xhr) {
							console.log("error");
							this.set({
									loadable: false,
									loadError: xhr.errorRsp.load_error,
									canEnable: !xhr.errorRsp.needs_reload
							});
					}, this)
			});
	},

	/*
	 * Disables the integration.
	 */
	disable: function() {
			this.save({
					enabled: false
			}, {
					wait: true,
					error: function(model, xhr) {
							alert(gettext('Failed to disable integration. ') +
										xhr.errorText + '.');
					}
			});
	},

	/*
	 * Returns a JSON payload for requests sent to the server.
	 */
	toJSON: function() {
			return {
					enabled: this.get('enabled')
			};
	},

	/*
	 * Performs AJAX requests against the server-side API.
	 */
	sync: function(method, model, options) {
			Backbone.sync.call(this, method, model, _.defaults({
					contentType: 'application/x-www-form-urlencoded',
					data: model.toJSON(options),
					processData: true,
					error: _.bind(function(xhr) {
							var rsp = null,
									loadError,
									text;

							try {
									rsp = $.parseJSON(xhr.responseText);
									text = rsp.err.msg;
									loadError = rsp.load_error;
							} catch (e) {
									text = 'HTTP ' + xhr.status + ' ' + xhr.statusText;
							}

							if (_.isFunction(options.error)) {
									xhr.errorText = text;
									xhr.errorRsp = rsp;
									options.error(xhr, options);
							}
					}, this)
			}, options));
	},

	parse: function(rsp) {
		if (rsp.stat !== undefined) {
			rsp = rsp.configured_integration;
		}

		return {
			id: rsp.id,
			name: rsp.name,
			integration: rsp.integration_id,
			integrationDescription: rsp.integration_description,
			integrationIcon: rsp.integration_icon,
			description: rsp.description,
			enabled: rsp.is_enabled,
			configuration: rsp.configuration,
			configureLink: rsp.configure_link
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

	initialize: function(options) {
		this.integrationID = options.integrationID;
	},

	url: function() {
		return SITE_ROOT + 'api/configured-integrations/?integrationID=' +
			this.integrationID;
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
	initialize: function(options) {
		this.configuredIntegrations = new ConfiguredIntegrationCollection(options);
	},

	load: function() {
		this.configuredIntegrations.fetch({
			success: _.bind(function() {
				this.trigger('loaded');
			}, this)
		});
	}
});