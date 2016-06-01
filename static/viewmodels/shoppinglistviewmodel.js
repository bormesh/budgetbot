function ShoppingItem (data){

    var self = this;

    self.item = ko.observable(data.item);
    self.inserted = ko.observable(data.inserted);

    self.shopping_list_id = ko.observable(data.shopping_list_id);

    self.ready_to_add = ko.computed(function(){
         return self.item();
    });

};

function ShoppingList (data){

    var self = this;

    self.shopping_list_id = ko.observable(data.shopping_list_id);
    self.shopping_list_name = ko.observable(data.shopping_list_name);
    self.store = ko.observable(data.store);

    self.inserted = ko.observable(data.inserted);

    self.ready_to_add = ko.computed(function(){
         return self.shopping_list_name() && self.store();
    });

    /* AJAX look up of name and store etc */
    self.look_up_deets = function(){


        return $.ajax({
            url:"/api/shopping-list-deets",
            type: "GET",
            data:{'shopping_list_id':self.shopping_list_id()},
            success: function (data) {

                if(data.success == true){
                   console.log('shopping list deets ', data);

                   // Update our data
                   self.shopping_list_name(data.deets.shopping_list_name);
                   self.store(data.deets.store);
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
    }
};

function AddShoppingListViewModel (data) {
    var self = this;

    self.shopping_lists = ko.observableArray([]);
    self.shared_shopping_lists = ko.observableArray([]);
    self.store_options = ko.observableArray([]);

    self.is_saving = ko.observable(false);
    self.is_busy = ko.observable(false);

    self.initialize = function(){
        self.is_busy(true);

        return (self.get_all_store_options().then(self.get_all_lists).then(function(){
          self.is_busy(false);
          // Set up an interval to long poll for new items
        }));
    };

    self.list_to_add = ko.observable(new ShoppingList({}));

    self.add_button_disabled = ko.computed(function(){
        return self.is_busy() || (!self.list_to_add().ready_to_add());
    });

    /* Use this to use jquery slide up on element */
    self.get_all_store_options = function(){

        return $.ajax({
            url:"/api/all-stores",
            type: "GET",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            success: function (data) {
                // Recaculate new totals
                //
                if(data.success == true){
                    self.store_options(data.stores);
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

    self.get_all_lists = function(){

        return $.ajax({
            url:"/api/shopping-lists",
            type: "GET",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            success: function (data) {
                // Recaculate new totals
                self.shopping_lists(
                    ko.utils.arrayMap(
                    data.lists,
                    function (p) {
                        x = new ShoppingList(p);
                        return x;
                }));

                self.shared_shopping_lists(
                    ko.utils.arrayMap(
                    data.shared_lists,
                    function (p) {
                        x = new ShoppingList(p);
                        return x;
                }));

            },

            failure: function(data)
            {
                toastr.alert("failure!")
            }
    })};


    self.add_list = function() {

        self.is_busy(true);

        $.ajax({
            url:"/api/insert-shopping-list",
            type: "POST",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            data: ko.toJSON(self.list_to_add()),

            success: function (data) {
                // Recaculate new totals
                console.log(data);

                self.list_to_add().shopping_list_id(data.shopping_list_id);
                self.shopping_lists.push(self.list_to_add());
                self.list_to_add(new ShoppingItem({}));
            },
            failure: function(data){
                alert("failure!");
            },
            complete: function(data){
                self.is_busy(false);
            }
        });

    };

    self.delete_list = function(list) {

        console.log('deleting ', list);

        $.ajax({
            url:"/api/delete-shopping-list",
            type: "POST",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            data: ko.toJSON(list),

            success: function (data) {
                // Recaculate new totals
                self.shopping_lists.remove(list);
            },

            failure: function(data)
            {
                alert("failure!")
            }


        });
    };
}


function ShoppingListViewModel (data) {
    var self = this;

    /* This should come in on the params */
    self.shopping_list_id = ko.observable();

    self.shopping_list = ko.observable(new ShoppingList({}));

    self.shopping_items = ko.observableArray([]);
    self.store_options = ko.observableArray([]);

    self.is_saving = ko.observable(false);
    self.is_busy = ko.observable(false);

    self.interval_timer = null;

    self.initialize = function(){
        self.is_busy(true);

        self.shopping_items.removeAll();

        //If the timers not null, null it out
        if(self.interval_timer != null){
            console.log('clearing interval');
            clearInterval(self.interval_timer);
            self.interval_timer = null;
        }

        console.log(self.shopping_list_id());

        console.log(self.interval_timer);
        self.shopping_list(new ShoppingList({'shopping_list_id':self.shopping_list_id()}));

        self.item_to_add(new ShoppingItem({shopping_list_id:self.shopping_list_id()}));



        return (self.shopping_list().look_up_deets().then(
            self.get_all_store_options().then(self.get_all_items).then(function(){
              self.is_busy(false);
              // Set up an interval to long poll for new items
              self.interval_timer =  setInterval(function(){

                  self.get_all_items();
                  // If we're not longer on this page, then clear out
                  // timer
                  if(pager.getActivePage().currentId != "shopping-list"){
                      clearInterval(self.interval_timer);
                      self.interval_timer = null;
                      console.log('cleared interval timer ', self.interval_timer);
                  }
              }, 30000);
            })));
    };

    self.item_to_add = ko.observable(new ShoppingItem({}));

    self.add_button_disabled = ko.computed(function(){
        return self.is_busy() || (!self.item_to_add().ready_to_add());
    });

    self.get_all_store_options = function(){

        return $.ajax({
            url:"/api/all-stores",
            type: "GET",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            success: function (data) {
                // Recaculate new totals
                //
                if(data.success == true){
                    self.store_options(data.stores);
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

    self.get_all_items = function(){

        return $.ajax({
            url:"/api/shopping-list-items",
            type: "GET",
            data:{ shopping_list_id: self.shopping_list_id()},
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                // Recaculate new totals
                self.shopping_items(
                    ko.utils.arrayMap(
                    data.items,
                    function (p) {
                        x = new ShoppingItem(p);
                        return x;
                }));
            },

            failure: function(data)
            {
                toastr.alert("failure!")
            }
    })};


    self.add_item = function() {

        self.is_busy(true);

        $.ajax({
            url:"/api/insert-shopping-item",
            type: "POST",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            data: ko.toJSON(self.item_to_add()),

            success: function (data) {
                // Recaculate new totals
                console.log(data);

                self.shopping_items.push(self.item_to_add());
                self.item_to_add(new ShoppingItem(
                    {shopping_list_id:self.shopping_list_id()}));
            },
            failure: function(data){
                alert("failure!");
            },
            complete: function(data){
                self.is_busy(false);
            }
        });

    };

    self.delete_item = function(item) {

        console.log('deleting item');

        $.ajax({
            url:"/api/delete-shopping-item",
            type: "POST",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            data: ko.toJSON(item),

            success: function (data) {
                // Recaculate new totals
                self.shopping_items.remove(item);
            },

            failure: function(data)
            {
                alert("failure!")
            }


        });
    };
}






