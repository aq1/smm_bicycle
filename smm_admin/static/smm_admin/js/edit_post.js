new Vue({
    el: '#app',
    data: {
        submitIsInProgress: false,
        url: '/api/post/',
        post_id: window.post_id,
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
            text_ru: '',
            tags: '#3d #cg #art #artwork #10khourslater #10khourslater_3d #progress #environment'
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
        this.post_id = window.post_id;

        if (this.post_id) {
            axios.get(this.url + this.post_id + '/').then(function(response) {
                view.post = response.data;
            }).catch(function() {
                alert('Could not get the post');
            });
        }

        document.addEventListener('DOMContentLoaded', function () {
            var tags = [];
            view.post.tags.split(' ').forEach(function (_tag) {
                tags.push({tag: _tag});
            });
            var instance = M.Chips.init(document.querySelectorAll('.chips'), {
                data: tags,
                placeholder: 'Tags',
                secondaryPlaceholder: 'Add more tags...',
                onChipDelete: function (_, chip) {
                    var tag = chip.innerText.replace(/close$/, '');
                    view.post.tags = view.post.tags.replace(tag, '').replace('  ', ' ');
                }
            })[0];

            // I don't know JS, okay?
            var addChip = instance.addChip;
            instance.addChip = function (chip) {
                if (chip.tag[0] !== '#') {
                    chip.tag = '#' + chip.tag;
                }
                var r = new RegExp('\\s?' + chip.tag + '\\s?');
                if (view.post.tags.match(r)) {
                    return;
                }
                addChip.apply(instance, [chip]);
                view.post.tags += ' ' + chip.tag;
            };

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
            console.log(this.post.tags);
            this.form_is_valid = this.validate();
            if (this.form_is_valid) {
                var view = this;
                view.submitIsInProgress = true;

                var httpRequest = axios.post;
                var url = this.url;
                if (this.post_id) {
                    httpRequest = axios.patch;
                    url = this.url + this.post_id + '/';
                }

                httpRequest(
                    url,
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
                        var patchUrl = url;
                        if (!view.post_id) {
                            patchUrl = view.url + response.data.id + '/';
                        }
                        axios.patch(
                            patchUrl,
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
