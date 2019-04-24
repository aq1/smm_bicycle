new Vue({
    el: '#app',
    data: {
        submitIsInProgress: false,
        url: '/api/post/',
        post: {
            account: '',
            name: '',
            artstation: '',
            instagram: '',
            old_work_year: '',
            old_work_url: '',
            new_work_year: '',
            new_work_url: '',
            text_en: '',
            text_ru: ''
        },
        old_work: '',
        new_work: '',
        form_is_valid: true,
        post_errors: {
            name: '',
            artstation: '',
            instagram: '',
            old_work_year: '',
            old_work_url: '',
            new_work_year: '',
            new_work_url: '',
            text_en: ''
        }
    },
    created: function () {
        var view = this;
        this.post.account = window.account_id;

        document.addEventListener('DOMContentLoaded', function () {
            ['old-work-card', 'new-work-card'].forEach(function (id) {
                var dropArea = document.getElementById(id);
                ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function (eventName) {
                    dropArea.addEventListener(
                        eventName,
                        function preventDefaults(e) {
                            e.preventDefault();
                            e.stopPropagation()
                        },
                        false
                    );
                });
                ['dragenter', 'dragover'].forEach(function (eventName) {
                    dropArea.addEventListener(
                        eventName,
                        function highlight() {
                            dropArea.classList.add('highlight');
                        },
                        false
                    );
                });
                ['dragleave', 'drop'].forEach(function (eventName) {
                    dropArea.addEventListener(
                        eventName,
                        function highlight() {
                            dropArea.classList.remove('highlight');
                        },
                        false
                    );
                });
                dropArea.addEventListener(
                    'drop',
                    function handle(e) {
                        view.setFile(
                            {target: {files: e.dataTransfer.files}},
                            id.slice(0, 8).replace('-', '_')
                        );
                    },
                    false
                );
            });
        });
    },
    methods: {
        validate: function () {
            // I bet there is a better way to do it
            var valid = true;

            this.post_errors.name = '';
            if (!this.post.name) {
                this.post_errors.name = 'Name is required';
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
                    this.url,
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
                            view.url + response.data.id + '/',
                            formData,
                            {
                                headers: {'X-CSRFToken': window.csrf_token},
                                params: {'t': token}
                            }
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
