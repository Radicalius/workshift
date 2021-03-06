// wariables to hold elements
var people_;
var shifts_;
var results;
var shiftsFile;
var peopleFile;
var gtfact;
var btfact;
var log;

var shifts = [["'Pots (Sample)'",2, "T|Th", 13, 14, 2, "Dishroom"]];
var people = [["'The Goat (Sample)'", 5, "", "xxxxxxxxxxxxxxxx\nxxxxxxxxxxxxxxxx\nxxxxxxxxxxxxxxxx\nxxxxxxxxxxxxxxxx\nxxxxxxxxxxxxxxxx\nxxxxxxxxxxxxxxxx\nxxxxxxxxxxxxxxxx"]]

// onload: load elements
// create forms
window.onload = function(){
	people_ = document.getElementById("people");
	shifts_ = document.getElementById("shifts");
	shiftFile = document.getElementById("shiftsFile");
	peopleFile = document.getElementById("peopleFile");
	results = document.getElementById("results");
	gtfact = document.getElementById("gtf");
	btfact = document.getElementById("btf");
	log = document.getElementById("log");
	createForms();
}

// generates tables for people and shift data
function createForms(){
	var html = "<table class=hiddentable style='width:50%'><tr><b><td>Type</td><td>Day(s)</td><td>Start Time</td><td>End Time</td><td>Hours</td><td>Number of People</td><td>Category</td></b></tr>";
	for (var i = 0; i < shifts.length; i++){
		html += "<tr>"
		for (var j = 0; j < 7; j++){
			html += '<td><input type=text size=10 id="shift'+i+':'+j+'" value="' + shifts[i][j] + '" /></td>\n';
		}
		html += '<td><button type=button onclick="javascript:removeShift('+i+')">Remove</button></td>';
		html+="</tr>"
	}
	html+="<tr><td colspan=5><center><button onclick='javascript:addShift()' type=button>Add Workshift</button></center></td></tr>";
	html += "</table>";
	shifts_.innerHTML = html;

	html = "<table class=hiddentable style='width:50%'><tr><b><td>Name</td><td>Assigned Hours</td><td>Preferences</td><td>Schedule</td></b></tr>";
	for (var i = 0; i < people.length; i++){
		html+="<tr>"
		for (var j = 0; j < 2; j++){
			html += "<td><input type=text size=10 id='person"+i+":"+j+"' value='" + people[i][j] + "' /></td>\n";
		}
		html += "<td><textarea rows=7 cols=16 id=person"+i+":2>"+people[i][2]+"</textarea></td>";
		html += "<td><textarea rows=7 cols=16 id=person"+i+":3>"+people[i][3]+"</textarea></td>";
		html += "<td><button type=button onclick='javascript:removePerson("+i+")'>Remove</button></td>";
		html += "</tr>"
	}
	html += "<tr><td colspan=5><center><button onclick='javascript:addPerson()' type=button>Add Person</button></center></td></tr>";
	html+="</table>"
	people_.innerHTML = html;
}

// adds a blank shift to the shifts table
function addShift(){
	shifts.push([" ",0, " ", 0, 0, 1, " "]);
	createForms();
}

// removes the shift at index i from the table
function removeShift(index){
	shifts.splice(index, 1);
	createForms();
}

// adds blank person to the table
function addPerson(index){
	people.push(["''", 5, "", "                \n                \n                \n                \n                \n                \n                "]);
	createForms();
}

// removes the person at specified index from the table
function removePerson(index){
	people.splice(index, 1);
	createForms();
}

// loads workshift and people data from files specified in the form.
function loadFromFile(){
	var sfile = shiftFile.files[0];
	var pfile = peopleFile.files[0];
	var reader = new FileReader();
    reader.onload = function(e){
    	loadShifts(e.target.result);
    }
    reader.readAsText(sfile);
}

