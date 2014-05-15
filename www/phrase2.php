<?php
	include_once("DBhelpers.php");	
?>
<html>
<head>
	<meta charset="UTF-8"><title>Enter Phrase</title>
</head>
<body>
	<div id="sessionPhrase">
		<form action="phrase.php" method="post">
			<p>Enter pass-phrase:</p>
			<input name="phrase" type="text" id="phrase" 
				<?php
				if(isset($_POST["phrase"])) echo "value=\"{$_POST["phrase"]}\""; 
				?>
				>
			<p><input type="submit" /></p>
		</form>
	</div>
</body>
</html>
<?php 
	if(isset($_POST["phrase"])){
		$mysqli = new mysqli("127.0.0.1", "www", "pin101", "haramain2");
		if($mysqli->connect_errno){
			echo "<p>Failed to connect to MySQL: " . $mysqli->connect_error."</p>";
		}
		$phrase = $_POST["phrase"];
		$nodes = getNodesByPhrase($mysqli, $phrase);
		if(isset($nodes)){
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
						<input type="hidden" id="phrase" name="phrase" value="<?php echo $phrase?>">
						<p><input type="submit" /></p>
					</form>
			</div>
<?php
		}
		else{
?>
			<p>Invalid session passphrase</p>
<?php	
		}
	}
?>