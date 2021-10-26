/***************************************************************************************************
 * DayPilot library - for admin user.
 * 
 * It is awesome but in lite version
 * Regex expression fails at modal - cannot use modal as input data :/
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
 ***************************************************************************************************/

// Global variable to store the users name
var current_user = "";


/***************************************************************************************************
 * Navigation setup
 ***************************************************************************************************/
var nav = new DayPilot.Navigator("nav");
nav.showMonths = 3;
nav.selectMode = "month";
nav.onTimeRangeSelected = function(args) {
    dp.startDate = args.start;
    dp.update();
};
nav.init();


/***************************************************************************************************
 * Calendar setup
 ***************************************************************************************************/
var dp = new DayPilot.Month("dp");

// Set the day to today
var today = new Date().toISOString();
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


// -------------------------------------------------------------------------------------------------
// On time range select, prompt resource reservation modal. 
// https://api.daypilot.org/daypilot-modal-form/
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
        {name: "Send request for resource reservation"},
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

    sendEventRequest(e);
};


// -------------------------------------------------------------------------------------------------
// When event is clicked, prompt Modal for event modification
// Admin rights required.
dp.onEventClick = async args => {
    var ev = args.e;

    if(ev.data.tags.status == "pending"){
        var opt = [
            {name: "Confirm request?", id: "confirm"},
            {name: "Delete request?", id: "delete"}
        ];
        const form = [
            {name: "Would you like to:"},
            {name: "", id: "action", options: opt}
        ];

        var modal = await DayPilot.Modal.form(form, {}, {focus: "action"});
        if(modal.canceled){
            return;
        }

        if(modal.result.action === "confirm"){
            console.log("Confirm selected resource")
            sendEventModify("confirm", ev);
        }
        else if(modal.result.action === "delete"){
            console.log("Delete selected resource")
            sendEventModify("delete", ev);
        }
    }
    else{
        message = "Would you like to delete reserved resource?"; 
        var modal = await DayPilot.Modal.confirm(message, {okText:"Yes", cancelText:"No"});
        if(modal.canceled){
            return;
        }
        console.log("Delete selected resource");
        sendEventModify("delete", ev);   
    }
    return;
};


// -------------------------------------------------------------------------------------------------
// Callback function to modify the events theme and colours
dp.onBeforeEventRender = args => {

    var type = args.data.tags && args.data.tags.radio_type;
    var status = args.data.tags && args.data.tags.status;

    switch (type) {
        case "SRDA":    // blue
            args.data.backColor = (status === "confirmed") ? "#3465a4" : "8badda";
            break;

        case "SRDB":    // yellow
            args.data.backColor = (status === "confirmed") ? "#edd400" : "#fff7b3";
            break;
        
        case "LPWA":    // green
            args.data.backColor = (status === "confirmed") ? "#73d216" : "#ccf6a2";
            break;

        case "UWB":     // red
            args.data.backColor = (status === "confirmed") ? "#ff3300" : "#ffc2b3";
            break;

        case "BLE":     // purple
            args.data.backColor = (status === "confirmed") ? "#75507b" : "#d5c1d7";
            break;
	default:
	    break;
    }
    
    switch(status) {
        case "pending":
            args.data.fontColor = "#5e6a6e";
            args.data.borderColor = "#5e6a6e";
            args.data.toolTip =  "Waiting for your conformation."
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
dp.init();

// Update calendar from servers database
loadExistingEvents();

// Send request to obtain the username (request to SMS platform outside the <iframe>) 
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









/***************************************************************************************************
 * Additional functions 
 ***************************************************************************************************/
/**
 * Function that sends HTTP GET request
 */
 function sendHttpRequest(url, data, callback) {
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

/**
 * Function prompts for event update from the testbed database.
 */
 async function loadExistingEvents() {

    const start = nav.visibleStart() > new DayPilot.Date() ? nav.visibleStart() : new DayPilot.Date();

    const params = {
      start: start.toString(),
      end: nav.visibleEnd().toString()
    };

    sendHttpRequest("/update", params, function(args){

        var response = JSON.parse(args);
        dp.events.list = response;
        dp.update();
    });
}

/**
 * Function sends new event request.
 */
async function sendEventRequest(event) {

    var request = event.data;
    request["user"] = current_user;

    sendHttpRequest("/event-request", request, function(args){

        var response = JSON.parse(args);
        var message = response["msg"];

        if (message !== "success"){
            var modal = new DayPilot.Modal.alert(message);
        }
        else{
            dp.events.add(event);
            dp.update();
        }
    });
}

/**
 * Function sends modify action.
 */
async function sendEventModify(action, event) {

    var request = event.data;
    request["user"] = current_user;
    request["action"] = action;

    sendHttpRequest("/event-modify", request, function(args){

        var response = JSON.parse(args);
        var message = response["msg"];

        if (message !== "success"){
            var modal = new DayPilot.Modal.alert(message);
        }
        else{
            loadExistingEvents();
        }
    });
}
