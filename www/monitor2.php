<?php
	if(!isset($_POST["phrase"]) or !isset($_POST["node"])){
		header("Location: phrase2.php");
	}
	include_once("GoogleMap.php");
	include_once("JSMin.php");
	include_once("DBhelpers.php");		

	$mysqli = new mysqli("127.0.0.1", "www", "pin101", "haramain2");
	if($mysqli->connect_errno){
		echo "<p>Failed to connect to MySQL: " . $mysqli->connect_error."</p>";
	}
	

	//Maps stuff
	$MAP_OBJECT = new GoogleMapAPI(); 
	$MAP_OBJECT->_minify_js = isset($_REQUEST["min"])?FALSE:TRUE;
	$MAP_OBJECT->setWidth('100%');
	$MAP_OBJECT->setHeight('100%');
	
	//get the passphrase from the POST global var
	$phrase = $_POST["phrase"];
	//get a list of nodes keyed by this pass phrase
	$nodes = getNodesByPhrase($mysqli, $phrase);
	//select the node the user chose
	$selNode = $nodes[$_POST["node"]];
	//get all locations of that node
	$locations = getLocationsByPhrase_NID($mysqli, $phrase, $selNode["nID"]);		
	// if $locations is not NULL
	if(isset($locations)){
	//plot all the locations on the map
		$locNum = 1;
		foreach($locations as $location){
			$MAP_OBJECT->addMarkerByCoords(floatval($location["lon"]),floatval($location["lat"]),"Location Number {$locNum}", $location["time"]);
			$locNum++;
		}
		//draw lines connecting the markers
		$MAP_OBJECT->addPolylineByCoordsArray($locations);			
	}
?>
<html>
<head>
	<meta charset="UTF-8"><title>Monitor</title>
	<?=$MAP_OBJECT->getHeaderJS();?>
	<?=$MAP_OBJECT->getMapJS();?>
	<style type="text/css">
      html { height: 100% }
      body { height: 100%; margin: 0; padding: 0 }
      #map { height: 100% }
    </style>
</head>
<body><?php	
	$MAP_OBJECT->printMap();
	$MAP_OBJECT->printOnLoad();
	//$MAP_OBJECT->printSidebar();
?>
</body>
</html>