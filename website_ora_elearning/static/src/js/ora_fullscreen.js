odoo.define('website_ora_elearning.ora', function (require) {
'"use strict"';

var core = require('web.core');
var _lt = core._lt;
var QWeb = core.qweb;
var Fullscreen = require('website_slides.fullscreen');
var publicWidget = require('web.public.widget');
var wysiwygLoader = require('web_editor.loader');
var weDefaultOptions = require('web_editor.wysiwyg.default_options');

/**
 * Helper: Get the slide dict matching the given criteria
 *
 * @private
 * @param {Array<Object>} slideList List of dict reprensenting a slide
 * @param {Object} matcher (see https://underscorejs.org/#matcher)
 */
var findSlide = function (slideList, matcher) {
    var slideMatch = _.matcher(matcher);
    return _.find(slideList, slideMatch);
};


Fullscreen.include({
    xmlDependencies: (Fullscreen.prototype.xmlDependencies || []).concat(
        ["/website_ora_elearning/static/src/xml/slide_ora.xml"]
    ),
    events: {
        "click .o_wslides_js_lesson_ora_submit": '_submitOra',
        "click .o_submit_peer_response": '_submitPeer',
        "click .o_wslides_fs_toggle_sidebar": '_onClickToggleSidebar',
    },
    /**
    * @override
    * @param {Object} el
    * @param {Object} slides Contains the list of all slides of the course
    * @param {integer} defaultSlideId Contains the ID of the slide requested by the user
    */
    init: function (parent, slides, defaultSlideId, channelData){
        var result = this._super.apply(this,arguments);
        var slide;
        var urlParams = $.deparam.querystring();
        if (defaultSlideId) {
            slide = findSlide(slides, {id: defaultSlideId, isQuiz: urlParams.quiz === "1"});
        } else {
            slide = this.slides[0];
        }
        this.set('slide', slide);
        this.sidebar = new NewSidebar(this, this.slides, slide);
        return result;
    },
    _preprocessSlideData: function (slidesDataList) {
        var res = this._super.apply(this, arguments);
        res.forEach(function (slideData, index) {
            slideData.isOra = !!slideData.isOra;
            slideData.hasQuestion = !!slideData.hasQuestion;
            slideData._autoSetDone = _.contains(['infographic', 'presentation', 'document', 'webpage'], slideData.type) && !slideData.isOra && !slideData.hasQuestion;
        });
        return res;
    },
    _onChangeSlideRequest: function (ev){
        var slideData = ev.data;
        var newSlide = findSlide(this.slides, {
            id: slideData.id,
            isQuiz: slideData.isQuiz || false,
            isOra: slideData.isOra || false,
        });
        this.set('slide', newSlide);
        this.shareButton._onChangeSlide(newSlide);
    },
    _renderSlide: function (){
        var def = this._super.apply(this, arguments);
        var $content = this.$('.o_wslides_fs_content');
        var self = this;
        if (this.get('slide').isOra === true){
            this._rpc({
                route: '/slides/slide/get_values',
                params: {
                    slide_id:(this.get('slide').id),
                }
            }).then(function (data){
                $content.html(QWeb.render('slide.ora.assessment',{widget: data}));
                _.each($('textarea.o_wysiwyg_loader'), function (textarea) {
                    var $textarea = $(textarea);
                    var toolbar = [
                        ['style', ['style']],
                        ['font', ['bold', 'italic', 'underline', 'clear']],
                        ['para', ['ul', 'ol', 'paragraph']],
                        ['table', ['table']],
                        ['insert', ['link', 'picture']],
                        ['video', ['video', 'audio']]
                    ];
                    var options = {
                        height: 150,
                        // width: 939,
                        minHeight: 80,
                        toolbar: toolbar,
                        styleWithSpan: false,
                        styleTags: _.without(weDefaultOptions.styleTags, 'h1', 'h2', 'h3'),
                        disableResizeImage: true,
                    };
                    wysiwygLoader.load(self, $textarea[0], options).then(wysiwyg => {
                        self._wysiwyg = wysiwyg;
                    });
                });
                _.each(this.$('.o_wforum_bio_popover'), authorBox => {
                    $(authorBox).popover({
                        trigger: 'hover',
                        offset: 10,
                        animation: false,
                        html: true,
                    });
                });
        
                $('.custom_response').click(function() {
                    var id = this.id.split('-')[this.id.split('-').length - 1]
                    if($('#collapse_div_'+id).hasClass('show')) {
                        $(this).children().text(_lt('View Response'))
                    }else {
                        $(this).children().text(_lt('Hide Response'))
                    }
                });
            });
        }
        return Promise.all([def]);
    },

    _submitPeer: function (ev) {
        var id = ev.currentTarget.id.split('_')[ev.currentTarget.id.split('_').length - 1]
        var data = $('#ora_peer_submit_'+id).serializeArray();
        var self = this;
        ev.preventDefault();
        $.ajax({
            type: "POST",
            url: "/submit/peer/response",
            data: data,
            success: function (data) {
                self._renderSlide();
            }
        });
    },

    _submitOra: function (ev) {
        var data = $('#ora_form').serializeArray();
        data.push({name: ev.currentTarget.name, value: ev.currentTarget.value});
        ev.preventDefault();
        var self = this;
        $.ajax({
            type: "POST",
            url: "/ora/response/save/",
            data: data,
            success: function (data) {
                self._renderSlide();
            }
        });
    },
});
/**
 * This widget is responsible of navigation for one slide to another:
 *  - by clicking on any slide list entry
 *  - by mouse click (next / prev)
 *  - by recieving the order to go to prev/next slide (`goPrevious` and `goNext` public methods)
 *
 * The widget will trigger an event `change_slide` with
 * the `slideId` and `isMiniQuiz` as data.
 */
var NewSidebar = publicWidget.Widget.extend({
    events: {
        "click .o_wslides_fs_sidebar_list_item": '_onClickTab',
    },
    init: function (parent, slideList, defaultSlide) {
        var result = this._super.apply(this, arguments);
        this.slideEntries = slideList;
        this.set('slideEntry', defaultSlide);
        return result;
    },
    start: function (){
        var self = this;
        this.on('change:slideEntry', this, this._onChangeCurrentSlide);
        return this._super.apply(this, arguments).then(function (){
            $(document).keydown(self._onKeyDown.bind(self));
        });
    },
    destroy: function () {
        $(document).unbind('keydown', this._onKeyDown.bind(this));
        return this._super.apply(this, arguments);
    },
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------
    /**
     * Change the current slide with the next one (if there is one).
     *
     * @public
     */
    goNext: function () {
        var currentIndex = this._getCurrentIndex();
        if (currentIndex < this.slideEntries.length-1) {
            this.set('slideEntry', this.slideEntries[currentIndex+1]);
        }
    },
    /**
     * Change the current slide with the previous one (if there is one).
     *
     * @public
     */
    goPrevious: function () {
        var currentIndex = this._getCurrentIndex();
        if (currentIndex >= 1) {
            this.set('slideEntry', this.slideEntries[currentIndex-1]);
        }
    },
    /**
     * Greens up the bullet when the slide is completed
     *
     * @public
     * @param {Integer} slideId
     */
    setSlideCompleted: function (slideId) {
        var $elem = this.$('.fa-circle-thin[data-slide-id="'+slideId+'"]');
        $elem.removeClass('fa-circle-thin').addClass('fa-check text-success o_wslides_slide_completed');
    },
    /**
     * Updates the progressbar whenever a lesson is completed
     *
     * @public
     * @param {*} channelCompletion
     */
    updateProgressbar: function (channelCompletion) {
        var completion = Math.min(100, channelCompletion);
        this.$('.progress-bar').css('width', completion + "%" );
        this.$('.o_wslides_progress_percentage').text(completion);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    /**
     * Get the index of the current slide entry (slide and/or quiz)
     */
    _getCurrentIndex: function () {
        var slide = this.get('slideEntry');
        var currentIndex = _.findIndex(this.slideEntries, function (entry) {
            return entry.id === slide.id && entry.isQuiz === slide.isQuiz;
        });
        return currentIndex;
    },
    //--------------------------------------------------------------------------
    // Handler
    //--------------------------------------------------------------------------
    /**
     * Handler called whenever the user clicks on a sub-quiz which is linked to a slide.
     * This does NOT handle the case of a slide of type "quiz".
     * By going through this handler, the widget will be able to determine that it has to render
     * the associated quiz and not the main content.
     *
     * @private
     * @param {*} ev
     */
    _onClickMiniQuiz: function (ev){
        var slideID = parseInt($(ev.currentTarget).data().slide_id);
        this.set('slideEntry',{
            slideID: slideID,
            isMiniQuiz: true
        });
        this.trigger_up('change_slide', this.get('slideEntry'));
    },
    /**
     * Handler called when the user clicks on a normal slide tab
     *
     * @private
     * @param {*} ev
     */
    _onClickTab: function (ev) {
        ev.stopPropagation();
        var $elem = $(ev.currentTarget);
        if ($elem.data('canAccess') === 'True') {
            var isQuiz = $elem.data('isQuiz');
            var isOra = $elem.data('isOra');
            var slideID = parseInt($elem.data('id'));
            var slide = findSlide(this.slideEntries, {id: slideID, isQuiz: isQuiz, isOra: isOra});
            this.set('slideEntry', slide);
        }
    },
    /**
     * Actively changes the active tab in the sidebar so that it corresponds
     * the slide currently displayed
     *
     * @private
     */
    _onChangeCurrentSlide: function () {
        var slide = this.get('slideEntry');
        this.$('.o_wslides_fs_sidebar_list_item.active').removeClass('active');
        var selector = '.o_wslides_fs_sidebar_list_item[data-id='+slide.id+'][data-is-quiz!="1"]';

        this.$(selector).addClass('active');
        this.$('.ora_tab.active').removeClass('active');
        this.trigger_up('change_slide', this.get('slideEntry'));
    },

    /**
     * Binds left and right arrow to allow the user to navigate between slides
     *
     * @param {*} ev
     * @private
     */
    _onKeyDown: function (ev){
        switch (ev.key){
            case "ArrowLeft":
                this.goPrevious();
                break;
            case "ArrowRight":
                this.goNext();
                break;
        }
    },
});
});