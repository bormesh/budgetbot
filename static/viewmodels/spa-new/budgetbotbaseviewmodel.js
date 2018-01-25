function BudgetBotBaseViewModel(data){
    var self = this;
    self.type = "BudgetBotBaseViewModel"

    data.rootvm = this;

    self.syslog = ko.observable();
    self.is_busy = ko.observable(false);
    self.initialized = ko.observable(false);

    self.selected_language = ko.observable('en');
    // Parameter for pages specifically en or de
    self.selected_lang_param = ko.observable();

    /* View Models  -- attach these in document.ready of base  */
    self.createbudgetvm= null;
    //Manage
    self.manageaccountvm = null;

    // Events
    // on state change is custom history.js -- should
    // be compatible with all browsers
    window.onstatechange = function(){
        $('.modal').modal('hide');
    }


    self.webapp_session = ko.observable(
        new WebappSession({rootvm: self}));

    self.initialize = function(){
        self.initialized(true);
    }

    self.check_login_status = function () {
        return self.webapp_session().get_session_status();
    };

    self.maybe_confirm_email = function(){
        var params = {}

        var paramsString = window.location.href.split("?");
        if (paramsString.length > 1){
            paramsString = paramsString[1];

            var paramValues = paramsString.split("&");

            for(var i = 0; i< paramValues.length; i++){
                    paramValue = paramValues[i].split("=");
                    params[paramValue[0]] = paramValue[1];
            }
            if (params.user_confirm){
                self.webapp_session().user().confirm_email(params.user_confirm)
            }
        }

    }

    self.show_confirmed = function(){
        $('#modalUserConfirm').modal('show');
    }

    self.user_logged_in = ko.computed(function () {
        if (self.webapp_session().person_uuid()) {
            return true;
        }
        else {
            return false;
        }
    });

	self.user = ko.computed(function(){
		if(self.user_logged_in()){
			return self.webapp_session().user()
		}
	});

    self.email_address = ko.observable();
    self.password = ko.observable();
    self.display_name = ko.observable()
    self.warning = ko.observable('');
    self.sendnews = ko.observable(true);
    self.conditions = ko.observable();

    self.email_is_valid = ko.computed(function(){
        return validateEmail(self.email_address());
    });


    self.selected_language.subscribe(function(){
        self.change_language(self.selected_language());
    });

    self.signup = function(){

       self.is_busy(true);

       return $.ajax({

            url: self.web_host + '/api/insert-new-user',
            type: 'POST',
            processData: false,
            data: ko.toJSON({
                display_name: self.display_name(),
                email_address:self.email_address(),
                raw_password:self.password(),
                sendnews:self.sendnews(),
                conditions:self.conditions(),
                language: self.selected_language()
            }),

            contentType: "application/json; charset=utf-8",

            success: function (data) {
                if(data.success){
                    self.signed_up(true);
                    if (data.emails){
                        window.open(data.emails[0], "_blank");
                    }
                } else{
                    self.warning(data.translation);
                }
            },
            error: function (data) {
                self.warning('modal.error_signup.email');
            },
            complete: function(){
                self.is_busy(false);
            }
        });

        self.signed_up(true);
    };

    self.send_reset_password = function(){
       self.is_busy(true);

       return $.ajax({

            url: self.web_host + '/api/send-reset-password-email',
            type: 'POST',
            processData: false,
            data: ko.toJSON({
                email_address:self.email_address(),
            }),

            contentType: "application/json; charset=utf-8",

            success: function (data) {
                if(data.success){
                    self.sent_reset_email(true);
                    if (data.emails){
                        window.open(data.emails[0], "_blank");
                    }
                } else{
                    self.warning(data.message);
                }
            },
            error: function (data) {
                self.warning('modal.error_signup.email');
            },
            complete: function(){
                self.is_busy(false);
            }
        });

        self.signed_up(true);


    }

    self.signup_disabled = ko.computed(function(){

        signup_disabled = self.is_busy() ||
            ((self.email_address() == '' ||
                            self.email_address() == undefined) ||
            (self.password() == '' || self.password() == undefined) ||
            (self.display_name() == '' || self.display_name() == undefined) ||
            !self.conditions());

        return signup_disabled;
    });


    self.login = function() {
       self.is_busy(true);
       self.warning('');

       return $.ajax({

            url: self.web_host + '/api/login',
            type: 'POST',
            processData: false,
            data: ko.toJSON({
                email_address:self.email_address(),
                password: self.password()
            }),

            xhrFields: {
                withCredentials: true,
            },

            contentType: "application/json; charset=utf-8",

            success: function (data) {
                if(data.success){
                    self.webapp_session().update_self(data);
                    $('#modalLogin').modal('hide');
                } else{
                    if(data.message == 'Sorry, status is: started registration'){
                        self.warning('modal.welcome.body');
                        console.log(self.warning());
                    }
                    else{
                        self.warning(data.message);
                    }
                }
            },
            error: function (data) {
                self.warning('modal.error_signup.email');
            },
            complete: function(){
                self.is_busy(false);
            }
        });
    }

    self.click_on_enter = function(selector_id){
        if ($('#' + selector_id).attr('disabled') != 'disabled'){
            $('#' + selector_id)[0].click();
        }
    };

};
