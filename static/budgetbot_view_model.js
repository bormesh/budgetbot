/*

    A money extender meaning I can data-bind like this

    <span data-bind="money: 1234567.2"></span>

    and it will be formatted like this

    $1,234,567.20

    I got the code for this from here:
    https://gist.github.com/jakiestfu/7894971
*/

(function(){

    var toMoney = function(num){
        return '$' + (num.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, '$1,')                      );
    };

    var handler = function(element, valueAccessor, allBindings){
        var $el = $(element);
        var method;

        // Gives us the real value if it is a computed observable or not
        var valueUnwrapped = ko.unwrap( valueAccessor() );

        if($el.is(':input')){
            method = 'val';
        } else {
            method = 'text';
        }
        return $el[method]( toMoney( valueUnwrapped ) );
    };

    ko.bindingHandlers.money = {
        update: handler
    };
})();


/* Borrowed this from: https://gist.github.com/tommck/6174395
   Now I can display date strings as moment strings with */
ko.bindingHandlers.moment = {
    update: function (element, valueAccessor, allBindingsAccessor, viewModel) {
        var val = valueAccessor();
        var date = moment(ko.utils.unwrapObservable(val));

        var format = allBindingsAccessor().format || 'MM/DD/YYYY';
        element.innerText = date.format(format);
    }
};


function display_news_message (message, alert_level) {

    if (alert_level == "alert-info") {
        toastr.info(message);
    } else if (alert_level == "alert-success") {
        toastr.success(message);
    } else if (alert_level == "alert-danger") {
        toastr.error(message);
    } else if (alert_level == "alert-warning") {
        toastr.warning(message);
    }
};

ko.extenders.completion_status = function (target, options) {

    if (options.initial_status) {
        target.completion_status = ko.observable(options.initial_status);
    } else {
        target.completion_status = ko.observable("incomplete");
    }

    // When the target changes, update the completion status by running
    // the verify function.
    target.subscribe(function (val) {
        target.completion_status(options.verify_function(val));
    });

};



function verify_not_blank (val) {

    if (!val) {
        return "incomplete";
    } else {
        return "complete";
    }

};

function Expense (data) {

    var self = this;

    self.person_id = ko.observable(data.person_id);
    self.expense_date = ko.observable();
    self.amount = ko.observable(data.amount);

    self.expense_uuid = ko.observable(data.expense_uuid);

    self.expense_category = ko.observable(data.expense_category);

    if (data.expense_date) {
        self.expense_date(new moment(data.expense_date));
    } else {
        self.expense_date(new moment().format("YYYY-MM-DD"));
    }

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
                self.expense_category(),
            expense_date: self.expense_date(),
            expense_uuid: self.expense_uuid(),
            person_id: self.person_id(),
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

    self.expense_category = new ExpenseCategory(data.expense_category)
    self.amount_spent = ko.observable(0);

    if(data.amount_spent != null)
    {
       self.amount_spent(data.amount_spent);
    }

    self.budgeted_amount = ko.observable(data.budgeted_amount);

    self.expenses = ko.observableArray();

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


    }


    if (data.expenses.length > 0 && data.expenses[0] != null){

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


    self.start_date =ko.observable(new moment(data.effective.lower));
    self.end_date = ko.observable(new moment(data.effective.upper));

}

function Project (data) {

    var self = this;

    self.project_uuid = ko.observable(data.project_uuid);
    self.title = ko.observable(data.title);
    self.client_uuid = ko.observable(data.client_uuid);
    self.description = ko.observable(data.description);
    self.inserted = ko.observable(data.inserted);
    self.updated = ko.observable(data.updated);

};


function ExpenseTrackViewModel (data) {
    var self = this;

    self.expense = ko.observable(new Expense({'amount':0}));

    self.expense_categories_denormal = ko.observableArray(
        ko.utils.arrayMap(
        data.expense_categories_denormal,
        function (p) {
            return new DenormalizedExpenseCategory(p);
    }));

    self.selected_expense_category = ko.observable();

    self.select_category = function(category)
    {
      self.selected_expense_category(category);
      //skip down to the deets section of the page
      location.href = '#deets';
    }

    self.selected_expense_category_from_select = ko.observable();

    self.selected_expense_category_from_select.subscribe(function(newValue) {
        self.expense().expense_category(newValue.expense_category.title());
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


    self.people = ko.observableArray(
        ko.utils.arrayMap(
            data.people,
            function (w) {
                return new Person(w);
            }));

    self.insert_data = ko.computed(function () {
        return {  };
    });

    self.is_saving = ko.observable(false);

    self.form_is_ready = ko.computed(function () {
        return true;
    });

    self.server_reply = ko.observable(null);

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

                url: "/insert-expense",
                type: "POST",
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                processData: false,

                data: ko.toJSON(self.expense()),

                success: function (data) {
                    self.server_reply(data);

                    //make sure we give this a uuid
                    var expense_uuid = data['data']['expense_uuid'];
                    self.expense().expense_uuid(expense_uuid);

                    var new_amount_spent = (
                    parseInt(self.expense().amount()) +
                        self.selected_expense_category_from_select().amount_spent());

                    self.selected_expense_category_from_select().amount_spent(new_amount_spent);

                    self.selected_expense_category_from_select().expenses.unshift(self.expense());

                    self.expense(new Expense({'amount':0,
                                 'expense_category':self.expense().expense_category()}));

                    //self.expense().extra_notes('');
                    self.is_saving(false);
                    display_news_message('Expense added!','alert-success')
                },

                failure: function(data)
                {
                    alert("failure!")
                }
            });
        }
    };

    self.add_to_localStorage = function () {

        if (self.email_address()) {
            localStorage.setItem('email_address',
                self.email_address());
        }

        if (self.password()) {
            localStorage.setItem('password',
                self.password());
        }

    };

    self.load_from_localStorage = function () {

        var email_address = localStorage.getItem('email_address');

        if (email_address && !self.email_address()) {
            self.email_address(email_address);
        }

        var password = localStorage.getItem('password');

        if (password && !self.password()) {
            self.password(password);
        }

    };

    self.load_from_localStorage();

    self.add_minutes_to_interval_worked = function (minutes_worked) {


        self.timesheet().interval_worked(
            self.timesheet().interval_worked() + minutes_worked);

    };

    self.minutes_to_add = [15, 30, 60];

};

