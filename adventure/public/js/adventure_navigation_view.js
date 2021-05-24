var AdventureNavigationView = Backbone.Marionette.ItemView.extend({
    template: "#adventure-navigation-view-template",

    ui: {
        backButton: ".navigation-back",
        nextButton: ".navigation-next",
        startOverButton: ".navigation-start-over"
    },

    events: {
        "click @ui.backButton": 'onShowPreviousStep',
        "click @ui.nextButton": 'onShowNextStep',
        "click @ui.startOverButton": 'onStartOver'
    },

    initialize: function(options) {
        this.app = options.app;
        _.bindAll(this, 'onStepChange', 'onStepChoiceSelect');
        this.app.vent.on('step:change', this.onStepChange);
        this.app.vent.on('step:choice:select', this.onStepChoiceSelect);
    },

    onShowNextStep: function(event) {
        event.preventDefault();
        event.currentTarget.disabled = true;
        this.app.vent.trigger('show:next:step');
    },

    onShowPreviousStep: function(event) {
        event.preventDefault();
        this.app.vent.trigger('show:previous:step');
    },

    onStartOver: function(event) {
        event.preventDefault();
        this.app.vent.trigger('start:over');
    },

    // handlers. TODO refactor for a better readability?
    onStepChange: function(step) {
        if (step.get('has_choices') && !step.get('student_choice')) {
            this.ui.nextButton.attr('disabled','disabled');
            this.ui.nextButton.show();
        }
        else {
            this.ui.nextButton.removeAttr('disabled');
            if (step.get('has_next_step') || step.get('student_choice')) {
                this.ui.nextButton.show();
            }
            else {
                this.ui.nextButton.hide();
            }
        }

        if (step.get('has_back_step')) {
            this.ui.backButton.show();
        }
        else {
            this.ui.backButton.hide();
        }

        if (step.get('can_start_over')) {
            this.ui.startOverButton.show();
        }
        else {
            this.ui.startOverButton.hide();
        }
        this.app.vent.trigger('choices:load');
    },

    onStepChoiceSelect: function(step) {
        this.ui.nextButton.removeAttr('disabled');
    }

});
