var AdventureStepModel = Backbone.Model.extend({
    defaults: {
        name: '',
        has_back_step: false,
        has_next_step: false,
        html: '',
        has_choices: false,
        xblocks: [],
        is_studio: false // TODO should be in the app config, not here. To move.
    }
});
