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

function TimeSheet (data) {

    var self = this;

    self.workerbee_id = ko.observable(data.workerbee_id);
    self.project_uuid = ko.observable(data.project_uuid);
    self.date_worked = ko.observable();

    if (data.date_worked) {
        self.date_worked(new moment(data.date_worked));
    } else {
        self.date_worked(new moment().format("YYYY-MM-DD"));
    }

    self.interval_worked = ko.observable(data.interval_worked || 0);
    self.work_type = ko.observable(data.work_type);
    self.billable = ko.observable(data.billable);
    self.extra_notes = ko.observable(data.extra_notes);
    self.inserted = ko.observable(data.inserted);
    self.updated = ko.observable(data.updated);
    self.is_saving = ko.observable(false);

    self.hours_worked = ko.computed(function () {
        return Math.floor(self.interval_worked() / 60);
    });

    self.modulo_minutes_worked = ko.computed(function () {
        return self.interval_worked() % 60;
    });

    self.html_extra_notes = ko.computed(function () {

        if (self.extra_notes()) {
            return self.extra_notes().split("\n").join("<br />");
        }

    });

    self.toJSON = function () {
        return {
            project_uuid: self.project_uuid(),
            date_worked: self.date_worked(),
            interval_worked: self.interval_worked(),
            work_type: self.work_type(),
            billable: self.billable(),
            extra_notes: self.extra_notes()
        };
    };
};

function Invoice(data) {

    var self = this;

    self.invoice_id= ko.observable(data.invoice_id);
    self.notes_to_client = ko.observable(data.notes_to_client);
    self.amount = ko.observable(data.amount);
    self.paid = ko.observable(data.paid);
    self.client_uuid = ko.observable(data.client_uuid);
    self.inserted = ko.observable();

    self.paid_css_class = ko.computed(function () {
        return self.paid() ? 'text-success' : 'text-danger';
    });

    if (data.inserted) {
        self.inserted(new moment(data.inserted).format("YYYY-MM-DD"));
    } else {
        self.inserted(new moment().format("YYYY-MM-DD"));
    }

    self.updated = ko.observable(data.updated);
    self.is_saving = ko.observable(false);

    self.html_notes_to_client = ko.computed(function () {

        if (self.notes_to_client()) {
            return self.notes_to_client().split("\n").join("<br />");
        }

    });

    self.paid_click_update = function(){

        self.is_saving(true);

        $.ajax({

            type:'POST',
            url:'/invoice-update-paid',
            dataType:'json',
            contentType: "application/json; charset=utf-8",
            processData: false,
            data: ko.toJSON({ 'invoice_id':self.invoice_id(),
                    'paid':self.paid()}),
            success: function (data) {
                    self.is_saving(false);
                }
        });

        return true;

    };

    self.toJSON = function () {
        return {
            invoice_id: self.invoice(),
            client_uuid: self.client_uuid(),
            paid: self.paid(),
            amount: self.amount(),
            notes_to_client: self.notes_to_client()
        };
    };
};



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

    self.email_address = ko.observable().extend({
        verify_function: verify_not_blank
    });

    self.password = ko.observable();
    self.expense = ko.observable(new Expense(data));

    /*
    self.denormalized_clients = ko.observableArray(ko.utils.arrayMap(
        data.denormalized_clients,
        function (dcl) {
            return new DenormalizedClient(dcl);
        }));
    */

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

    self.insert_data = ko.computed(function () {

        return {
            email_address: self.email_address(),
            password: self.password(),
            timesheet: self.timesheet()
        };

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

                url: "/insert-timesheet",
                type: "POST",
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                processData: false,
                data: ko.toJSON(self.insert_data()),

                success: function (data) {
                    self.server_reply(data);
                    self.is_saving(false);
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

