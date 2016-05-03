function AddUserShoppingListViewModel (data) {
    var self = this;

    self.is_busy = ko.observable(false);

    self.rootvm = data.rootvm;
    self.shopping_list_id = ko.observable();
    self.shopping_list = ko.observable(new ShoppingList({});


    self.initialize = function(){
        self.is_busy(true);

        console.log('shopping list id is ', self.shopping_list_id());
        self.shopping_list(new ShoppingList({'shopping_list_id':self.shopping_list_id()));
        self.shopping_list.look_up_deets();

        self.is_busy(false);
    };

    self.name_or_email = ko.observable();
    self.no_results_message = ko.observable(false);
    self.search_results = ko.observableArray([]);

    self.search_button_disabled = ko.computed(function(){
        return self.is_busy() || !self.name_or_email();
    });

    self.show_results_table = ko.computed(function(){
        return self.search_results().length > 0;
    });

    self.add_user_to_shopping_list = function(user) {

        self.is_busy(true);

        console.log('adding user uuid: ', user.person_uuid());

        $.ajax({
            url:"/api/insert-shopping-list-user",
            type: "POST",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            data: {'person_uuid':user.person_uuid(),
                'shopping_list_id':self.shopping_list_id()},

            success: function (data) {
                // Recaculate new totals
                console.log(data);

            },
            failure: function(data){
                alert("failure!");
            },
            complete: function(data){
                self.is_busy(false);
            }
        });
    };

    self.user_search = function(){

        self.is_busy(true);
        self.no_results_message(false);

        $.ajax({
            url:"/api/user-search",
            type: "GET",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            data: {'search_query':self.name_or_email()},
            success: function (data) {
                // Recaculate new totals
                console.log(data);
                if(data.num_results > 0){
                    self.search_results(ko.utils.arrayMap(data.search_results,
                    function(p){
                        x = new Person(p);
                        console.log(x);
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

