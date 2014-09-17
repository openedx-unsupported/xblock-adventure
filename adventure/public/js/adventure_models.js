var AdventureStepModel = Backbone.Model.extend({
    defaults: {
        name: '',
        has_back_step: false,
        html: '',
        is_last_step: false,
        has_choices: false
    }
});
