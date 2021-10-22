/**
 * DayPilot library. It is awesome but in lite version:
 * Tags are not working
 * Regex expression fails at modal - cannot use modal as input data :/
 *
 *
 *
 * // Dummy event
    var ev = new DayPilot.Event({
        start: new DayPilot.Date("2021-10-04T00:00:00"),
        end: new DayPilot.Date("2021-10-07T20:00:00"),
        id: DayPilot.guid(),
        text: "SRDB",
        tags: {
            radio_type : "SRDB",
            status : "confirmed"
        },
    });
    dp.events.add(ev);

 *
 * TODO: Can't find a username on the frontend... workaround:
 * Prompt a user for his GitHub username :)
 */


/**
 * Function that sends HTTP GET request
 * @param url URL for request
 * @param data dictionary with data to send
 * @param callback a callback function to handle response
 */
 var HttpClient = function() {
    this.get = function(url, data, callback) {
        var httpRequest = new XMLHttpRequest();
        httpRequest.onreadystatechange = function() { 
            if (httpRequest.readyState == 4 && httpRequest.status == 200){
                callback(httpRequest.responseText);
            }
        }
        u = "/scheduler" + url;
        // u = url; --> LOCAL TEST!
        httpRequest.open("POST", u, true );            
        httpRequest.setRequestHeader("Content-Type", "application/json");
        httpRequest.send(JSON.stringify(data));
    }
}

// --------------------------------------------------------------------------------------------------
// Navigation setup
// --------------------------------------------------------------------------------------------------
var nav = new DayPilot.Navigator("nav");
nav.showMonths = 3;
nav.selectMode = "month";
nav.onTimeRangeSelected = function(args) {
    dp.startDate = args.start;
    dp.update();
};
nav.init();


// --------------------------------------------------------------------------------------------------
// Month calendar setup
// --------------------------------------------------------------------------------------------------
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
        text: modal.result.radio_type,
        tags: {
            radio_type: modal.result.radio_type,
            status: "pending"
        }
    });

    //console.log(e.data);
    sendEventRequest(e);
};


/**
 * Modal for event info
 */
 dp.onEventClick = async args => {

    var ev = args.e.data;
    if(ev.tags.status === "pending"){
        var message = "Waiting for admin conformation.";
    }
    else{
        var message = ev.tags.radio_type + " testbed resources reserved from " + ev.start + " to " + ev.end;
    }
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
            args.data.toolTip =  "Waiting for admin conformation."
            break;

        case "confirmed":
            args.data.fontColor = "black";
            args.data.borderColor = "black";
            args.data.toolTip = "Resources reserved from: " + args.data.start + " to " + args.data.end + ".";
            break;
    	default:
	    break;
	};    
  };



// --------------------------------------------------------------------------------------------------
// Init calendar
// --------------------------------------------------------------------------------------------------
dp.init();
// Update calendar from servers database
loadExistingEvents();


var current_user = "";

var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function() {
    if(this.readyState == 4 && this.status == 200){
        var resp = JSON.parse(this.response);
        current_user = resp["username"];
    }
}
xhttp.open("POST", "/handler", true);
xhttp.setRequestHeader("Content-Type", "application/json");
xhttp.send(JSON.stringify({action:"get_current_user", data:{}}));


// --------------------------------------------------------------------------------------------------
// Additional functions 
// --------------------------------------------------------------------------------------------------
/**
 * Function returns the stored events from server database.
 */
 async function loadExistingEvents() {

    const start = nav.visibleStart() > new DayPilot.Date() ? nav.visibleStart() : new DayPilot.Date();

    const params = {
      start: start.toString(),
      end: nav.visibleEnd().toString()
    };
    //console.log(params);

    var client = new HttpClient();
    client.get("/update", params, function(args){

        var response = JSON.parse(args);
        //console.log(response);

        dp.events.list = response;
        dp.update();
    });
}

async function sendEventRequest(event) {

    // Workaround: Add a username to the request
    var request = event.data;
    request["user"] = current_user;

    var client = new HttpClient();
    client.get("/event-request", request, function(args){

        var response = JSON.parse(args);
        var message = response["msg"];

        if (message !== "success"){
            var modal = new DayPilot.Modal.alert(message)
        }
        else{
            dp.events.add(event);
            //dp.events.add(response["response_event"]);
            dp.update();
        }
    });
}