/**
 * DayPilot library. It is awesome but in lite version:
 * Tags are not working
 * Regex expression fails at modal - cannot use modal as input data :/
 */



/**
 * Send HTTP GET request with callback function
 */
 var HttpClient = function() {
    this.get = function(url, data, callback) {
        var httpRequest = new XMLHttpRequest();
        httpRequest.onreadystatechange = function() { 
            if (httpRequest.readyState == 4 && httpRequest.status == 200){
                callback(httpRequest.responseText);
            }
        }

        httpRequest.open("POST", url, true );            
        httpRequest.setRequestHeader("Content-Type", "application/json");
        httpRequest.send(JSON.stringify(data));
    }
}




// -------------------------------------------------
// Navigation setup
// -------------------------------------------------
var nav = new DayPilot.Navigator("nav");
nav.showMonths = 3;
nav.selectMode = "month";
nav.onTimeRangeSelected = function(args) {
    dp.startDate = args.start;
    dp.update();
};
nav.init();





// -------------------------------------------------
// Month calendar setup
// -------------------------------------------------

/* EXAMPLE OF AN EVENT
{
    "start": "2021-03-06T00:00:00",
    "end": "2021-03-06T12:00:00",
    "id": "cb122202-5263-f467-73b3-643e4683bbc7",
    "text": "USERNAME",
    "tags": {
        "radio_type": "SRDA",
        "status": "pending"/"confirmed",
    }
}
*/


var dp = new DayPilot.Month("dp");

// Set the day to today
var today = new Date().toISOString();
//console.log(date);  // Example: 2021-10-06T12:40:43.626Z
dp.startDate = today;

// Locale sets the view of the calendar (Mon first)
//dp.locale = "en-gb";

// Disable moving the events and stuff
dp.eventMoveHandling = "Disabled";
dp.eventResizeHandling = "Disabled";
dp.eventDoubleClickHandling = "Disabled";
dp.eventRightClickHandling = "Disabled";
dp.eventSelectHandling = "Disabled";
dp.showToolTip = "True";
//dp.eventClickHandling = "Disabled";
//dp.timeRangeSelectedHandling = "Disabled";


// Dummy event
var ev = new DayPilot.Event({
    start: new DayPilot.Date("2021-10-04T00:00:00"),
    end: new DayPilot.Date("2021-10-07T20:00:00"),
    id: DayPilot.guid(),
    text: "test1",
    tags: {
        radio_type : "SRDB",
        status : "confirmed"
    },
});
console.log("Tuki");
console.log(ev);
dp.events.add(ev);





/**
 * Resource reservation modal.
 * https://api.daypilot.org/daypilot-modal-form/
 */
dp.onTimeRangeSelected = async args => {

    const device_types = [
        {name: "SRD A", id: "SRDA"},
        {name: "SRD B", id: "SRDB"},
        {name: "LPWA", id: "LPWA"},
        {name: "UWB", id: "UWB"},
        {name: "BLE", id: "BLE"},
    ];

    const data = {
        start: args.start,
        end: args.end,
    };

    const options = {
        focus: "radio_type"
    };

    const form = [
        {name: "Send request for resource reservation"}, // - choose date and device type and click OK."},
        {name: "From", id: "start", dateFormat: "MMMM d, yyyy", disabled: true},
        {name: "To", id: "end", dateFormat: "MMMM d, yyyy", disabled: true},
        //{name: "From", id: "start", dateFormat:"dd.MM.yyyy - hh:mm"},
        //{name: "To", id: "end", dateFormat:"dd.MM.yyyy - hh:mm"},
        //{name: "From", id: "start", dateFormat:"MM d, yyyy"},
        //{name: "To", id: "end", dateFormat:"MM d, yyyy"},
        {name: "Radio type", id: "radio_type", options: device_types},
    ];

    // Prompt modal to the user and wait for completion
    const modal = await DayPilot.Modal.form(form, data, options);

    dp.clearSelection();
    if(modal.canceled){
        return;
    }

    //console.log(modal.result);

    var e = new DayPilot.Event({
        start: modal.result.start,
        end: modal.result.end,
        id: DayPilot.guid(),
        // TODO: fill in the username by user login credentials
        text: modal.result.radio_type,
        tags: {
            radio_type: modal.result.radio_type,
            status: "pending"
        }
    });

    //console.log(e.data);
    var client = new HttpClient();

        //client.get("/request-event?user=admin", function(response){

        client.get("/request-event", e.data, function(args){

            var response = JSON.parse(args);
            var message = response["response_message"];

            if (message !== "success"){
                var modal = new DayPilot.Modal.alert(message)
            }
            else{
                dp.events.add(e);
                //dp.events.add(response["response_event"]);
                dp.update();
            }
    });
};


