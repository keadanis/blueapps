odoo.define('theme_syncoria_electronics.editor', function (require) {
var editor = require('web_editor.editor');
var EditorMenuBar = editor.Class.include({
    _onSaveClick: function () {
        var te = `<div><img src="/theme_syncoria_electronics/static/src/images/loading.svg" alt="loading" style="margin:auto;display:block;text-align:center" /></div>`;
        $('.syncoria-snippet-initialized').each(function () {
            $(this).removeClass('syncoria-snippet-initialized');
            $(this).html(te);
        });
        $('.slick-initialized').slick('unslick');
        this._super.apply(this, arguments);
    },
});
return  {
    Class: EditorMenuBar,
}

});