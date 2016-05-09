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


