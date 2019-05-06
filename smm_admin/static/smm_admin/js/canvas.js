fabric.Object.prototype.set({
    transparentCorners: false,
    borderColor: '#ff38ae',
    cornerColor: '#ff0000',
    cornerSize: 20
});

var config = {
    grid: 10,
    initWidth: 1920,
    initHeight: 1080,
    minWidth: 1000,
    minHeight: 500,
    textFills: ['#000', '#fff', '#BFBFBF']
};

window.selectedTexts = [];

var canvas = new fabric.Canvas('canvas', {
    preserveObjectStacking: true,
    width: config.initWidth,
    height: config.initHeight
});


var _resizeCanvas = function (w, h) {
    canvas.setWidth(w);
    canvas.setHeight(h);
    canvas.calcOffset();
    setSizeValueInInput();
    resizeDivWrapper();
};

var resizeCanvas = function () {
    var w = Number(document.getElementById('canvas_width').value);
    var h = Number(document.getElementById('canvas_height').value);
    if (!(w && h)) {
        return;
    }
    if (w < config.minWidth) {
        w = config.minWidth;
    }
    if (h < config.minHeight) {
        h = config.minHeight;
    }
    _resizeCanvas(w, h);
    M.Modal.getInstance(document.getElementById('resize-modal')).close();
};


var setSizeValueInInput = function () {
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
                var fillIndex = (config.textFills.indexOf(text.fill) + 1);
                text.set({
                    fill: config.textFills[fillIndex % config.textFills.length]
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
            left: Math.round(options.target.left / config.grid) * config.grid,
            top: Math.round(options.target.top / config.grid) * config.grid
        });
    });

})();

var addYearToImage = function (image, year) {
    var year_text = new fabric.IText(year.toString(), {
        left: image.left + config.grid * 2,
        top: image.top + config.grid * 2,
        fontFamily: 'Intro',
        fill: config.textFills[2],
        fontSize: Math.round(config.innerWidth / 50)
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

    _resizeCanvas(config.initWidth, config.initHeight);

    canvas.backgroundColor = config.textFills[2];

    fabric.Image.fromURL(post.old_work, function (old_work_img) {
        old_work_img.top = config.grid;
        old_work_img.left = config.grid;
        old_work_img.scaleToHeight(Math.round(config.innerHeight / 2));
        canvas.add(old_work_img);

        addYearToImage(old_work_img, post.old_work_year);

        fabric.Image.fromURL(post.new_work, function (new_work_img) {
            new_work_img.top = config.grid;
            new_work_img.left = old_work_img.getScaledWidth() + config.grid * 2;
            new_work_img.scaleToHeight(Math.round(config.innerHeight / 2));
            canvas.add(new_work_img);

            addYearToImage(new_work_img, post.new_work_year);
            if (post.account.logo) {
                fabric.Image.fromURL(post.account.logo, function (logo_img) {
                    logo_img.top = old_work_img.getScaledHeight() + config.grid * 2;
                    logo_img.left = config.grid;
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
                left: x_offset + config.grid * 2,
                top: old_work_img.getScaledHeight() + config.grid * 2,
                fontFamily: 'Intro',
                fontSize: 30,
                fill: config.textFills[0]
            });
            canvas.add(name);

            var text = new fabric.IText(post.text_en, {
                left: x_offset + config.grid * 2,
                top: name.top + name.getScaledHeight() + config.grid,
                fontFamily: 'Intro',
                fontSize: 15,
                fill: config.textFills[0]
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
                left: x_offset + config.grid * 2,
                top: text.top + text.getScaledHeight() + config.grid,
                fontFamily: 'Myriad Pro',
                fontSize: 19,
                fill: config.textFills[0]
            });
            canvas.add(links);
            resolve();
        };
    });
};


var saveProject = function () {
    var tab = document.getElementById('save');
    tab.classList.add('disabled');

    axios.post(
        '/post/' + window.post_id + '/save_canvas/',
        JSON.stringify(canvas)
    ).then(function () {
        M.toast({html: 'Saved', displayLength: 1000})
    }).catch(function (reason) {
        console.log(reason);
    }).finally(function () {
        tab.classList.remove('disabled');
    });
};


var setRenderButtons = function (url) {
    url = url || '';
    var a = document.getElementById('open-rendered');
    a.href = url;
    [
        a,
        document.getElementById('delete-rendered')
    ].forEach(function (button) {
        if (url) {
            button.style.visibility = 'visible';
        } else {
            button.style.visibility = 'hidden';
        }
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
        setRenderButtons(url);
    }).catch(function () {
        M.toast({html: 'Something went wrong', displayLength: 3000});
    }).finally(function () {
        button.disabled = false;
    });
};


var deleteRender = function () {
    var button = document.getElementById('delete-render');
    button.disabled = true;

    axios.patch(
        '/api/post/' + window.post_id + '/',
        {'rendered_image': null}
    ).then(function (response) {
        M.Modal.getInstance(document.getElementById('delete-render-modal')).close();
        M.toast({
            html: 'Render deleted',
            displayLength: 4000
        });
        setRenderButtons('');
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


axios.defaults.headers.common = {
    'X-CSRFToken': window.csrf_token
};


axios.get('/api/post/' + window.post_id + '/').then(function (response) {
    window.post = response.data;
    document.getElementById('render_name').value = window.post.name.toLowerCase().replace(/\s/gi, '_');
    setRenderButtons(window.post.rendered_image);
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

    M.Modal.init(document.querySelectorAll('.modal'));

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
                min: {width: config.minWidth, height: config.minHeight}
            })
        ]
    }).on('resizemove', function (event) {
        _resizeCanvas(Math.round(event.rect.width), Math.round(event.rect.height));
    });
});
