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
        this.app.vent.on('choices:load', this.onChoicesLoad);
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

        this.selectStudentChoice();
    },

    registerHandlers: function() {
        this.app.reqres.setHandler("stepData", this.getData);
    },

    onChoicesLoad: function() {
        if (wistiaEmbeds.iframes.length > 0) {
            wistiaEmbeds.bind("end", function() {
                $(".navigation-view").addClass("show").removeClass("hide")
                $('[data-type="MCQBlock"]').addClass("show").removeClass("hide")
                $('.videoWrapper').css("pointer-events", "none" )
                if (!$(".checked").length){
                    $('.navigation-next').attr('disabled', 'disabled')
                }
            });
            $("[data-type='MCQBlock']").parent().addClass("mcq-block");
            $(".navigation-view").addClass("hide").removeClass("show")
            $('[data-type="MCQBlock"]').addClass("hide").removeClass("show")
            $('.videoWrapper').removeAttr("style")
        }
        $("input[type=radio]").map( function() {
            var nameValue = $(this).attr('value').replace("-correct", "")
            $("[data-type='HTMLBlock'] [name='"+ nameValue + "']").hide()
            $(this).parents(".choice").removeClass("checked correct incorrect")
        });

        // wrapping video and MCQs section in order to show feedback below MCQs options
        if (!$(".wrapper-video").length) {
            $('[data-type=\'HTMLBlock\'] [name=\'video\']').
              parents('.step-child').
              siblings('.mcq-block').
              andSelf().
              wrapAll('<div class=\'wrapper-video\' />')
        }
    },

    getData: function() {
        var data = {};

        // Returns the selected choice
        var selected_choice = $('input[type=radio]:checked', this.ui.choices);
        var newClass = '';
        if (selected_choice.length) {
            data['choice'] = selected_choice.val().replace("-correct", "");
            $('.navigation-next').removeAttr("disabled")
            newClass = selected_choice.val().includes("-correct")? "correct": "incorrect";
        }

        $("input[type=radio]").map( function() {
            var nameValue = $(this).attr('value').replace("-correct", "")
            $("[data-type='HTMLBlock'] [name='"+ nameValue + "']").hide()
            $(this).parents(".choice").removeClass("checked correct incorrect")
        });

        var feedbackText = $("[data-type='HTMLBlock'] [name='"+ data['choice'] +"']");

        feedbackText.show();
        feedbackText.addClass(newClass);
        selected_choice.parents(".choice").addClass("checked " + newClass)

        return data;
    },

    selectStudentChoice: function() {
        if (this.model.get('student_choice')) {
            $('input[value=' + this.model.get('student_choice')+']', this.el).prop( "checked", true );
            this.app.vent.trigger('step:choice:select', this.model);
        }
    },

    onChoiceSelect: function() {
        this.app.vent.trigger('step:choice:select', this.model);
    }
});
