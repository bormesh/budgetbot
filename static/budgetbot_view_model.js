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
    self.date_expense = ko.observable();
    self.amount = ko.observable(data.amount);

    self.expense_category_denorm = ko.observable(data.expense_category);

    if (data.date_expense) {
        self.date_expense(new moment(data.date_expense));
    } else {
        self.date_expense(new moment().format("YYYY-MM-DD"));
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
                self.expense_category_denorm().expense_category.title(),
            date_expense: self.date_expense(),
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

function Client (data) {
    var self = this;

    self.client_uuid = ko.observable(data.client_uuid);
    self.title = ko.observable(data.title);
    self.description = ko.observable(data.description);
    self.current_status = ko.observable(data.current_status);
    self.inserted = ko.observable(data.inserted);
    self.updated = ko.observable(data.updated);
};

function WorkType (data) {
    var self = this;

    self.title = ko.observable(data.title);
    self.description = ko.observable(data.description);
    self.inserted = ko.observable(data.inserted);
    self.updated = ko.observable(data.updated);
};

function DenormalizedClient (data) {
    var self = this;
    self.client = ko.observable(new Client(data.client));

    self.projects = ko.observableArray(ko.utils.arrayMap(
        data.projects,
        function (p) {
            return new Project(p);
        }));
};

function ExpenseTrackViewModel (data) {
    var self = this;

    /*
    self.denormalized_clients = ko.observableArray(ko.utils.arrayMap(
        data.denormalized_clients,
        function (dcl) {
            return new DenormalizedClient(dcl);
        }));


    self.expense_categories = ko.observableArray(ko.utils.arrayMap(
        data.expense_categories,
        function (p) {
            return new ExpenseCategory(p);
        }));

    self.work_types = ko.observableArray(ko.utils.arrayMap(
        data.work_types,
        function (wt) {
            return new WorkType(wt);
        }));

    */
    self.expense = ko.observable(new Expense({'amount':0}));

    self.expense_categories_denormal = ko.observableArray(ko.utils.arrayMap(
        data.expense_categories_denormal,
        function (p) {
            return new DenormalizedExpenseCategory(p);
    }));

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

    self.insert = function () {

        if (!self.form_is_ready()) {
            alert("OH NOES");
        }

        else {

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

                    var new_amount_spent = (
                    parseInt(self.expense().amount()) +
                self.expense().expense_category_denorm().amount_spent());

                    console.log(new_amount_spent);
                    self.expense().expense_category_denorm().amount_spent(new_amount_spent);

                    self.expense().amount(0);
                    self.expense().extra_notes('');
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



