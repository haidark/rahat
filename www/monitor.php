<!DOCTYPE HTML>
<html>
<head>
	<meta charset="UTF-8"><title>Monitor</title>
</head>
<body>
<?php
	
	$mysqli = new mysqli("127.0.0.1", "www", "pin101", "haramain");
	if($mysqli->connect_errno){
		echo "<p>Failed to connect to MySQL: " . $mysqli->connect_error."</p>";
	}
	$phrase = $_POST['phrase'];
	$session = $mysqli->query("SELECT SID FROM sessions WHERE phrase='{$phrase}'");
	//if the session exists
	if($session->num_rows == 1){
		$row = $session->fetch_assoc();
		$SID = $row["SID"];		
		echo "<p>Session ID is ".$SID."</p>";
		$nodes = $mysqli->query("SELECT NID, info FROM nodes WHERE sessionID='{$SID}'");
		//for each node is the session
		for($nodeNum = 0; $nodeNum < $nodes->num_rows; $nodeNum++){
			//print out a table (caption is info
			$node = $nodes->fetch_assoc();
			echo "<table><caption>".$node["info"]."</caption>\n";
			echo "<tr><th>Time</th><th>Latitude</th><th>Longitude</th></tr>";
			//get all locations of the node
			$locations = $mysqli->query("SELECT time, lat, lon FROM locations WHERE nodeID='{$node["NID"]}'");
			for($locNum = 0; $locNum < $locations->num_rows; $locNum++){
				$location = $locations->fetch_assoc();
				echo "<tr><td>{$location["time"]}</td><td>{$location["lat"]}</td><td>{$location["lon"]}</td></tr>";
			}
			echo "</table>";			
		}
	}else{
		echo "<p>Session not found!!!</p>";
	}	
?>
</body>

</html>