function RecentTimesheetEntriesViewModel (data) {

    var self = this;

    self.entries = ko.observableArray(
        ko.utils.arrayMap(
            data.entries,
            function (e) {
                return new DenormalizedTimeSheet(e);
            }));

    self.workers = ko.observableArray(
        ko.utils.arrayMap(
            data.workers,
            function (w) {
                return new Person(w);
            }));

    self.selected_workers = ko.observableArray([]);

    self.toggle_worker_selection = function (worker) {

        // If it ain't in there.
        if (self.selected_workers.indexOf(worker) == -1) {
            self.selected_workers.removeAll();
            self.selected_workers.push(worker);

        // If it is in there.
        } else {
            self.selected_workers.remove(worker);
        }
    };


    self.in_selected_workers = function (x) {

        return ko.utils.arrayFirst(
            self.selected_workers(),
            function (w) {
                return w.email_address == x.worker().email_address;
            });

    };

    self.total_hours_worked = ko.computed(function() {
                      var total = 0;
                      ko.utils.arrayForEach(self.entries(),
                      function(entry) {

                      if (self.in_selected_workers(entry)){
                        var value = parseFloat(entry.timesheet().interval_worked());
                            if (!isNaN(value)) {
                                total += value;
                            }
                        }
                    });
                    return (total/60).toFixed(2);
                }, this);
};

function InvoicesViewModel (data) {

    var self = this;

    self.invoices = ko.observableArray(
        ko.utils.arrayMap(
            data.denormalized_invoices,
            function (e) {
                return new DenormalizedInvoice(e);
            }));

    self.workers = ko.observableArray(
        ko.utils.arrayMap(
            data.workers,
            function (w) {
                return new Person(w);
            }));


};

function Person (data) {

    var self = this;
    self.display_name = data.display_name;
    self.email_address = data.email_address;
    self.person_id = data.person_id;

};

function BudgetedExpense (data) {

    var self = this;
    self.expense_category = ko.observable(data.expense_category);
};



function DenormalizedTimeSheet (data) {

    var self = this;
    self.client = ko.observable(new Client(data.client));
    self.project = ko.observable(new Project(data.project));
    self.worker = ko.observable(new Person(data.worker));
    self.timesheet = ko.observable(new TimeSheet(data.timesheet));

    self.show_raw_json = ko.observable(false);

};

function DenormalizedInvoice (data) {
    var self = this;

    self.invoice = ko.observable(new Invoice(data.invoice));

    self.client = ko.observable(new Client(data.client));

    self.timesheet_entries = ko.observableArray(ko.utils.arrayMap(
        data.timesheets,
        function (w) {
            return new TimeSheet(w);
        }));

    self.expenses_total = ko.observable(data.expenses_total);

    /* defined right now as 20% after expenses */
    self.partner_share = ko.observable(data.partner_share);
    self.associate_share = ko.observable(data.associate_share);

    self.net_profit = ko.observable(data.net_profit);

    self.total_hours_billed = ko.computed(function() {
                      var total = 0;
                      ko.utils.arrayForEach(self.timesheet_entries(),
                      function(entry) {
                        var value = parseFloat(entry.interval_worked());
                        if (!isNaN(value)) {
                            total += value;
                        }
                    });
                    return (total/60).toFixed(2);
                }, this);



    self.worker_hours_billed = ko.computed(function() {

              var worker_hours= {};
                      ko.utils.arrayForEach(self.timesheet_entries(),
                      function(entry) {
                        var value = parseFloat(entry.interval_worked());
                        var worker = entry.workerbee_id();
                        if (!isNaN(value)) {
                            if (worker in worker_hours)
                            {
                               worker_hours[worker]+=(value/60);
                            }
                            else
                            {
                               worker_hours[worker]=(value/60);
                            }
                        }
                    });
              return worker_hours;

    }, this);

   self.worker_amount_owed = ko.computed(function() {

        var worker_owed = {}

        var hours_billed = self.worker_hours_billed();
        var total_hours = self.total_hours_billed();
        var money = self.associate_share();

        Object.keys(hours_billed).forEach(
        function(key, index)
        {
           worker_owed[key] = (hours_billed[key] / total_hours) * money;
        });

        return worker_owed;

   }, this);

   console.log(self.worker_amount_owed());


};



