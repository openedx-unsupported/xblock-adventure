var AdventureNavigationView = Backbone.Marionette.ItemView.extend({
    template: "#adventure-navigation-view-template",

    ui: {
        backButton: ".navigation-back",
        nextButton: ".navigation-next",
        startOverButton: ".navigation-start-over"
    },

    events: {
        "click @ui.backButton": 'showPreviousStep',
        "click @ui.nextButton": 'showNextStep',
        "click @ui.startOverButton": 'startOver'
    },

    initialize: function(options) {
        this.app = options.app;
        _.bindAll(this, 'lastStepHandler', 'backHandler');
        this.app.vent.on('step:is:last', this.lastStepHandler);
        this.app.vent.on('step:allow:back', this.backHandler);
    },

    showNextStep: function(event) {
        event.preventDefault();
        this.app.vent.trigger('showNextStep');
    },

    showPreviousStep: function(event) {
        event.preventDefault();
        this.app.vent.trigger('showPreviousStep');
    },

    startOver: function(event) {
        event.preventDefault();
        this.app.vent.trigger('startOver');
    },

    // handlers
    lastStepHandler: function(value) {
        if (value) {
            this.ui.nextButton.hide();
        }
        else {
            this.ui.nextButton.show();
        }
    },

    backHandler: function(value) {
        if (value) {
            this.ui.backButton.show();
        }
        else {
            this.ui.backButton.hide();
        }
    }
});
