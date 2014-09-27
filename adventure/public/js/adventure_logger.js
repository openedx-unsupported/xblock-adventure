var AdventureLogger = Backbone.Marionette.Controller.extend({
    initialize: function(options) {
        this.app = options.app;
        this.runtime = options.runtime;
        this.element = options.element;
        this.registerHandlers();
    },

    registerHandlers: function() {
        _.bindAll(this, 'logStepShown', 'logChoiceSelected', 'logWentForward',
            'logWentBackward', 'logStartedOver', 'logVideoStarted');
        this.app.vent.on("step:change", this.logStepShown);
        this.app.vent.on("step:choice:select", this.logChoiceSelected);
        this.app.vent.on("show:next:step", this.logWentForward);
        this.app.vent.on("show:previous:step", this.logWentBackward);
        this.app.vent.on("start:over", this.logStartedOver);
    },

    logStepShown: function(step) {
        var step_name = step.get("name");
        this._publish_event({
            event_type: "xblock.adventure.step-shown",
            step: step_name
        });

        var is_final_step = !(step.get("has_next_step") || step.get("has_choices"));
        if (is_final_step) {
            this._publish_event({event_type: "xblock.adventure.final-step-shown"});
        };
    },

    logChoiceSelected: function(step) {
        this._publish_event({
            event_type: "xblock.adventure.choice-selected",
            step: step.get("name"),
            choice: this.app.request('stepData').choice
        });
    },

    logWentForward: function() {
        this._publish_event({event_type: "xblock.adventure.went-forward"});
    },

    logWentBackward: function() {
        this._publish_event({event_type: "xblock.adventure.went-backward"});
    },

    logStartedOver: function() {
        this._publish_event({event_type: "xblock.adventure.started-over"});
    },

    _publish_event: function(data) {
        console.log("publising event", data);
        $.ajax({
            type: "POST",
            url: this.runtime.handlerUrl(this.element, 'publish_event'),
            data: JSON.stringify(data)
        });
    }
});
