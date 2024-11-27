function JournalEntry (data){

    var self = this;

    self.text = ko.observable(data.item);
    self.new_text = ko.observable(data.item);
    self.inserted = ko.observable(data.inserted);

    self.journal_id = ko.observable(data.journal_id);



    self.save = () => {
        console.log("Saving Journal Entry");

		fetch('/api/journal/todays-entry', {
		  method: 'POST',
		  headers: {
			'Content-Type': 'application/json'
		  },
		  body: JSON.stringify({ entry:self.new_text(), journal_id: self.journal_id() })
		})
	  .then(response => {
		if (response.ok) {
		  console.log('Entry posted successfully');
          toastr.success('Saved');
          self.text(self.new_text());
		} else {
		  console.error('Failed to post entry:', response.status);
          toastr('Failed to post entry:', response.status);

		}
	  })
	  .catch(error => {
		console.error('Error posting entry:', error);
          toastr('Failed to post entry:', error);
	  });
	}


};

function JournalViewModel (data){

    var self = this;

    self.todays_entry = new JournalEntry({});
    self.is_editing = ko.observable(false);
	self.todays_date = new Date();

    self.initialize = () =>{
        self.look_up_today_entry();
    }
    /* AJAX look up of name and store etc */
    self.look_up_today_entry = function(){

        return $.ajax({
            url:"/api/journal/todays-entry",
            type: "GET",
            success: function (data) {

                if(data.success == true){

                   self.todays_entry.text(data.entry);
                   self.todays_entry.new_text(data.entry);
                   self.todays_entry.journal_id(data.journal_id);

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
