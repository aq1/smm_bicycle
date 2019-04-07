new Vue({
    el: '#app',
    data: {
        submitIsInProgress: false,
        post: {
            account: location.pathname.match(/\d/)[0],
            name_en: '',
            artstation: '',
            instagram: '',
            old_work_year: '',
            old_work_url: '',
            new_work_year: '',
            new_work_url: '',
            text_en: ''
        },
        old_work: '',
        new_work: '',
        form_is_valid: true,
        post_errors: {
            name_en: '',
            artstation: '',
            instagram: '',
            old_work_year: '',
            old_work_url: '',
            new_work_year: '',
            new_work_url: '',
            text_en: ''
        }
    },
    methods: {
        validate: function () {
            // I bet there is a better way to do it
            var valid = true;

            this.post_errors.name_en = '';
            if (!this.post.name_en) {
                this.post_errors.name_en = 'Name is required';
                valid = false;
            }

            this.post_errors.artstation = '';
            if (!this.post.artstation || this.post.artstation.search('artstation.com') === -1) {
                this.post_errors.artstation = 'Link to Art Station is required';
                valid = false;
            }

            this.post_errors.old_work_year = '';
            this.post_errors.old_work_url = '';
            if (!this.post.old_work_year || isNaN(this.post.old_work_year)) {
                this.post_errors.old_work_year = 'Year is required here';
                valid = false;
            }

            if (!(this.post.old_work_url || this.old_work)) {
                this.post_errors.old_work_url = 'URL required if no file selected.';
                valid = false;
            }

            this.post_errors.new_work_year = '';
            this.post_errors.new_work_url = '';
            if (!this.post.new_work_year || isNaN(this.post.new_work_year)) {
                this.post_errors.new_work_year = 'Year is required here';
                valid = false;
            }

            if (!(this.post.new_work_url || this.new_work)) {
                this.post_errors.new_work_url = 'URL required if no file selected.';
                valid = false;
            }

            return valid;
        },
        submit: function () {
            this.form_is_valid = this.validate();
            if (this.form_is_valid) {
                var view = this;
                view.submitIsInProgress = true;

                axios.post(
                    '/api/post/',
                    this.post,
                    {headers: {'X-CSRFToken': window.csrf_token}}
                ).then(function (response) {
                    var token = response.data.token;

                    if (view.old_work || view.new_work) {
                        //    upload files
                        var formData = new FormData();
                        if (view.old_work) {
                            formData.append('old_work', view.old_work);
                        }
                        if (view.new_work) {
                            formData.append('new_work', view.new_work);
                        }
                        axios.patch(
                            '/api/post/' + token + '/',
                            formData,
                            {headers: {'X-CSRFToken': window.csrf_token}}
                        ).then(
                            function (response) {
                                location.pathname = '/p/' + token + '/';
                            }
                        ).catch(function () {
                                alert('Something went wrong. We are terribly sorry.');
                            }
                        ).finally(function () {
                            view.submitIsInProgress = false;
                        });
                    } else {
                        location.pathname = '/p/' + token + '/';
                    }
                }).catch(function () {
                    alert('Something went wrong. We are terribly sorry.');
                }).finally(function () {
                    view.submitIsInProgress = false;
                });
            }
        },
        setFile: function (event, work) {
            this[work] = event.target.files[0];
        }
    }
});
