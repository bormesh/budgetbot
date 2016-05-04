function AddUserShoppingListViewModel (data) {
    var self = this;

    self.is_busy = ko.observable(false);

    self.rootvm = data.rootvm;
    self.shopping_list_id = ko.observable();
    self.shopping_list = ko.observable(new ShoppingList({}));


    self.initialize = function(){
        self.is_busy(true);

        console.log('shopping list id is ', self.shopping_list_id());
        self.shopping_list(new ShoppingList({'shopping_list_id':self.shopping_list_id()}));
        return (self.shopping_list().look_up_deets().then(
            self.look_up_shopping_list_users).then(
            function(){
                self.is_busy(false);

        }));

    };

    self.name_or_email = ko.observable();
    self.no_results_message = ko.observable(false);
    self.search_results = ko.observableArray([]);
    self.shopping_list_users = ko.observableArray([]);

    self.search_button_disabled = ko.computed(function(){
        return self.is_busy() || !self.name_or_email();
    });

    self.show_results_table = ko.computed(function(){
        return self.search_results().length > 0;
    });

    self.show_users_table = ko.computed(function(){
        return self.shopping_list_users().length > 0;
    });

    self.look_up_shopping_list_users = function(){

        return $.ajax({
            url:"/api/shopping-list-users",
            type: "GET",
            data:{'shopping_list_id':self.shopping_list_id()},
            success: function (data) {

                if(data.success == true){
                   console.log('shopping list deets ', data);
                    self.shopping_list_users(ko.utils.arrayMap(data.people,
                    function(p){
                        x = new Person(p);
                        console.log(x);
                        return x;
                    }));
                }
                else if (data.success == false && data.needs_to_log_in) {
                    toastr.error(data.message);
                    pager.navigate("login");
                }
                else {
                    toastr.error(data.message);
                    pager.navigate("login");
                }
            },

            failure: function(data)
            {
                toastr.alert("failure!")
            }
        });
    };

    self.add_user_to_shopping_list = function(user) {

        self.is_busy(true);

        $.ajax({
            url:"/api/insert-shopping-list-user",
            type: "POST",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            data: ko.toJSON({'person_uuid':user.person_uuid(),
                'shopping_list_id':self.shopping_list_id()}),
            success: function (data) {
                // Recaculate new totals
                console.log(data);

                if(data.success == true){
                    // Move user to the added people list
                    self.shopping_list_users.push(user);
                    // Remove from current search users
                    self.search_results.remove(user);
                }

            },
            failure: function(data){
                alert("failure!");
            },
            complete: function(data){
                self.is_busy(false);
            }
        });
    };

    self.remove_user_from_shopping_list = function(user){

        console.log('not implemented');


    };

    self.user_search = function(){

        self.is_busy(true);
        self.no_results_message(false);

        $.ajax({
            url:"/api/user-search",
            type: "GET",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            data: {'search_query':self.name_or_email(),
                'shopping_list_id':self.shopping_list_id()},
            success: function (data) {
                // Recaculate new totals
                console.log(data);
                if(data.num_results > 0){
                    self.search_results(ko.utils.arrayMap(data.search_results,
                    function(p){
                        x = new Person(p);
                        return x;
                    }));
                }
                else{
                    self.no_results_message(true);
                    self.search_results.removeAll();
                }
            },
            failure: function(data){
                alert("failure!");
            },
            complete: function(data){
                self.is_busy(false);
            }
        });
    };
};

