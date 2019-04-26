new Vue({
    el: '#app',
    data: {
        STATUSES: {
            0: 'In Progress',
            1: 'Not Ready',
            2: 'Ready',
            3: 'OK',
            4: 'Failed'
        },
        wip: true,
        pageSize: 20,
        count: 0,
        page: 1,
        filters: {},
        posts: []
    },
    methods: {
        pagesCount: function () {
            return Math.ceil(this.count / this.pageSize);
        },
        getPreview: function (post) {
            return post.previews.rendered_image[100] || post.previews.new_work[100] || post.previews.old_work[100];
        },
        cleanSinglePost: function (post) {
            // post.status = this.STATUSES[post.status];
            post.image = this.getPreview(post);
            post.time = '';
            if (post.schedule) {
                post.schedule = new Date(post.schedule);
                // Goddamit, JS
                var hours = post.schedule.getHours();
                var minutes = post.schedule.getMinutes();
                if (hours < 10) {
                    hours = '0' + hours;
                }
                if (minutes < 10) {
                    minutes = '0' + minutes;
                }
                post.time = hours + ':' + minutes;
            }
            return post;
        },
        cleanPosts: function (posts) {
            var _posts = [];
            var view = this;
            posts.forEach(function (post) {
                _posts.push(view.cleanSinglePost(post));
            });
            return _posts;
        },
        getPosts: function (page) {
            var view = this;
            view.wip = true;
            page = page ? page : 1;

            axios.get(
                '/api/post/',
                {params: {'page': page}}
            ).then(function (response) {
                view.posts = view.cleanPosts(response.data.results);
                view.count = response.data.count;
                view.page = page;
            }).catch(function (e) {
                console.log(e);
                alert('We did not expect this. Maybe server is down?');
            }).finally(function () {
                view.wip = false;
            });
        },
        scheduleChanged: function (post, dateValue) {
            if (dateValue) {
                post.schedule = dateValue;
            }

            if (post.schedule && post.time) {
                var view = this;
                var time = post.time.slice(0, 5).split(':');
                var hours = Number(time[0]);
                var minutes = Number(time[1]);
                if (hours && minutes) {
                    post.schedule.setHours(time[0]);
                    post.schedule.setMinutes(time[1]);
                }
                // Why do I have to do it?
                if (post.scheduleTimeoutId) {
                    clearTimeout(post.scheduleTimeoutId);
                }
                post.scheduleTimeoutId = setTimeout(function () {
                    post.submitting = true;
                    axios.patch(
                        '/api/post/' + post.id + '/',
                        {schedule: post.schedule},
                        {headers: {'X-CSRFToken': window.csrf_token}}
                    ).then(function (response) {
                        for (var i = 0; i < view.posts.length; i++) {
                            console.log(view.posts[i].id, post.id);
                            if (view.posts[i].id === post.id) {
                                view.posts[i] = view.cleanSinglePost(response.data);
                                view.$forceUpdate();  // god damit
                                break;
                            }
                        }
                    }).finally(function () {
                        post.submitting = false;
                    });
                }, 1000);
            }
        }
    },
    created: function () {
        this.getPosts();
    },
    updated: function () {
        var now = new Date();
        var view = this;

        this.posts.forEach(function (post) {
            M.Datepicker.init(
                document.querySelectorAll('#date_' + post.id),
                {
                    autoClose: true,
                    firstDay: 1,
                    defaultDate: post.schedule || '',
                    format: 'yyyy.mm.dd',
                    setDefaultDate: Boolean(post.schedule),
                    minDate: now,
                    showClearBtn: true,
                    onSelect: function (value) {
                        view.scheduleChanged(post, value);
                    }
                }
            );
            new Cleave('#time_' + post.id, {
                time: true,
                timePattern: ['h', 'm']
            });
        });
    }
});
