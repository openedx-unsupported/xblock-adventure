var AdventureStepView = Backbone.Marionette.ItemView.extend({
    template: "#adventure-step-view-template",

    ui: {
        'choices': '.choices .choices-list'
    },

    events: {
        "click @ui.choices .choice-selector": 'onChoiceSelect'
    },

    initialize: function(options) {
        this.app = options.app;
        _.bindAll(this, 'getData', 'onChoiceSelect');
        this.registerHandlers();
    },

    registerHandlers: function() {
        this.app.reqres.setHandler("stepData", this.getData);
    },

    getData: function() {
        var data = {};

        // Returns the selected choice
        var selected_choice = $('input[type=radio]:checked', this.ui.choices);
        if (selected_choice.length) {
            data['choice'] = selected_choice.val();
        };

        return data;
    },

    onChoiceSelect: function() {
        this.app.vent.trigger('step:choice:select', this.model);
    }
});
