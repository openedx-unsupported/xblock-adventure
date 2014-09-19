var AdventureStepView = Backbone.Marionette.LayoutView.extend({
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
        this.initializeXBlockRegions();
    },

    initializeXBlockRegions: function() {
        var self = this;
        _.each(this.model.get('xblocks'), function(xblock) {
            self.addRegion(xblock.id, "#" + xblock.id + ".step-child");
        });
    },

    onRender: function() {
        /* TODO refactoring: do not initialize the xblock like this, create a common XBlockView */
        var self = this;
        _.each(this.model.get('xblocks'), function(xblock) {
            var options = xblock;
            if (!self.model.get('is_studio')) {
                options.xblock.useCurrentHost = true;
                $('#'+options.id, self.el).xblock(options.xblock);
            }
            else {
                $('#'+options.id, self.el).html(
                    '<p>Ooyala-player child will be displayed in the LMS.</p>'
                );
            }
        });
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