/**
 * Modal for event info
 */
dp.onEventClick = function(args) {


    var s = args.e.start(),
        e = args.e.end(),
        j = args.e.id();

    // TODO: 
    // Event tags are not working - function returns NULL :|
    // can not obtain radio type name for modal display :/
    // Can not display wether the reservation is pending or if it is confirmed :(
    console.log(args.e.tag["status"]);
    console.log(args.e.tag("radio_type"));


    var message = "Testbed resources already reserved from " + s + " to " + e;
    //message += "For more info contact the administrator.";
    var modal = new DayPilot.Modal.alert(message);
};





/**
 * Callback function to modify the events theme and colours
 */
//dp.onBeforeEventRender = function(args) {
dp.onBeforeEventRender = args => {

    var type = args.data.tags && args.data.tags.radio_type;
    var status = args.data.tags && args.data.tags.status;
	
	console.log("\n\n -----------------------------------------------\n\n");
	console.log(type);
	console.log(status);
    switch (type) {
        case "SRDA":
            if(status === "confirmed"){
                args.data.backColor = "#3465a4";    // blue
            }
            else{
                args.data.backColor = "8badda";
            }
            break;

        case "SRDB":
            if(status === "confirmed"){
                args.data.backColor = "#edd400";    // yellow
            }
            else{
                args.data.backColor = "#fff7b3";
            }
            break;
        
        case "LPWA":
            if(status === "confirmed"){
                args.data.backColor = "#73d216";    // green
            }
            else{
                args.data.backColor = "#ccf6a2";
            }
            break;

        case "UWB":
            if(status === "confirmed"){
                args.data.backColor = "#ff3300";    // red
            }
            else{
                args.data.backColor = "#ffc2b3";
            }
            break;

        case "BLE":
            if(status === "confirmed"){
                args.data.backColor = "#75507b";    // purple
            }
            else{
                args.data.backColor = "#d5c1d7";
            }
            break;
	default:
	    break;
    }

    
    switch(status) {
        case "pending":
            args.data.fontColor = "#5e6a6e";
            args.data.borderColor = "#5e6a6e";
            args.data.toolTip = "Type: " + args.data.tags.radio_type + " | Waiting for admin conformation."
            break;

        case "confirmed":
            args.data.fontColor = "black";
            args.data.borderColor = "black";
            args.data.toolTip = "Type: " + args.data.tags.radio_type + " | Resource already reserved from: " + args.data.start + " to " + args.data.end + ".";
            break;
    	default:
	    break;
	};    
  };





// Init calendar
dp.init();

// Update calendar from servers database
loadExistingEvents();







/**
 * This function returns the stored events from server database.
 * @param {*} day 
 */
 async function loadExistingEvents(day) {

    const start = nav.visibleStart() > new DayPilot.Date() ? nav.visibleStart() : new DayPilot.Date();

    const params = {
      start: start.toString(),
      end: nav.visibleEnd().toString()
    };

    console.log(params);

    var client = new HttpClient();
    client.get("/update", params, function(args){

        var response = JSON.parse(args);

        console.log(response);

	dp.events.list = response;
	dp.update();
/*        for (let i = 0; i < response.length; i++){
	    console.log(i);
	    if (response[i].id){
		uid = response[i].id;
	    }
	    else{
		console.log("No ID found");
		uid = DayPilot.guid();
	    }
	    var ne = new DayPilot.Event({
		start: response[i].start,
		end: response[i].end,
		id: uid,
		text: " ",
		tags: {
			radio_type: response[i].radio_type,
			status: response[i].status,
		},
	    });
	    console.log(response[i]);
	    console.log(ne);
	    dp.events.add(ne);
	    console.log("next");
	}
	//dp.update();
*/

  });


/*
    if (day) {
      dp.startDate = day;
    }
    dp.events.list = data;
    dp.update();

    nav.events.list = data;
    nav.update();
*/
}
