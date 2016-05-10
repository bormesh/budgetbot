ko.bindingHandlers.masked_input =  {

  init: function(element, valueAccessor, allBindings, viewModel, bindingContext)   {

        var clean = valueAccessor();

        $(element).keyup(function () {

            if($(element).val() == ""){
                clean($(element).val());
            }
            else{
                clean($(element).cleanVal());
            }
        });

    },

    update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {

        var clean = valueAccessor();
        /* We need to trigger the mask function, so let's use paste here
         */

        $(element).val(clean()).trigger("paste");

    }

};

ko.bindingHandlers.masked_input_on_change =  {

  init: function(element, valueAccessor, allBindings, viewModel, bindingContext)   {

        var clean = valueAccessor();

        $(element).change(function () {

            if($(element).val() == ""){
                clean($(element).val());
            }
            else{
                clean($(element).cleanVal());
            }
        });

    },

    update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {

        var clean = valueAccessor();
        /* We need to trigger the mask function, so let's use paste here
         */

        $(element).val(clean()).trigger("keyup");

    }

};

phone_number_has_error = function (ph) {
    if (ph != undefined && ph != "" && ph.length != 10) {
        return true;
    }
};

/*
    A money extender
    data-bind like this:
    <span data-bind="money: 1234567.2"></span>
    and it will be formatted like this
    $1,234,567.20
*/

(function(){

    var toMoney = function(num){
        if (num != undefined)
        {
           return '$' + (num.toFixed(0).replace(/(\d)(?=(\d{3})+$)/g, '$1,'));
        }
        else{
            return num;
        }
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

/*
    A percent extender
    data-bind like this:
    <span data-bind="percent: 67"></span>
    and it will be formatted like this
    67%
*/

(function(){

    var toPercent = function(num){
        if (num != undefined)
        {
           return num + '%';
        }
        else{
            return num;
        }
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
        return $el[method]( toPercent( valueUnwrapped ) );
    };

    ko.bindingHandlers.percent = {
        update: handler
    };
})();

/* Custom binding for making modals */
ko.bindingHandlers.bootstrapModal = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
        var props = valueAccessor(),
            vm = bindingContext.createChildContext(viewModel);
        ko.utils.extend(vm, props);
        vm.close = function () {
            vm.show(false);
            vm.onClose();
        };
        vm.action = function () {
            vm.onAction();
        }
        ko.utils.toggleDomNodeCssClass(element, "modal fade", true);
        ko.renderTemplate("makeAnOfferModal", vm, null, element);
        var showHide = ko.computed(function () {
            $(element).modal(vm.show() ? 'show' : 'hide');
        });
        return {
            controlsDescendantBindings: true
        };
    }
}

/* Custom handler for Bootstrap 3 Datetimepicker */
ko.bindingHandlers.dateTimePicker = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {

        var options = ko.unwrap(valueAccessor());
        var valueObservable = allBindings.get('value');

        var defaults = {
            //defaultDate: valueObservable(), //can't set default here because parsing fails for time strings (ex:  "09:15 AM" throws error)
            format: 'MM/DD/YYYY hh:mm A',
            icons: {
                down: 'fa fa-chevron-down',
                up: 'fa fa-chevron-up'
            },
            stepping: 15,
            sideBySide: false,
            widgetPositioning: {
                horizontal: 'auto',
                vertical: 'auto'
            }
        };

        var config = ko.utils.extend(defaults, options); //override defaults with passed in options
        var $pickerElement = $(element).datetimepicker(config);

        $pickerElement.bind('dp.change', function (eventObj) {
            var picker = $(element).data("DateTimePicker");
            if (picker) {
                var date = picker.date();
                var formattedDate = date ? date.format(picker.format()) : "";
                if (formattedDate != valueObservable()) {
                    valueObservable(formattedDate);
                }
            }
        });

        ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
            var picker = $(element).data("DateTimePicker");
            if (picker) {
                picker.destroy();
            }
        });
    },
    update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        var picker = $(element).data("DateTimePicker");
        if (picker) {
            var valueObservable = allBindings.get('value');
            var date = picker.date();
            var formattedDate = date ? date.format(picker.format()) : "";

            if (formattedDate != valueObservable()) {
                if(valueObservable()){
                    picker.date(valueObservable());
                }
            }
        }

    }
 };

/* Got execute on enter from :
   http://stackoverflow.com/questions/23087721/call-function-on-enter-key-press-knockout-js

   bind like this

   data-bind="executeOnEnter: sendMessage, button : buttonSelector"
*/


