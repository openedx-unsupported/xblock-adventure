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
        $("input[type=radio]").map( function() {
            var nameValue = $(this).attr('value').replace("-correct", "")
            $("[data-type='HTMLBlock'] [name='"+ nameValue + "']").hide()
            $(this).parents(".choice").removeClass("checked correct incorrect")
        });

        var isFullScreen = false;
        if (wistiaEmbeds.iframes.length > 0) {
            wistiaEmbeds.bind("enterfullscreen", function() {
                isFullScreen = true;
            });
            wistiaEmbeds.bind("cancelfullscreen", function() {
                isFullScreen = false;
                if (wistiaApi._state === 'ended') {
                    $(".navigation-view").addClass('show').removeClass('hide');
                    var mcqBlock = $('[data-type="MCQBlock"]');
                    mcqBlock.addClass("show").removeClass("hide")
                    if (mcqBlock.length) {
                        $('.videoWrapper').css("pointer-events", "none" )
                    } else {
                        $(".navigation-next").css('display','none');
                        if ($('.navigation-back').css('display') === 'none') {
                            $(".navigation-back-next-buttons").css("background", "#ffffff");
                        }
                    }
                }
            });

            wistiaEmbeds.bind("end", function() {
                if (isFullScreen) {
                    return
                }
                $(".navigation-view").addClass('show').removeClass('hide');
                var mcqBlock = $('[data-type="MCQBlock"]');
                mcqBlock.addClass("show").removeClass("hide")
                if (mcqBlock.length) {
                    $('.videoWrapper').css("pointer-events", "none" )
                } else {
                    $(".navigation-next").css('display','none');
                    if ($('.navigation-back').css('display') === 'none') {
                        $(".navigation-back-next-buttons").css("background", "#ffffff");
                    }
                }
            });
            $("[data-type='MCQBlock']").parent().addClass("mcq-block");
            $(".navigation-view").addClass("hide").removeClass("show")
            $('[data-type="MCQBlock"]').addClass("hide").removeClass("show")
            $('.videoWrapper').removeAttr("style")
        } else {
            $(".navigation-view").addClass("show").removeClass("hide");
            if (!$('[data-type="MCQBlock"]').length) {
                $(".navigation-next").css('display','none');
            }
        }

        if (!$(".checked").length){
            $('.navigation-next').attr('disabled', 'disabled')
        }

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
        var selectedChoice = $('input[type=radio]:checked');
        var newClass = '';
        if (selectedChoice.length) {
            data['choice'] = selectedChoice.val().replace("-correct", "");
            $('.navigation-next').removeAttr("disabled")
            newClass = selectedChoice.val().includes("-correct")? "correct": "incorrect";
        }

        $("input[type=radio]").map( function() {
            var nameValue = $(this).attr('value').replace("-correct", "")
            $("[data-type='HTMLBlock'] [name='"+ nameValue + "']").hide()
            $(this).parents(".choice").removeClass("checked correct incorrect")
        });

        var feedbackText = $("[data-type='HTMLBlock'] [name='"+ data['choice'] +"']");

        feedbackText.show();
        feedbackText.addClass(newClass);
        selectedChoice.parents(".choice").addClass("checked " + newClass)

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
