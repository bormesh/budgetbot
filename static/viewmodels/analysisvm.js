function AnalysisViewModel(data){

    var self = this;
    self.type = "AnalysisViewModel"

    self.rootvm = data.roovtm;

    self.expense_data = ko.observableArray([]);

    self.start_date = ko.observable();
    self.end_date = ko.observable();

    self.initialize = () => {
        console.log("Hello, Analysis View Model reporting from init, sir!");
        self.get_data_to_analyze();
    }

    self.get_data_to_analyze = async () => {
        // do our fetch here
        //
        fetch('/api/expenses',
          {
            credentials : "same-origin",
            headers: { 'Accept': 'application/json'}
          }).then((response) => response.json())
            .then((data) =>{
                if(data.success){
                    //process our data here
                    console.log(data);
                }
                else{
                    console.log("Fetch was not successful");
                }
            })

    }



}
