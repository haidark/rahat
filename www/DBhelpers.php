<?php
function getNodesByPhrase($mysqli, $phrase){
		$nodes  = NULL;
		$rows = $mysqli->query("SELECT * FROM nodes WHERE session='{$phrase}'");
		//create an array of nodes
		for($rowNum = 0; $rowNum < $rows->num_rows; $rowNum++){
			$nodes[$rowNum] = $rows->fetch_assoc();
			$contactID = $nodes[$rowNum]['contactID'];
			//if this node has a contact associated with it
			if( isset($contactID) ){
				//get the contact info of this node
				$contact = getContactByCID($mysqli, $contactID);
				//iterate through possible identifiers in reverse order of desirability
				$keys = array('sms', 'email', 'lName', 'fName');
				//set the most desirable identifier which is not null as this nodes identifier
				foreach ($keys as $key){
					if( isset($contact[$key]) ){
						$nodes[$rowNum]['ident'] = $contact[$key];
					}
				}
			}
			//if no contact is associated with this node	
			else{
				//set the identifier to the deviceID
				$nodes[$rowNum]['ident'] = $nodes[$rowNum]['devID'];
			}
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

function getContactByCID($mysqli, $contactID){
	$row = $mysqli->query("SELECT * FROM contacts WHERE cID='{$contactID}'");
	return $row->fetch_assoc();
}

?>