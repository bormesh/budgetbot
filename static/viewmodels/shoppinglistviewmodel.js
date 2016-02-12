function ShoppingItem (data){

    var self = this;

    self.item = ko.observable(data.item);
    self.store = ko.observable(data.store);
    self.shopping_category = ko.observable(data.shopping_category);
    self.inserted = ko.observable(data.inserted);

    self.ready_to_add = ko.computed(function(){
         return self.item() && self.store();
    });

};


function ShoppingListViewModel (data) {
    var self = this;

    self.shopping_items = ko.observableArray([]);
    self.store_options = ko.observableArray([]);

    self.is_saving = ko.observable(false);
    self.is_busy = ko.observable(false);


    self.initialize = function(){
        self.is_busy(true);

        return (self.get_all_store_options().then(self.get_all_items).then(function(){
          self.is_busy(false);
        }));
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
                self.store_options(data.stores);
            },

            failure: function(data)
            {
                toastr.alert("failure!")
            }
        });
    };

    self.get_all_items = function(){

        return $.ajax({
            url:"/api/shopping-list",
            type: "GET",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
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



    self.add_item = function(item) {
        self.shopping_items.push(self.item_to_add());
        self.item_to_add(new ShoppingItem({}));


        /*

        $.ajax({
            url:"/add-item",
            type: "POST",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            data: ko.toJSON(item),

            success: function (data) {
                // Recaculate new totals
                console.log(data);

                self.items.add(item);
                display_news_message('Shopping List deleted!','alert-success')
            },

            failure: function(data)
            {
                alert("failure!")
            }


        });
        */
    };

    self.delete_item = function(item) {

        $.ajax({
            url:"/delete-item",
            type: "POST",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            data: ko.toJSON(expense),

            success: function (data) {
                // Recaculate new totals
                console.log(data);

                var new_amount_spent = (
                self.amount_spent() -
                    parseInt(expense.amount()));

                self.amount_spent(new_amount_spent);
                self.expenses.remove(expense);
                display_news_message('Expense deleted!','alert-success')
            },

            failure: function(data)
            {
                alert("failure!")
            }


        });
    };
}






