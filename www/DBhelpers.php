<?php
function getNodesByPhrase($mysqli, $phrase){
		$nodes  = NULL;
		$rows = $mysqli->query("SELECT * FROM nodes WHERE session='{$phrase}'");
		for($rowNum = 0; $rowNum < $rows->num_rows; $rowNum++){
			$nodes[$rowNum] = $rows->fetch_assoc();
		}
		return $nodes;
	}

function getLocationsByPhrase_NID($mysqli, $phrase, $nID){
	$locations = NULL;
	$rows = $mysqli->query("SELECT time, lat, lon FROM {$phrase} WHERE nodeID='{$nID}' ORDER BY time DESC");
	for($rowNum = 0; $rowNum < $rows->num_rows; $rowNum++){
		$locations[$rowNum] = $rows->fetch_assoc();
	}
	return $locations;
}

?>