function Expense (data) {

    var self = this;

    self.person_uuid = ko.observable(data.person_uuid);
    self.expense_date = ko.observable();

    self.amount = ko.observable(data.amount);

    self.expense_uuid = ko.observable(data.expense_uuid);

    self.expense_category = ko.observable(data.expense_category);

    if (data.expense_date) {
        self.expense_date(new moment(data.expense_date).format("MM/DD/YYYY"));
    } else {
        self.expense_date(new moment().format("MM/DD/YYYY"));
    }

    self.expense_date_moment = ko.computed(function(){
        if(self.expense_date()){
            return new moment(self.expense_date());
        }
    });

    self.extra_notes = ko.observable(data.extra_notes);
    self.inserted = ko.observable(data.inserted);
    self.updated = ko.observable(data.updated);
    self.is_saving = ko.observable(false);

    self.html_extra_notes = ko.computed(function () {

        if (self.extra_notes()) {
            return self.extra_notes().split("\n").join("<br />");
        }

    });

    self.toJSON = function () {
        return {
            expense_category:
                self.expense_category().title(),
            expense_date: self.expense_date(),
            expense_uuid: self.expense_uuid(),
            person_uuid: self.person_uuid(),
            amount: self.amount(),
            extra_notes: self.extra_notes()
        };
    };
};

function ExpenseCategory(data)
{
    var self = this;

    self.title = ko.observable(data.title);
    self.description = ko.observable(data.description);

    self.inserted = ko.observable(data.inserted);
    self.updated = ko.observable(data.updated);

};

function DenormalizedExpenseCategory(data)
{
    var self = this;

    self.expense_category = ko.observable(new ExpenseCategory(data.expense_category || {}))
    self.expenses = ko.observableArray([]);
    self.amount_spent = ko.computed(function(){
        var total_amount = 0;

        for(i = 0; i < self.expenses().length; i++){
            total_amount += parseInt(self.expenses()[i].amount());
        }
        return total_amount;
    });

    self.budgeted_amount = ko.observable(data.budgeted_amount);


    self.delete_expense = function(expense) {

        $.ajax({
            url:"/delete-expense",
            type: "POST",
            dataType:"json",
            contentType: "application/json; charset=utf-8",
            processData: false,
            data: ko.toJSON(expense),

            success: function (data) {
                // Recaculate new totals
                console.log(data);

                self.expenses.remove(expense);
            },

            failure: function(data)
            {
                alert("failure!")
            }


        });


    }


    if (data.expenses && data.expenses.length > 0 && data.expenses[0] != null){

        self.expenses(ko.utils.arrayMap(
            data.expenses,
            function (e) {
                return new Expense(e);
            }));
    }


    self.amount_spent_percentage = ko.computed(function (){

        if (self.budgeted_amount() == 0)
        {
           return "0%";
        }
        var perc =  (self.amount_spent() / self.budgeted_amount()) * 100;
        /* nothing over 100% */
        if (perc > 100)
        {
           perc = 100;
        }
        return perc + '%';
    });

    self.amount_spent_color = ko.computed(function ()
    {
       return 'green';
    });


    self.start_date = ko.observable();
    self.end_date = ko.observable();
    if(data.effective){
        self.start_date(new moment(data.effective.lower));
        self.end_date(new moment(data.effective.upper));
    }

}

function ExpenseTrackViewModel (data) {
    var self = this;

    self.initialize = function(){

        $.ajax({
            url:"/api/expense-categories",
            type: "GET",
            success: function (data) {

                if(data.success == true){

                    //Look up people
                    self.expense_categories_denormal(
                        ko.utils.arrayMap(
                        data.expense_categories_denormal,
                        function (p) {
                            return new DenormalizedExpenseCategory(p);
                    }));

                    self.expense_categories(
                        ko.utils.arrayMap(
                        data.expense_categories,
                        function (p) {
                            return new ExpenseCategory(p);
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
    }

    self.expense = ko.observable(new Expense({'amount':0}));

    self.expense_categories_denormal = ko.observableArray([]);

    self.expense_categories = ko.observableArray([]);
    self.selected_expense_category = ko.observable();

    self.select_category = function(category)
    {
      self.selected_expense_category(category);
      $('html, body').animate({
          scrollTop: $("#expenseCategoryDeets").offset().top
      }, 1000);
      //skip down to the deets section of the page
    }

    self.selected_expense_category_from_select = ko.observable();

    self.selected_denormal_expense = ko.computed(function(){

        if(self.expense().expense_category() != undefined){
            return ko.utils.arrayFirst(self.expense_categories_denormal(),
                function(item){
                    return item.expense_category().title() == self.expense().expense_category().title();
                });
        }
    });


    self.total_budgeted_amount = ko.computed( function() {
         var total_budgeted_amount = 0;
         for(var i=0; i < self.expense_categories_denormal().length; i++)
         {
            total_budgeted_amount +=
                self.expense_categories_denormal()[i].budgeted_amount();
         }
         return total_budgeted_amount;
    });

    self.total_spent_amount = ko.computed( function() {
         var total_spent_amount = 0;
         for(var i=0; i < self.expense_categories_denormal().length; i++)
         {
            total_spent_amount +=
                parseInt(self.expense_categories_denormal()[i].amount_spent());
         }
         return total_spent_amount;
    });


    self.insert_data = ko.computed(function () {
        return {  };
    });

    self.is_saving = ko.observable(false);

    self.form_is_ready = ko.computed(function () {
        return true;
    });

    self.add_expense_button_enabled = ko.computed(function(){

         if (self.is_saving())
         {
            return true;
         }
         else if(parseInt(self.expense().amount()) <= 0)
         {
            return true;
         }
         else
         {
            return false;
         }
    });

    self.insert = function () {
        if (!self.form_is_ready()) {
            alert("OH NOES");
        }
        else {

            console.log(ko.toJSON(self.expense()))
            self.is_saving(true);
            $.ajax({

                url: "/api/insert-expense",
                type: "POST",
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                processData: false,

                data: ko.toJSON(self.expense()),

                success: function (data) {
                    //make sure we give this a uuid
                    var expense_uuid = data['data']['expense_uuid'];

                    self.expense().expense_uuid(expense_uuid);

                    self.selected_denormal_expense().expenses.unshift(self.expense());

                    self.expense(new Expense({'amount':0,
                                  'expense_date': self.expense().expense_date(),
                                 'expense_category':self.expense().expense_category()}));

                    //self.expense().extra_notes('');
                    self.is_saving(false);
                },

                failure: function(data)
                {
                    alert("failure!")
                }
            });
        }
    };
};


