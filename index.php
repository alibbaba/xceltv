<?php
	$data = "Sani?Thakkar?1445544";
	list($firstname, $lastname, $macip) = explode("?", $data);
	echo $firstname;
	echo '<br>'; // Line break
	echo $lastname;
	echo '<br>';
	echo $macip;

?>
<?php
$servername = "sql3.freesqldatabase.com";
$username = "sql370736";
$password = "rF6!gZ5*";
$dbname = "sql370736";




// Create connection
$conn = mysqli_connect($servername, $username, $password, $dbname);

// Check connection
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}
else{

echo "connected to database";

}

// Create entries to the database
/*
$sql = "INSERT INTO user_detail (firstname, lastname, mac_ip_address)
VALUES ('Sani', 'Thakkar', '0987654321')";

if (mysqli_query($conn, $sql)) {
    echo "New record created successfully";
} else {
    echo "Error: " . $sql . "<br>" . mysqli_error($conn);
}
*/

// Wherify database
$sql = "SELECT * FROM xceltv WHERE username='chintu' AND password='chintu'";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // output data of each row
    while($row = $result->fetch_assoc()) {
        echo "<br> Name: " . $row["username"]. " " . $row["password"]. "<br>" . "Mac ip address: " . $row["macaddress"]. "<br>";
        
    }
    
    $json = file_get_contents('http://xceltv.googlecode.com/svn/trunk/plugin.video.xceltv/4_channels.json'); 
    $data = json_decode($json);
    header('Content-type: application/json');
  //header("Location: http://xceltv.googlecode.com/svn/trunk/plugin.video.xceltv/4_channels.json");
  // echo json_encode($data,JSON_PRETTY_PRINT);
      echo str_replace('\/','/',json_encode($data,JSON_PRETTY_PRINT));
      
      $fp = fopen('results.json', 'w');
fwrite($fp, json_encode($data,JSON_PRETTY_PRINT ));
fclose($fp);
    
} else {
    echo "0 results";
}

mysqli_close($conn);
?>