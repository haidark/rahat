<?php
	//start this users session
	session_start();
	if(!isset($_POST["phrase"]) and !isset($_SESSION['phrase'])){
		header("Location: phrase.php");
	}elseif(isset($_POST["phrase"])){
		//get the passphrase from the POST global var
		$phrase = $_POST["phrase"];
		//store the phrase in this users session		
		$_SESSION['phrase']= $phrase;
	}elseif(isset($_SESSION['phrase'])){
		//get the passphrase from the SESSION global var
		$phrase = $_SESSION['phrase'];
	}
	
	include_once("DBhelpers.php");		

	$mysqli = new mysqli("127.0.0.1", "www", "pin101", "haramain2");
	if($mysqli->connect_errno){
		die("<p>Failed to connect to MySQL: " . $mysqli->connect_error."</p>");
	}
	
	//get a list of nodes keyed by this pass phrase
	$nodes = getNodesByPhrase($mysqli, $phrase);
	//if phrase is invalid, destroy the session and send the user back to try again
	if(!isset($nodes)){
		session_destroy();
		header("Location: phrase.php");
	}
?>
<html>
<head>
	<meta charset="UTF-8"><title>Monitor</title>
	<style type="text/css">
		html { height: 100% }
		body { height: 100%; margin: 0; padding: 0 }
		#map-canvas { height: 100% }
    </style>
	<script type="text/javascript"
		src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBqzCOiJ7cs28M9hbwISmeDaHzvaF2aoGc&sensor=false">
    </script>
    <script type="text/javascript">
		//google map variable
		var map;
		//array to hold markers
		var markers = [];
		var cBoxState = [];
		var firstLoad = true;
		//create map and add all node markers
		function initialize(){		
			var mapOptions = {
				center: new google.maps.LatLng(-34.397, 150.644),
				zoom: 8,
				panControl: false,
				streetViewControl: false,
				overviewMapControl: false
			};
			map = new google.maps.Map(document.getElementById("map-canvas"),
				mapOptions);
					
			//onload, update node locations to latest
			getLatestLocations();			
		}
		
		//uses AJAX to get the updated node data from the database
		//called every minute and onload
		function getLatestLocations(){			
			//create an xmlhttpRequest object
			var xmlhttp;
			if (window.XMLHttpRequest){// code for IE7+, Firefox, Chrome, Opera, Safari
				xmlhttp=new XMLHttpRequest();
			}else {// code for IE6, IE5
				xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
			}
			xmlhttp.onreadystatechange=function(){ updateMarkers(xmlhttp) };
			xmlhttp.open("GET","getNodes.php",true);
			xmlhttp.send();			
		}
		
		//called after xmlhttp.responseText contains new markerData from the DB
		function updateMarkers(xmlhttp){
			if (xmlhttp.readyState==4 && xmlhttp.status==200){
				//first delete all existing markers?
				deleteMarkers();				
				//get the new markerData using Ajax
				var markerData = JSON.parse(xmlhttp.responseText);
				
				//initialize an infoWindow for markers
				var infowindow = new google.maps.InfoWindow();				
				
				//add last location of each node as a marker
				for(var i = 0; i < markerData.length; i++){
					var marker = addMarker(markerData[i].ident, markerData[i].lat, markerData[i].lon);
					
					//set listener for click even on this marker
					google.maps.event.addListener(marker, 'click', (function(marker, i) {
						return function() {
							infowindow.setContent(markerData[i].ident+" at "+markerData[i].time);
							infowindow.open(map, marker);
						}
					})(marker, i));				
				}
				//execute these only if this is the first time the page has loaded
				//and marker data has been received
				if (firstLoad == true){	
					setAllMap(map);
					fitMarkers();
					firstLoad = false;
					//initialize array to hold state of checkboxes
					for(var i = 0; i < markers.length; i++) cBoxState[i] = true;
				} else{
					showSelectedNodes();
				}
				//updates NodeControl checkboxes and manages check box states
				updateNodeControl();
			}			
		}
		
		function fitMarkers(){
			//initialize empty bounds variable
			var bounds = new google.maps.LatLngBounds();
			for(var i = 0; i < markers.length; i++){
				//extend the bounds to include the new marker
				bounds.extend(markers[i].position);
			}
			//scale to show all the markers
			map.fitBounds(bounds);
		}
		
		// Add a marker to the map and push to the array.
		function addMarker(ident, lat, lon) {
			var marker = new google.maps.Marker({
				position: new google.maps.LatLng(lat, lon),
				title: ident
			});
			markers.push(marker);
			return marker
		}
		
		function setAllMap(map){
			for(var i = 0; i < markers.length; i++){
				markers[i].setMap(map);
			}
		}
		
		function deleteMarkers(){
			setAllMap(null);
			markers = [];
		}

		function getMarker(ident){
			//iterate through the whole list
			for(var i = 0; i < markers.length; i++){
				if(markers[i].title == ident) break;
			}
			return markers[i];
		}
		
		function updateNodeControl() {			
			//Ensure cBoxState and markers arrays are of same length
			//balance lengths of markers and cBoxState arrays:
			//if more markers than cBoxState elements
			if(cBoxState.length < markers.length){
				//growthe array and set new values to true
				for(var i = cBoxState.length; i < markers.length; i++) cBoxState[i] = true;
			}
			//to handle case where markers are removed
			//set length of cBoxState to markers.length 
			cBoxState.length = markers.length;
			
			//create a new form
			var controlForm = document.createElement('form');
			controlForm.id = 'nodeForm';
			controlForm.onchange = onNodeControlChanged;
			//create the checkboxes
			for(var i = 0; i < markers.length; i++){
				var checkBox = document.createElement('input');
				checkBox.type = 'checkbox';
				checkBox.id = markers[i].title;
				checkBox.checked = cBoxState[i];
				controlForm.appendChild(checkBox)
				var checkBoxText = document.createElement('span');
				checkBoxText.innerHTML = markers[i].title;
				controlForm.appendChild(checkBoxText)
			}
			var nodeControlDiv = document.getElementById('nodeControlDiv');
			var oldControlForm = document.getElementById('nodeForm');				
			nodeControlDiv.replaceChild(controlForm, oldControlForm);		
		}
		
		function createNodeControl(){
			var nodeControlDiv = document.getElementById('nodeControlDiv');			
			nodeControlDiv.index = 1;
			map.controls[google.maps.ControlPosition.TOP_CENTER].push(nodeControlDiv);	
			updateNodeControl();
		}
		
		function showSelectedNodes(){
			for(var i = 0; i < markers.length; i++){
				if(cBoxState[i] == true){
					markers[i].setMap(map);
				} else{
					markers[i].setMap(null);
				}
			}
		}
		
		function onNodeControlChanged(){
			for(var i = 0; i < markers.length; i++){
				var checkBox = document.getElementById(markers[i].title);
				cBoxState[i] = checkBox.checked;
				if(checkBox.checked)
					markers[i].setMap(map);
				else
					markers[i].setMap(null);
			}
		}
		
		google.maps.event.addDomListener(window, 'load', initialize);
		google.maps.event.addDomListener(window, 'load', createNodeControl);
		//update locations every 15 seconds
		window.setInterval(function(){getLatestLocations();}, 1000*15);		
    </script>
</head>
<body>
	<div id="map-canvas" style="width: 100%; height: 100%"></div>
	<div id="nodeControlDiv" style="padding: 5px;">
		<form id="nodeForm" ></form>
	</div>
</body>
</html>