ko.bindingHandlers.executeOnEnter = {
    init: function (element, valueAccessor, allBindings, viewModel) {
        var options = valueAccessor();

        if (options === undefined)
        {
            return false;
        }
        var callback = options.callback;
        var selector_id = options.selector_id || element;
        $(element).keypress(function (event) {
            var keyCode = (event.which ? event.which : event.keyCode);
            if (keyCode === 13) {
                callback.call(viewModel, selector_id);
                return false;
            }
            return true;
        });
    }
};


ko.bindingHandlers.selected = {
    update: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
        var selected = ko.utils.unwrapObservable(valueAccessor());
        if (selected) element.select();
    }
};


/* Sort column by column headers and types.

   Check out this jsFiddle http://jsfiddle.net/brendonparker/6S85t/

   Use it like this
   <th data-bind="sort: { arr: Records, prop: 'Name' }">Name</th>
*/

ko.bindingHandlers.sort = {
    init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
        var asc = false;
        element.style.cursor = 'pointer';

        element.onclick = function(){
            var value = valueAccessor();
            var prop = value.prop;
            var data = value.arr;

            asc = !asc;

            data.sort(function(left, right){
                var rec1 = left;
                var rec2 = right;

                if(!asc) {
                    rec1 = right;
                    rec2 = left;
                }

                var props = prop.split('.');
                for(var i in props){
                    var propName = props[i];
                    var parenIndex = propName.indexOf('()');
                    if(parenIndex > 0){
                        propName = propName.substring(0, parenIndex);
                        rec1 = rec1[propName]();
                        rec2 = rec2[propName]();
                    } else {
                        rec1 = rec1[propName];
                        rec2 = rec2[propName];
                    }
                }

                return rec1 == rec2 ? 0 : rec1 < rec2 ? -1 : 1;
            });
        };
    }
};

ko.bindingHandlers.sort_desc = {
    init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
        var asc = false;
        element.style.cursor = 'pointer';

        element.onclick = function(){
            var value = valueAccessor();
            var prop = value.prop;
            var data = value.arr;

            data.sort(function(left, right){
                var rec1 = left;
                var rec2 = right;

                if(!asc) {
                    rec1 = right;
                    rec2 = left;
                }

                var props = prop.split('.');
                for(var i in props){
                    var propName = props[i];
                    var parenIndex = propName.indexOf('()');
                    if(parenIndex > 0){
                        propName = propName.substring(0, parenIndex);
                        rec1 = rec1[propName]();
                        rec2 = rec2[propName]();
                    } else {
                        rec1 = rec1[propName];
                        rec2 = rec2[propName];
                    }
                }

                return rec1 == rec2 ? 0 : rec1 < rec2 ? -1 : 1;
            });
        };
    }
};


/* Fades */
// Here's a custom Knockout binding that makes elements shown/hidden via jQuery's fadeIn()/fadeOut() methods
// Could be stored in a separate utility library
ko.bindingHandlers.fadeVisible = {
    init: function(element, valueAccessor) {
        // Initially set the element to be instantly visible/hidden depending on the value
        var value = valueAccessor();
        $(element).toggle(ko.unwrap(value)); // Use "unwrapObservable" so we can handle values that may or may not be observable
    },
    update: function(element, valueAccessor) {
        // Whenever the value subsequently changes, slowly fade the element in or out
        var value = valueAccessor();
        ko.unwrap(value) ? $(element).fadeIn() : $(element).fadeOut();
    }
};

ko.bindingHandlers.fadeSwitcher = {
    init: function (element, valueAccessor) {
        var value = ko.utils.unwrapObservable(valueAccessor());
        element.setAttribute('previousValue', value);
        ko.bindingHandlers.text.update(element, ko.observable(value));
    },
    update: function (element, valueAccessor) {
        var value = ko.utils.unwrapObservable(valueAccessor());
        var previousValue = element.getAttribute('previousValue');
        if (value !== previousValue) {
            $(element).fadeOut('fast', function () {
                ko.bindingHandlers.text.update(element, ko.observable(value));
                $(element).fadeIn();
            });
            element.setAttribute('previousValue', value);
        }
    }
};

/* Borrowed this from: https://gist.github.com/tommck/6174395
   Now I can display date strings as moment strings with */
ko.bindingHandlers.moment = {
    update: function (element, valueAccessor, allBindingsAccessor, viewModel) {
        var val = valueAccessor();
        var date = moment(ko.utils.unwrapObservable(val));

        var format = allBindingsAccessor().format || 'MM/DD/YYYY';
        element.innerHTML = date.format(format);
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


