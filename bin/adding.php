<?php
$Model =  $_POST['Name'];
$DOI = $_POST['doi'];
$Version =  $_POST['Version'];
$Author =  $_POST['Author'];
$Email =  $_POST['Email'];
$Tag =  $_POST['Tag'];
$location =$_POST['Location'];
$pdf =  basename( $_FILES["fileToUpload"]["name"]);
$file = $_FILES["fileToUpload"];
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    
    if (empty($_POST["Name"])) {
      echo "Model name is needed.";
      exit;
    } else {
        
        if (!preg_match("/^[a-zA-Z0-9 ]*$/",$Model)) {
          echo "Model name has error"; 
          exit;
          }
      }
    
    if (empty($_POST["Email"])) {
        echo "Email is needed";
        exit;
      } else {

        
        if (!preg_match("/([\w\-]+\@[\w\-]+\.[\w\-]+)/",$Email)) {
          echo "Illegal Email address"; 
          exit;
        }
      }
    
    if (empty($_POST["Author"])) {
      echo "Author is needed!";
    } 
  
    if (empty($_POST["Tag"])) {
      echo "Tag is needed!";
    } 
    
    if (empty($_POST["Location"])) {
        echo "Location is needed!";
      } 

    if (empty($_POST["Version"])) {
      echo "Version is needed!";
    } else{
        if (!preg_match("/^[.0-9]*$/",$Version)) {
        echo "Version must be number"; 
        exit;
      }
    }
 

}

$pathmdl = $Model;

if ( !is_dir( $pathmdl ) ) {
  mkdir( $pathmdl,0775 );       
}

$pathmdlvrs = $pathmdl.'/'.$Version;
if ( !is_dir( $pathmdlvrs ) ) {
  mkdir( $pathmdlvrs );       
}
$target_dir = "$pathmdlvrs/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]['name']);
            

move_uploaded_file($_FILES["fileToUpload"]['tmp_name'], $target_file);


$params = "$Model $DOI $Version $Author $Email $location $Tag  $file $pdf"; 

$path="python3 web.py "; 
#
passthru($path.$params);
$newURL = 'https://straiti3.org/blog/';
    
header('Location: '.$newURL);

?>


