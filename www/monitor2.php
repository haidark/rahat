<?php
	include_once("GoogleMap.php");
	include_once("JSMin.php");
	include_once("DBhelpers.php");	
	

	$mysqli = new mysqli("127.0.0.1", "www", "pin101", "haramain2");
	if($mysqli->connect_errno){
		echo "<p>Failed to connect to MySQL: " . $mysqli->connect_error."</p>";
	}
	$phrase = 'session1';
	$nodes = getNodesByPhrase($mysqli, $phrase);

	//Maps stuff
	$MAP_OBJECT = new GoogleMapAPI(); 
	$MAP_OBJECT->_minify_js = isset($_REQUEST["min"])?FALSE:TRUE;
	if( $_POST != NULL){
			$selNode = $nodes[$_POST["node"]];
			//get all locations of the node
			$locations = getLocationsByPhrase_NID($mysqli, $phrase, $selNode["nID"]);		
			//TODO: plot all the locations on the map
			$locNum = 1;
			foreach($locations as $location){
				$MAP_OBJECT->addMarkerByCoords(floatval($location["lon"]),floatval($location["lat"]),"Location Number {$locNum}", $location["time"]);
				$locNum++;
			}
	}
?>
<html>
<head>
	<meta charset="UTF-8"><title>Monitor</title>
	<?=$MAP_OBJECT->getHeaderJS();?>
	<?=$MAP_OBJECT->getMapJS();?>
</head>
<body>
<?php	

?>
<div id="selectNode">
		<form action="monitor2.php" method="POST">
			<p>Select Node:</p>
			<select name="node">
			<?php
			for($nodeNum = 0; $nodeNum < count($nodes); $nodeNum++){
				$node = $nodes[$nodeNum];
				echo "<option value=\"{$nodeNum}\"> {$node["devID"]} </option>";
			}
			?>
			</select>
			<p><input type="submit" /></p>
		</form>
</div>

<?php		
	if( $_POST != NULL){
		$selNode = $nodes[$_POST["node"]];
		//get all locations of the node
		$locations = getLocationsByPhrase_NID($mysqli, $phrase, $selNode["nID"]);
		
		//plot all the locations on the map
	
		$MAP_OBJECT->printOnLoad();
		$MAP_OBJECT->printMap();
		//$MAP_OBJECT->printSidebar();
		
		//print out a table (caption is devID)
		echo "<table><caption>".$selNode["devID"]."</caption>\n";
		echo "<tr><th>Time</th><th>Latitude</th><th>Longitude</th></tr>";		
		foreach($locations as $location){
			echo "<tr><td>{$location["time"]}</td><td>{$location["lat"]}</td><td>{$location["lon"]}</td></tr>";
		}
		echo "</table>";	
		
	}		
?>
</body>

</html>