var grid = 10;

var canvas = new fabric.Canvas('canvas', {
    preserveObjectStacking: true
});

var getMaxWidth = function () {
    return document.getElementById('canvas-wrapper').offsetWidth;
};

var resizeCanvas = function () {
    var topX = 0;
    var topY = 0;
    var selectedGroup = canvas.getActiveObject();

    canvas.getObjects().forEach(function (obj) {
        topX = Math.max(obj.left + obj.getScaledWidth(), topX);
        topY = Math.max(obj.top + obj.getScaledHeight(), topY);
    });

    if (selectedGroup) {
        topX = Math.max(selectedGroup.left + selectedGroup.getScaledWidth(), topX);
        topY = Math.max(selectedGroup.top + selectedGroup.getScaledHeight(), topY);
    }

    topX += grid;
    canvas.setWidth(Math.min(topX, getMaxWidth() - grid));
    canvas.setHeight(Math.round(topY + grid));
    canvas.calcOffset();
};

canvas.setWidth(getMaxWidth());
canvas.setHeight(Math.round(window.innerHeight * 0.8));
canvas.calcOffset();

var setHooks = function () {
    canvas.off('object:modified');
    canvas.off('object:added');
    canvas.on('object:modified', function (options) {
        resizeCanvas();
    });
    canvas.on('object:added', function (options) {
        resizeCanvas();
    });
    window.onresize = resizeCanvas;

    // http://jsfiddle.net/fabricjs/S9sLu/
    canvas.on('object:moving', function (options) {
        options.target.set({
            left: Math.round(options.target.left / grid) * grid,
            top: Math.round(options.target.top / grid) * grid
        });
    });

};

var add_year_to_image = function (image, year) {
    var year_text = new fabric.IText(year.toString(), {
        left: image.left + grid * 2,
        top: image.top + grid * 2,
        fontFamily: 'Intro',
        fill: 'white',
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

    canvas.backgroundColor = '#BFBFBF';

    fabric.Image.fromURL(post.old_work, function (old_work_img) {
        old_work_img.top = grid;
        old_work_img.left = grid;
        old_work_img.scaleToHeight(Math.round(window.innerHeight / 2));
        canvas.add(old_work_img);

        add_year_to_image(old_work_img, post.old_work_year);

        fabric.Image.fromURL(post.new_work, function (new_work_img) {
            new_work_img.top = grid;
            new_work_img.left = old_work_img.getScaledWidth() + grid * 2;
            new_work_img.scaleToHeight(Math.round(window.innerHeight / 2));
            canvas.add(new_work_img);

            add_year_to_image(new_work_img, post.new_work_year);
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
                fontSize: 30
            });
            canvas.add(name);

            var text = new fabric.IText(post.text_en, {
                left: x_offset + grid * 2,
                top: name.top + name.getScaledHeight() + grid,
                fontFamily: 'Intro',
                fontSize: 15
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
                fontSize: 13
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


var renderCanvas = function(maxWidth, maxHeight) {
    var initWidth = canvas.width;
    var initHeight = canvas.height;
    var minScaleX = maxWidth / initWidth;
    var minScaleY = maxHeight / initHeight;
    var imagesFound = 0;  // wow this is fucked up
    canvas.getObjects().forEach(function(obj) {
        imagesFound += 1;
        if (imagesFound === 3) {
            return;
        }

        if (obj.type !== 'image' || obj.name === 'logo') {
            return;
        }

        minScaleX = Math.min(minScaleX, obj.width / obj.getScaledWidth());
        minScaleY = Math.min(minScaleX, obj.height / obj.getScaledHeight());
    });
    var minScale = Math.min(minScaleX, minScaleY);
    canvas.setZoom(minScale);
    var topX = 0;
    var topY = 0;
    for (var i = 0; i < canvas.size(); i++) {
        topX = Math.max(topX, canvas.item(i).oCoords.br.x);
        topY = Math.max(topY, canvas.item(i).oCoords.br.y);
    }
    canvas.setWidth(topX + grid * minScale);
    canvas.setHeight(topY + grid * minScale);
    var data = canvas.toDataURL();

    canvas.setZoom(1);
    canvas.setWidth(initWidth);
    canvas.setHeight(initHeight);

    return data;
};


var render = function () {
    var width = document.getElementById('render_width').value;
    var height = document.getElementById('render_height').value;
    var render_name = document.getElementById('render_name').value;
    if (!(Number(width) && Number(height))) {
        return;
    }
    var button = document.getElementById('render');
    button.disabled = true;

    axios.post(
        '/post/' + window.post_id + '/save_render/',
        renderCanvas(width, height),
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
    }).catch(function() {
        M.toast({html: 'Something went wrong', displayLength: 3000})
    }).finally(function() {
        button.disabled = false;
    });
};


var load = function(post, use_json) {
    return new Promise(function(resolve) {
        placeObjectsFromPost(post, use_json, resolve);
    });
};


var reset = function(post) {
    var button = document.getElementById('reset');
    button.disabled = true;
    return new Promise(function(resolve) {
        placeObjectsFromPost(post, false, resolve);
    }).then(function() {
        button.disabled = false;
        M.toast({html: 'Reset', displayLength: 1000})
    });
};

axios.get('/post/' + window.post_id + '/').then(function (response) {
    window.post = response.data;
    document.getElementById('render_name').value = window.post.name_en.toLowerCase().replace(/\s/gi, '_');
    load(response.data, true).then(function() {
        setHooks();
        M.toast({html: 'Project loaded', displayLength: 1000})
    });
}).catch(function (reason) {
    console.log(reason);
});
