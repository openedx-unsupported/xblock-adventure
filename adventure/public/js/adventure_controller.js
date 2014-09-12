var AdventureController = Backbone.Marionette.Controller.extend({

    initialize: function(options) {
        this.app = options.app;
        this.runtime = options.runtime;

        this._createFunctionAliases();
        _.bindAll(this, 'showNextStep', 'showPreviousStep', 'showStep', 'startOver');
    },

    /* Create the following function aliases, which are variants of _fetchStep
     * _fetchCurrentStep
     * _fetchNextStep
     * _fetchPreviousStep
     * _startOver
     */
    _createFunctionAliases: function() {
        this._fetchCurrentStep = _.partial(
            this._fetchStep,
            this.runtime.handlerUrl(this.app.container, 'fetch_current_step')
        );

        this._fetchNextStep = _.partial(
            this._fetchStep,
            this.runtime.handlerUrl(this.app.container, 'submit')
        );

        this._fetchPreviousStep = _.partial(
            this._fetchStep,
            this.runtime.handlerUrl(this.app.container, 'fetch_previous_step')
        );

        this._startOver = _.partial(
            this._fetchStep,
            this.runtime.handlerUrl(this.app.container, 'start_over')
        );
    },

    // Fetch previous current and next steps on th server
    // Mock this function for client side tests
    _fetchStep: function(url, data) {
        var self = this;
        var defer = $.Deferred();
        var promise = defer.promise();
        var data = data || {};

        $.post(url, JSON.stringify(data)).done(function(data) {
            if (data.result == 'error') {
                console.error("Failed to fetch step: " + data.message);
                defer.reject();
            }
            else {
                defer.resolve(data.step);
            }
        }).fail(function() {
            console.error("Failed to fetch step.");
            defer.reject();
        });

        return promise;
    },

    _changeNavigationRegion: function(view) {
        this.app.navigationViewRegion.show(view);
    },

    _changeStepRegion: function(view) {
        this.app.stepViewRegion.show(view);
    },

    // Controller Public API
    showNavigation: function() {
        this._changeNavigationRegion(new AdventureNavigationView({app: this.app}));
    },

    showStep: function(step_data) {
        var step = new AdventureStepModel(step_data);
        this._changeStepRegion(new AdventureStepView({model: step}))
        this.app.vent.trigger('step:is:last', step_data.is_last_step);
        this.app.vent.trigger('step:allow:back', step_data.can_go_back);
    },

    showCurrentStep: function() {
        this._fetchCurrentStep().done(this.showStep);
    },

    showNextStep: function() {
        this._fetchNextStep().done(this.showStep);
    },

    showPreviousStep: function() {
        this._fetchPreviousStep().done(this.showStep);
    },

    startOver: function() {
        this._startOver().done(this.showStep);
    }
});
