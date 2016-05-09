"use strict";

function BudgetBotViewModel (data) {

    var self = this;

    self.type = "BudgetBotViewModel";
    self.is_busy = ko.observable(false);
    self.syslog = ko.observable();

    self.slvm = new ShoppingListViewModel({rootvm: self});
    self.aslvm = new AddShoppingListViewModel({rootvm: self});
    self.aduslvm = new AddUserShoppingListViewModel({rootvm: self});

    self.expensetrackvm = new ExpenseTrackViewModel({rootvm: self});

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
