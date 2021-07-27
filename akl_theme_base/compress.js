/**
 * ugly and compress the js
 */
let UglifyJS = require("uglify-js");
let fs = require("fs");
let path = require("path")

function _compress(dir) {
    const files = fs.readdirSync(dir)
    files.forEach(function (tmpFile, index) {
        if (tmpFile == 'compress.js' 
        || !tmpFile 
        || tmpFile == 'akara_overlay.js'
        || tmpFile == 'akara_selection.js'
        || tmpFile == 'akara_action_manager.js' 
		|| tmpFile == 'akara_control_pannel.js' 
		|| tmpFile == 'akara_fields_old.js' 
		|| tmpFile == 'akara_footer.js' 
		|| tmpFile == 'akara_form_render.js'
		|| tmpFile == 'akara_ralation_fields.js' 
		|| tmpFile == 'akara_view_dialog.js') {
            return
        }
		
        let file_path = path.join(dir, tmpFile)
        let stat = fs.lstatSync(file_path)
        if (stat.isFile()) {
            let code = fs.readFileSync(file_path, "utf8");
            let uglifyCode = UglifyJS.minify(code, {
                mangle: { reserved: ['require', '_super'] }
            }).code;
            if (uglifyCode) {
                fs.writeFileSync(file_path, uglifyCode);
            }
        } if (stat.isDirectory() && tmpFile != '.' && tmpFile != '..') {
            _compress(file_path)
        }
    })
}

_compress('./static/js/')


