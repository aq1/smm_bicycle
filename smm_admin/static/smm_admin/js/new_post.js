new Vue({
    el: '#app',
    data: {
        submitIsInProgress: false,
        post: {
            links: [{}],
            old_work: {},
            new_work: {}
        },
        old_work: '',
        new_work: '',
        form_is_valid: true,
        post_errors: {
            old_work: {
                year: '',
                url: ''
            },
            new_work: {
                year: '',
                url: ''
            }
        }
    },
    methods: {
        validate: function () {
            // I bet there is a better way to do it
            var valid = true;

            this.post_errors.name_en = '';
            if (!this.post.name_en) {
                this.post_errors.name_en = 'This field is required';
                valid = false;
            }

            this.post_errors.links = '';
            if (!this.post.links[0].value) {
                this.post_errors.links = 'At least one link is required';
                valid = false;
            }

            this.post_errors.old_work.year = '';
            this.post_errors.old_work.url = '';
            if (!this.post.old_work.year || isNaN(this.post.old_work.year)) {
                this.post_errors.old_work.year = 'Number is required here';
                valid = false;
            }

            if (!(this.post.old_work.url || this.old_work)) {
                this.post_errors.old_work.url = 'URL required if no file selected.';
                valid = false;
            }

            this.post_errors.new_work.year = '';
            this.post_errors.new_work.url = '';
            if (!this.post.new_work.year || isNaN(this.post.new_work.year)) {
                this.post_errors.new_work.year = 'Number is required here';
                valid = false;
            }

            if (!(this.post.new_work.url || this.new_work)) {
                this.post_errors.new_work.url = 'URL required if no file selected.';
                valid = false;
            }

            return valid;
        },
        submit: function (redirectToImageEditPage) {
            this.form_is_valid = this.validate();
            if (!this.form_is_valid) {
                return;
            }
            var view = this;
            view.submitIsInProgress = true;

            view.post.tags = [];
            M.Chips.getInstance(
                document.getElementById('tags')
            ).chipsData.forEach(
                function (chip) {
                    view.post.tags.push(chip.tag);
                }
            );
            this.post.tags = this.post.tags.join(' ');

            this.post.schedule = M.Datepicker.getInstance(document.getElementById('schedule_date')).date || '';
            if (this.post.schedule) {
                var time = M.Timepicker.getInstance(document.getElementById('schedule_time'));
                if (time.hours && time.minutes)
                this.post.schedule.setHours(time.hours);
                this.post.schedule.setMinutes(time.minutes);
            }

            axios.post(
                '/new/',
                this.post,
                {headers: {'X-CSRFToken': window.csrf_token}}
            ).then(function (response) {
                var post_id = response.data.post_id;

                if (view.old_work || view.new_work) {
                    //    upload files
                    var formData = new FormData();
                    if (view.old_work) {
                        formData.append('old_work', view.old_work);
                    }
                    if (view.new_work) {
                        formData.append('new_work', view.new_work);
                    }
                    axios.post(
                        '/new/' + post_id + '/upload_files/',
                        formData,
                        {
                            headers: {'X-CSRFToken': window.csrf_token},
                            params: {'t': token}
                        }
                    ).then(
                        function (response) {
                            if (redirectToImageEditPage) {
                                window.location = '/p/' + response.data.post_id + '/edit_image/';
                            } else {
                                window.location = '/p/' + response.data.post_id + '/';
                            }
                        }
                    ).catch(function () {
                            alert('Something went wrong. We are terribly sorry.');
                        }
                    ).finally(function () {
                        view.submitIsInProgress = false;
                    });
                } else {
                    view.submitIsInProgress = false;
                }
            }).catch(function () {
                alert('Something went wrong. We are terribly sorry.');
                view.submitIsInProgress = false;
            })
        },
        setFile: function (event, work) {
            console.log(this.form_is_valid);
            this[work] = event.target.files[0];
        },
        linksInputChanged: function (index) {
            for (var i = 0; i < this.post.links.length - 1; i++) {
                if (!this.post.links[i].value) {
                    this.post.links.splice(i, 1);
                    return;
                }
            }

            if (this.post.links[i].value) {
                this.post.links.push({value: ''});
            }
        }
    }
});
