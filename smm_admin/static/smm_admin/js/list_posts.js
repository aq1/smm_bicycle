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
        cleanPosts: function (posts) {
            var _posts = [];
            var view = this;
            posts.forEach(function (post) {
                post.status = view.STATUSES[post.status];
                // post.schedule = new Date(post.schedule).toLocaleDateString();
                _posts.push(post);
            });
            return _posts;
        },
        getPosts: function (page) {
            var view = this;
            view.wip = true;
            page = page ? page : 1;

            axios.get(
                '/api/posts/',
                {params: {'page': page}}
            ).then(function (response) {
                view.posts = view.cleanPosts(response.data.results);
                view.count = response.data.count;
                view.page = page;
            }).catch(function () {
                alert('We did not expect this. Maybe server is down?');
            }).finally(function () {
                view.wip = false;
            });
        }
    },
    created: function () {
        this.getPosts();
    },
    updated: function () {
        M.Materialbox.init(document.querySelectorAll('.materialboxed'), {});
        var now = new Date();

        this.posts.forEach(function (post) {
            M.Datepicker.init(
                document.querySelectorAll('#date_' + post.id),
                {
                    autoClose: true,
                    firstDay: 1,
                    defaultDate: new Date(post.schedule),
                    setDefaultDate: true,
                    minDate: now,
                    showClearBtn: true
                }
            );
        });
    }
});
