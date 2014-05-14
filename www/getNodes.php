<?php
//start this users session
	session_start();
//include DB helper functions
include_once("DBhelpers.php");	
//get the phrase from this users session data
$phrase=$_SESSION['phrase'];
//connect to the DB
$mysqli = new mysqli("127.0.0.1", "www", "pin101", "haramain2");
if($mysqli->connect_errno){
	echo "<p>Failed to connect to MySQL: " . $mysqli->connect_error."</p>";
}
//get a list of nodes keyed by this pass phrase
$nodes = getNodesByPhrase($mysqli, $phrase);
//loop through the nodes, get the ones with valid locations/times
//add them to markerData array
$markerData = array();
$i = 0;
foreach($nodes as $node){					
	$devID = $node['devID'];
	$time = $node['time'];
	$lat = $node['lat'];
	$lon = $node['lon'];
	if(isset($time) and isset($lat) and isset($lon)){
		$markerData[$i] = array('devID'=>$devID, 'time'=>$time,'lat'=>$lat,'lon'=>$lon);
		$i = $i+1;
	}
}
//send back the nodes encoded with json
echo json_encode($markerData);
?>