fabric.Object.prototype.set({
    transparentCorners: false,
    borderColor: '#ff38ae',
    cornerColor: '#ff0000',
    cornerSize: 20
});

window.initWidth = 1200;
window.initHeight = 700;

var grid = 5;
window.textFills = ['#000', '#fff', '#BFBFBF'];
window.selectedTexts = [];

var canvas = new fabric.Canvas('canvas', {
    preserveObjectStacking: true,
    width: window.initWidth,
    height: window.initHeight
});

var resizeCanvas = function (w, h) {
    w = Number(document.getElementById('canvas_width').value);
    h = Number(document.getElementById('canvas_height').value);
    if (!(w && h)) {
        return;
    }
    canvas.setWidth(w);
    canvas.setHeight(h);
    canvas.calcOffset();
    M.Modal.getInstance(document.getElementById('resize-modal')).close();
};

var setHooks = function () {
    canvas.off('object:modified');
    canvas.off('object:added');
    canvas.off('object:selected');
    canvas.on('object:added', function (options) {
        options.target.setControlsVisibility({
            ml: false,
            mt: false,
            mr: false,
            mb: false,
            mtr: false
        });
    });

    var selectionCallback = function (options) {
        window.selectedTexts = [];
        if (options.target.type === 'i-text') {
            window.selectedTexts = [options.target];
        } else if (options.target.getObjects) {
            window.selectedTexts = options.target.getObjects().filter(
                function (a) {
                    return a.type === 'i-text';
                }
            );
        }
    };
    canvas.on('selection:updated', selectionCallback);
    canvas.on('selection:created', selectionCallback);
    // window.onbeforeunload = function (e) {
    //     var dialogText = 'Unsaved progress will be lost. Exit anyway?';
    //     e.returnValue = dialogText;
    //     return dialogText;
    // };

    document.body.onkeydown = function (e) {
        if (!e.ctrlKey) {
            return;
        }
        if (window.selectedTexts && e.key === 'c') {
            window.selectedTexts.forEach(function (text) {
                console.log(text.fill);
                var fillIndex = (window.textFills.indexOf(text.fill) + 1);
                text.set({
                    fill: window.textFills[fillIndex % window.textFills.length]
                });
            });
            canvas.requestRenderAll();
        } else if (e.key === 's') {
            saveProject();
            e.preventDefault();
        }
    };

    // http://jsfiddle.net/fabricjs/S9sLu/
    canvas.on('object:moving', function (options) {
        options.target.set({
            left: Math.round(options.target.left / grid) * grid,
            top: Math.round(options.target.top / grid) * grid
        });
    });

};

var addYearToImage = function (image, year) {
    var year_text = new fabric.IText(year.toString(), {
        left: image.left + grid * 2,
        top: image.top + grid * 2,
        fontFamily: 'Intro',
        fill: window.textFills[1],
        fontSize: Math.round(window.innerWidth / 50)
    });
    canvas.add(year_text);
};


var placeObjectsFromPost = function (post, use_json, resolve) {

    canvas.clear();

    if (use_json && post.canvas_json) {
        canvas.loadFromJSON(post.canvas_json);
        resolve();
        return;
    }
    canvas.setWidth(window.initWidth);
    canvas.setHeight(window.initHeight);
    canvas.calcOffset();

    canvas.backgroundColor = '#BFBFBF';

    fabric.Image.fromURL(post.old_work, function (old_work_img) {
        old_work_img.top = grid;
        old_work_img.left = grid;
        old_work_img.scaleToHeight(Math.round(window.innerHeight / 2));
        canvas.add(old_work_img);

        addYearToImage(old_work_img, post.old_work_year);

        fabric.Image.fromURL(post.new_work, function (new_work_img) {
            new_work_img.top = grid;
            new_work_img.left = old_work_img.getScaledWidth() + grid * 2;
            new_work_img.scaleToHeight(Math.round(window.innerHeight / 2));
            canvas.add(new_work_img);

            addYearToImage(new_work_img, post.new_work_year);
            if (post.account.logo) {
                fabric.Image.fromURL(post.account.logo, function (logo_img) {
                    logo_img.top = old_work_img.getScaledHeight() + grid * 2;
                    logo_img.left = grid;
                    logo_img.scaleToWidth(canvas.width / 10);
                    canvas.add(logo_img);
                    place_text(logo_img.getScaledWidth());
                });
            } else {
                place_text(0);
            }
        });

        var place_text = function (x_offset, y_offset) {
            var name = new fabric.IText(post.name_en, {
                left: x_offset + grid * 2,
                top: old_work_img.getScaledHeight() + grid * 2,
                fontFamily: 'Intro',
                fontSize: 30,
                fill: window.textFills[0]
            });
            canvas.add(name);

            var text = new fabric.IText(post.text_en, {
                left: x_offset + grid * 2,
                top: name.top + name.getScaledHeight() + grid,
                fontFamily: 'Intro',
                fontSize: 15,
                fill: window.textFills[0]
            });
            canvas.add(text);

            var links_text = [];
            post.links.forEach(function (l) {
                links_text.push(l.url)
            });
            var links = new fabric.IText(links_text.join('\n'), {
                left: x_offset + grid * 2,
                top: text.top + text.getScaledHeight() + grid,
                fontFamily: 'Intro',
                fontSize: 13,
                fill: window.textFills[0]
            });
            canvas.add(links);
            resolve();
        };
    });
};


var saveProject = function () {
    var button = document.getElementById('save');
    button.disabled = true;

    axios.post(
        '/post/' + window.post_id + '/save_canvas/',
        JSON.stringify(canvas),
        {headers: {'X-CSRFToken': window.csrf_token}}
    ).then(function () {
        button.disabled = false;
        M.toast({html: 'Saved', displayLength: 1000})
    }).catch(function (reason) {
        console.log(reason);
    });
};


var render = function () {
    var render_name = document.getElementById('render_name').value;
    var button = document.getElementById('render');
    button.disabled = true;

    axios.post(
        '/post/' + window.post_id + '/save_render/',
        canvas.toDataURL(),
        {
            headers: {'X-CSRFToken': window.csrf_token},
            params: {'f': render_name + '.png'}
        }
    ).then(function (response) {
        M.Modal.getInstance(document.getElementById('render-modal')).close();
        var url = window.location.origin + response.data.url;
        var toastHTML = '<span>Saved</span>' +
            '<a target="_blank" href="' + url +
            '" class="btn-flat toast-action">Open</a>';
        M.toast({
            html: toastHTML,
            displayLength: 4000
        })
    }).catch(function () {
        M.toast({html: 'Something went wrong', displayLength: 3000});
    }).finally(function () {
        button.disabled = false;
    });
};


var load = function (post, use_json) {
    return new Promise(function (resolve) {
        placeObjectsFromPost(post, use_json, resolve);
    });
};


var reset = function (post) {
    var button = document.getElementById('reset');
    button.disabled = true;
    return new Promise(function (resolve) {
        placeObjectsFromPost(post, false, resolve);
    }).then(function () {
        button.disabled = false;
        M.toast({html: 'Reset', displayLength: 1000})
    });
};

axios.get('/post/' + window.post_id + '/').then(function (response) {
    window.post = response.data;
    document.getElementById('render_name').value = window.post.name_en.toLowerCase().replace(/\s/gi, '_');
    load(response.data, true).then(function () {
        setHooks();
        M.toast({html: 'Project loaded', displayLength: 1000})
    });
}).catch(function (reason) {
    console.log(reason);
});