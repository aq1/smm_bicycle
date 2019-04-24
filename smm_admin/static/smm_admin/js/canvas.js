fabric.Object.prototype.set({
    transparentCorners: false,
    borderColor: '#ff38ae',
    cornerColor: '#ff0000',
    cornerSize: 20
});

window.initWidth = 1920;
window.initHeight = 1080;

var grid = 10;
window.textFills = ['#000', '#fff', '#BFBFBF'];
window.selectedTexts = [];

var canvas = new fabric.Canvas('canvas', {
    preserveObjectStacking: true,
    width: window.initWidth,
    height: window.initHeight
});


var _resizeCanvas = function(w, h) {
    canvas.setWidth(w);
    canvas.setHeight(h);
    canvas.calcOffset();
    resizeDivWrapper();
};

var resizeCanvas = function () {
    var w = Number(document.getElementById('canvas_width').value);
    var h = Number(document.getElementById('canvas_height').value);
    if (!(w && h)) {
        return;
    }
    _resizeCanvas(w, h);
    M.Modal.getInstance(document.getElementById('resize-modal')).close();
};


var setSizeValueInModal = function () {
    document.getElementById('canvas_width').value = canvas.getWidth();
    document.getElementById('canvas_height').value = canvas.getHeight();
};

(function setHooks() {
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

})();

var addYearToImage = function (image, year) {
    var year_text = new fabric.IText(year.toString(), {
        left: image.left + grid * 2,
        top: image.top + grid * 2,
        fontFamily: 'Intro',
        fill: window.textFills[2],
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

    _resizeCanvas(window.initWidth, window.initHeight);

    canvas.backgroundColor = window.textFills[2];

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

        var place_text = function (x_offset) {
            var name = new fabric.IText(post.name, {
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

            var artstation = post.artstation.replace(/\/$/, '').split('/');
            artstation = 'artstation/' + artstation[artstation.length - 1];

            var links_text = [artstation];
            if (post.instagram) {
                var instagram = post.instagram.replace(/\/$/, '').split('/');
                links_text.push('@' + instagram[instagram.length - 1]);
            }

            var links = new fabric.IText(links_text.join('\n'), {
                left: x_offset + grid * 2,
                top: text.top + text.getScaledHeight() + grid,
                fontFamily: 'Myriad Pro',
                fontSize: 19,
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
        });
        var link = document.getElementById('open_rendered');
        link.style.visibility = 'visible';
        link.href = url;
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

axios.get('/api/posts/' + window.post_id + '/').then(function (response) {
    window.post = response.data;
    document.getElementById('render_name').value = window.post.name.toLowerCase().replace(/\s/gi, '_');
    load(response.data, true).then(function () {
        M.toast({html: 'Project loaded', displayLength: 1000})
    });
}).catch(function (reason) {
    console.log(reason);
});


var resizeDivWrapper = function () {
    var div = document.getElementById('canvas-wrapper');
    div.style.width = canvas.getWidth() + 10 + 'px';
    div.style.height = canvas.getHeight() + 10 + 'px';
};

document.addEventListener('DOMContentLoaded', function () {
    resizeDivWrapper();
    interact('#canvas-wrapper').resizable({
        inertia: false,
        edges: {
            left: false,
            right: true,
            bottom: true,
            top: false
        },
        modifiers: [
            // keep the edges inside the parent
            interact.modifiers.restrictEdges({
                outer: 'parent',
                endOnly: true
            }),

            // minimum size
            interact.modifiers.restrictSize({
                min: {width: 1000, height: 500}
            })
        ]
    }).on('resizemove', function (event) {
        _resizeCanvas(Math.round(event.rect.width), Math.round(event.rect.height));
    });
});