//retrieve any edits from user in form
function updateValues(){
	for (var i = 0; i < shifts.length; i++){
		for (var j = 0; j < 5; j++){
			shifts[i][j] = document.getElementById("shift"+i+":"+j).value;
		}
	}
	for (var i = 0; i < people.length; i++){
		for (var j = 0; j < 4; j++){
			people[i][j] = document.getElementById("person"+i+":"+j).value;
		}
	}
}

function loadPeopleFromFile(){
	var pfile = peopleFile.files[0];
	var reader = new FileReader();
    reader.onload = function(e){
    	loadPeople(e.target.result);
    }
    reader.readAsText(pfile);
}

function loadShifts(text){
	shifts = [];
	var lines = text.split("\n");
	for (var i = 0; i < lines.length; i++){
		if (lines[i]!=""){
			var cols = lines[i].split(",");
			cols[5] = "1";
			shifts.push(cols);
		}
	}
	createForms();
	loadPeopleFromFile();
}

function loadPeople(text){
	people = [];
	var ent = text.split("[END]\n");
	for (var i = 0; i < ent.length; i+=1){
		var lines = ent[i].split("\n")
		if (lines[0]!=""){
			person = [];
			person.push(lines[0]);
			person.push(lines[1]);
			var pref="";
			for (var k = 9; k < lines.length; k++){
				if (lines[k].length > 3){
					pref += lines[k]+"\n";
				}
			}
			person.push(pref);
			var sched = "";
			for (var j = 0; j < 7; j++){
				sched+=lines[2+j]+"\n";
			}
			person.push(sched);
			people.push(person);
		}
	}
	createForms();
}

// from stack overflow: https://stackoverflow.com/questions/247483/http-get-request-in-javascript
function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

// loads results at res.csv into on page table
function loadResults(){
	var res = httpGet("/log.html");
	var html = res.split("</h1>")[1].split("<h2>")[0];
	results.innerHTML = html;
}

// also from stack overflow :) (https://stackoverflow.com/questions/247483/http-get-request-in-javascript)
function httpGetAsync(theUrl, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous 
    xmlHttp.send(null);
}

// also from stack overflow :) (https://stackoverflow.com/questions/18169933/submit-form-without-reloading-page)
function httpPostAsync(theUrl, theParams, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("POST", theUrl, true); // true for asynchronous 
    xmlHttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xmlHttp.setRequestHeader("Content-length",theParams.length);
    xmlHttp.send(theParams);
}

// queue a job on the server
function GO(){
	updateValues();
	var shiftfile = "";
	for (var i = 0; i < shifts.length; i++){
		for (var j = 0; j < 7; j++){
			shiftfile += shifts[i][j]+",";
		}
		shiftfile+="\n";
	}
	var peoplefile = "";
	for (var i = 0; i < people.length; i++){
		peoplefile += people[i][0] + "\n";
		peoplefile += people[i][1] + "\n";
		peoplefile += people[i][3];
		peoplefile += people[i][2] + "\n";
		peoplefile+="[END]\n";
	}
	
	var params = "";
	params += "btf="+btfact.value+"&";
	params += "gtf="+gtfact.value+"&";
	params += "shifts="+encodeURIComponent(shiftfile)+"&";
	params += "people="+encodeURIComponent(peoplefile);
	log.innerHTML = "Starting Job"
	httpPostAsync(window.location+"query", params, function(result){
		log.innerHTML += result;
		loadResults();
	});
}

function onLoadFromServer(){
	httpGetAsync("/shifts.csv",loadShifts);
	httpGetAsync("/people.txt",loadPeople);
}

function onSync() {
	var button = document.getElementById("sync");
	var pass = document.getElementById("pass");
	var user = document.getElementById("user");
	var house = document.getElementById("house");
	var mesg = document.getElementById("syncmesg");
	button.innerHTML="Sync with BSC Server (Running)";
	httpGetAsync("/sync?user="+user.value+"&pass="+pass.value+"&house="+house.value, function(text) {
		button.innerHTML = "Sync with BSC Server";
		mesg.innerHTML = text;
		if (text.trim() == "<font color=#00FF00>Sync Successful</font>"){
			onLoadFromServer();
		}
	});
}