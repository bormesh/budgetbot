"use strict";

/* Got execute on enter from :
   http://stackoverflow.com/questions/23087721/call-function-on-enter-key-press-knockout-js

   bind like this

   data-bind="executeOnEnter: sendMessage, button : buttonSelector"
*/

/* Visiblity div fading in and out */
ko.bindingHandlers.fadeVisible = {
    init: function(element, valueAccessor) {
        // Initially set the element to be instantly visible/hidden depending on the value
        var value = valueAccessor();
        $(element).toggle(ko.unwrap(value)); // Use "unwrapObservable" so we can handle values that may or may not be observable
    },
    update: function(element, valueAccessor) {
        // Whenever the value subsequently changes, slowly fade the element in or out
        var value = valueAccessor();
        ko.unwrap(value) ? $(element).fadeIn() : $(element).fadeOut();
    }
};

ko.bindingHandlers.executeOnEnter = {
    init: function (element, valueAccessor, allBindings, viewModel) {
        var options = valueAccessor();

        if (options === undefined)
        {
            return false;
        }
        var callback = options.callback;
        var selector_id = options.selector_id || element;
        $(element).keypress(function (event) {
            var keyCode = (event.which ? event.which : event.keyCode);
            if (keyCode === 13) {
                callback.call(viewModel, selector_id);
                return false;
            }
            return true;
        });
    }
};



ko.bindingHandlers.selected = {
    update: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
        var selected = ko.utils.unwrapObservable(valueAccessor());
        if (selected) element.select();
    }
};


function BudgetBotViewModel (data) {

    var self = this;

    self.type = "BudgetBotViewModel";
    self.is_busy = ko.observable(false);
    self.syslog = ko.observable();

    self.slvm = new ShoppingListViewModel({rootvm: self});
    self.aslvm = new AddShoppingListViewModel({rootvm: self});

    self.uavm = new UserAdminViewModel({rootvm: self})

    self.webapp_session = ko.observable(
        new WebappSession({rootvm: self}));

    self.check_login_status = function () {
        return self.webapp_session().get_session_status();
    };

    self.send_to_login_screen_if_not_logged_in = function () {

        self.check_login_status().then(function () {

            if (!self.user_logged_in()) {
                toastr.error("You have to log in first!");
                pager.navigate("login");
            }
        });

    };

    self.user_logged_in = ko.computed(function () {
        if (self.webapp_session().person_uuid()) {
            return true;
        }
        else {
            return false;
        }
    });

    self.setup_reset_password = function () {
    };

    self.click_on_enter = function(selector_id){

        // click selector button
        //
        if ($('#' + selector_id).attr('disabled') != 'disabled')
        {
            $('#' + selector_id)[0].click();
        }
    };


   /* For the top nav bar, this is where we'll define what
     * links to show */

    self.show_user_admin = ko.computed(function (){
        return false;
    });

};
