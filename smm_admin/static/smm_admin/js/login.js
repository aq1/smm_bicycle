new Vue({
    el: '#app',
    data: {
        submitInProgress: false,
        defaultRedirectURL: '/me/',
        loginFormActive: true,
        required: 'This field is required',
        reg: /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,24}))$/,
        user: {
            username: '',
            password: '',
            passwordConfirm: ''
        },
        userErrors: {
            username: '',
            password: '',
            passwordConfirm: ''
        }
    },
    methods: {
        validateUsername: function () {
            this.userErrors.username = '';
            if (!this.user.username) {
                this.userErrors.username = this.required;
                return false
            }
            if (!this.reg.test(this.user.username)) {
                this.userErrors.username = 'Enter valid email address';
                return false;
            }
            return true;
        },
        validatePassword: function () {
            this.userErrors.password = '';
            if (!this.user.password) {
                this.userErrors.password = this.required;
                return false;
            }
            return true;
        },
        validatePasswordConfirm: function () {
            this.userErrors.passwordConfirm = '';
            if (!this.loginFormActive) {
                if (!this.user.passwordConfirm) {
                    this.userErrors.passwordConfirm = this.required;
                    return false;
                }
                if (this.user.password !== this.user.passwordConfirm) {
                    this.userErrors.passwordConfirm = 'Passwords do not match';
                    return false;
                }
            }
            return true;
        },
        validate: function () {
            // There has to be a better way;
            return this.validateUsername() & this.validatePassword() & this.validatePasswordConfirm();
        },
        submit: function () {
            if (!this.validate()) {
                return;
            }

            this.submitInProgress = true;
            var view = this;
            axios.post(
                '/login/',
                this.user,
                {headers: {'X-CSRFToken': window.csrf_token}}
            ).then(function () {
                window.location.search.substr(1).split('&').forEach(function(query) {
                    var q = query.split('=');
                    if (q[0] === 'next') {
                        location.pathname = q[1];
                    }
                });
                window.location = view.defaultRedirectURL;
            }).catch(function (response) {
                if (response.data) {
                    view.userErrors = response.data;
                } else {
                    view.userErrors.username = 'Wrong credentials';
                }
            }).finally(function() {
                view.submitInProgress = false;
            });
        },
        changeForm: function () {
            this.user.passwordConfirm = '';
            this.userErrors.passwordConfirm = '';
            this.loginFormActive = !this.loginFormActive;
        }
    }
});
