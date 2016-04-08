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

    /*
    self.getLocation = function () {
        self.error('getting location');
        self.error(navigator.geolocation);
        if (navigator.geolocation.getCurrentPosition) {
            navigator.geolocation.getCurrentPosition(self.setPosition);
        } else {
            self.error("Geolocation is not supported by this browser.");
        }
    };

    self.setPosition = function(position) {
        self.error('got to set position');
        self.lat(position.coords.latitude);
        self.lon(position.coords.longitude);
    };*/


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
                self.item_to_add(new ShoppingItem({}));
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






