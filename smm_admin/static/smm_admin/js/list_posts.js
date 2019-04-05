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
        cleanPosts: function(posts) {
            var _posts = [];
            var view = this;
            posts.forEach(function(post) {
                post.status = view.STATUSES[post.status];
                post.schedule = new Date(post.schedule).toLocaleDateString();
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
            ).then(function(response) {
                view.posts = view.cleanPosts(response.data.results);
                view.count = response.data.count;
                view.page = page;
            }).catch(function() {
                alert('We did not expect this. Maybe server is down?');
            }).finally(function () {
                view.wip = false;
            });
        }
    },
    created: function() {
        this.getPosts();
    }
});
