<?php $version=" (v1.2)"; ?>
<!-- 13/04/2015 fix display chor file v1.2
<!-- 21/01/2015 add file midi v1.1
<!-- 17/01/2015 v1.0
     generator choreography for Nabaztag v2  by carlo64 ^_^ 
     -->
     
<html>
<head>
<style>
form { padding:0;margin:0;}
input { text-align:center;}
input[type="number"] { width: 3rem; }
.ColoreCH {background-color: #FF8080;}
.ColoreReadonly {background-color: #408080;width:20px;}
.parteSX {display:inline-block;}
.parteDX {width:80%;display:inline-block;text-align:right;}
.parteSXalta {display:inline-block;}
.parteDXalta {width:60%;display:inline-block;text-align:right;}
</style>
<script>
function colore( iSelect, iRGB, nomeForm, nomeEsempio )
{
var esempio = document.getElementById(nomeEsempio);
var x = document.getElementsByName(nomeForm)[0][iSelect+5].options;
var l = x.length;
for(i=0;i<l;i++)
{
  if (x[i].selected==true)
	var v = x[i].value;
}
var rgb = v.split(",");
document.getElementsByName(nomeForm)[0][iRGB+2].value=rgb[0];
document.getElementsByName(nomeForm)[0][iRGB+3].value=rgb[1];
document.getElementsByName(nomeForm)[0][iRGB+4].value=rgb[2];
esempio.style.backgroundColor = 'rgb('+v+')';
}
</script>
</head>
<body>
<!-- tt imposta il font antico.. :) -->
<tt>
<?php
//$nomeFile = "/var/www/OpenJabNab/http-wrapper/ojn_local/tts/acapela/Claire/chor1.chor";//tmp/chor.chor";//$_REQUEST['nomeFile'];
//$nomeFile = "tmp/chor.chor";//$_REQUEST['nomeFile'];

$contenuto = array();

// ----------- costanti prese dal main.mtl
// ---------------------------------------
define ("CH_frame_duration","1"); //*
//var CH_set_color=6;;
define ("CH_set_led_color","7"); //*
define ("CH_set_motor","8"); //*
define ("CH_set_leds_color","9"); //*
define ("CH_set_led_off","10"); //*
define ("CH_set_led_palette","14");
//var CH_set_palette=15;;
define ("CH_randmidi","16"); //*
define ("CH_avance","17"); //*
define ("CH_ifne","18");
define ("CH_attend","19"); //*
define ("CH_setmotordir","20");

define ("CH_file_midi","30");

//define ("LED_BOTTOM","0");
//define ("LED_LEFT","1");
//define ("LED_MIDDLE","2");
//define ("LED_RIGHT","3");
//define ("LED_TOP","4");

$posizioneLed = array( 0=>"LED_BOTTOM",1=>"LED_LEFT",2=>"LED_MIDDLE",3=>"LED_RIGHT",4=>"LED_TOP");

//define ("EAR_LEFT","1");
//define ("EAR_RIGHT","0");
//define ("EAR_BACK","1");
//define ("EAR_FRONT","0");

// ------------------------------------------
// form imposta il nome del file
if ( isset($_REQUEST['nomeFile']) ) {
  $nomeFile = $_REQUEST['nomeFile'];
//  echo "impostato nome file: $nomeFile ";
}
else {
  $nomeFile = 'tmp/chor.chor'; // default da cambiare a discrezione..
}  

// ------------------------------------------
// form visualizza il file esistente
if ( isset($_REQUEST['f0Form']) )
{
 visualizza( $nomeFile );
}

// ------------------------------------------
// form cancella il file esistente
if ( isset($_REQUEST['resetForm']) )
{
 $file = fopen($nomeFile, "w");
 fclose($file);
 echo "file $nomeFile deleted";
}

// ------------------------------------------
// form vari di inserimento
if ( (isset($_REQUEST['f1Form'])) ||
     (isset($_REQUEST['f2Form'])) ||
     (isset($_REQUEST['f3Form'])) ||
     (isset($_REQUEST['f4Form'])) ||
     (isset($_REQUEST['f5Form'])) ||
     (isset($_REQUEST['f6Form'])) ||
     (isset($_REQUEST['f7Form'])) ||
     (isset($_REQUEST['f8Form'])) ||
     (isset($_REQUEST['f9Form'])) ||
     (isset($_REQUEST['f10Form'])) ||
     (isset($_REQUEST['f11Form'])) ||
     (isset($_REQUEST['f12Form'])) ||
     (isset($_REQUEST['f13Form'])) ||
     (isset($_REQUEST['f14Form'])) ||
     (isset($_REQUEST['f15Form'])) ||
     (isset($_REQUEST['f15aForm'])) ||
     (isset($_REQUEST['f16Form'])) ||
     (isset($_REQUEST['f17Form'])) ||
     (isset($_REQUEST['fMidi'])) )
{
   $pacchetto = $_REQUEST['valore'];
   
  // ------------------------------------------
  // form led. deve togliere il campo di input con i colori di esempio
  if ( (isset($_REQUEST['f8Form'])) ||
       (isset($_REQUEST['f9Form'])) ||
       (isset($_REQUEST['f10Form'])) ||
       (isset($_REQUEST['f11Form'])) ||
       (isset($_REQUEST['f12Form'])) ||
       (isset($_REQUEST['f13Form'])) )
    {
	 $x = array_pop($pacchetto);
    }

  // form midi
  if (isset($_REQUEST['fMidi'])) 
  {
    $stringaMidi = strtoupper($pacchetto[4]);
    $x = array_pop($pacchetto); 
	
	$stringaMidiArray = str_split($stringaMidi, 2);
	foreach($stringaMidiArray as $tmp)
	{
	 $x = hexdec($tmp);
	 $pacchetto[]=$x;
	}
    $lunMidi = count($pacchetto);
    $lunMidi = $lunMidi -1 -1 -1 -1;
    $b1 = 0;
    $b2 = $lunMidi;
    if ($lunMidi > 255) {
      $b1 = intval($lunMidi/256);
      $b2 = $lunMidi - $b1*256;
    }
    $pacchetto[2] = $b1;
    $pacchetto[3] = $b2;

  }


  // ------------------------------------------
  // visualizza il comando insertito
  $stringa = "";
  foreach($pacchetto as $tmp) {
    $stringa .= sprintf("%'02X ", $tmp);
  }
  echo "command added: $stringa";


// ---------------- FILE BINARIO
// ---------------- FILE BINARIO
// ---------------- FILE BINARIO
// ---------------- FILE BINARIO
if ((file_exists($nomeFile)) && (filesize($nomeFile)>0)) {

	$file = fopen($nomeFile, "rb");
	$contenuto = array();
	$b = fread($file, filesize($nomeFile));
	$contenuto = unpack("C*",$b);
	fclose($file);
	$x = array_pop($contenuto); // toglie  coda
	$x = array_pop($contenuto);
	$x = array_pop($contenuto);
	$x = array_pop($contenuto);
	$x = array_shift($contenuto); // toglie header
	$x = array_shift($contenuto);
	$x = array_shift($contenuto);
	$x = array_shift($contenuto);
}

//
$file = fopen($nomeFile, "wb");
$header = array( 0, 0, 0, 0); //, 0, 1, 0 );
$codaDati = array( 0,0,0,0);//0x02, 0x0A, 0x04 );
//
$lenPacchetto = count($pacchetto);
$lenHeader = count($header);
$lenContenuto = count($contenuto);

$b1 = 0;
$b2 = $lenPacchetto + $lenContenuto;
if ($lenPacchetto > 255) {
  $b1 = intval($lenPacchetto/256);
  $b2 = $lenPacchetto - $b1*256;
}
//echo " ".$lenPacchetto." ".$lenHeader." ".$b1." ".$b2;
$header[2] = $b1;
$header[3] = $b2;
//$header[3] = $lenPacchetto + $lenHeader;
foreach($header as $tmp) {
// printf("%'02X ",$tmp);
 $t=pack("C",$tmp);
 fwrite($file,$t);
 }
//echo "( ";

if ($lenContenuto>0) {
//echo "[ ";
   foreach($contenuto as $tmp) {
     //printf("%'02X ",$tmp);
     $t=pack("C",$tmp);
     fwrite($file,$t);
   } 
//echo " ]";
}

foreach($pacchetto as $tmp) {
 //printf("%'02X ",$tmp);
 $t=pack("C",$tmp);
 fwrite($file,$t);
 } 
//echo ") "; 
foreach($codaDati as $tmp) {
 //printf("%'02X ",$tmp);
  $t=pack("C",$tmp);
 fwrite($file,$t);
 }
fclose($file);

}
// fine POST
?>
<center><b><i>Choreography generator<?php echo $version; ?></i></b></center>

<div class="parteDXalta">
<form name="f0" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<input type="submit" name="f0Form" value="show current file">
</form>
</div><div class="parteSXalta">
<form name="f0" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<input type="submit" name="resetForm" value="reset file">
</form>
</div>

<!-- NOMEFILE ----------------->
<!-- NOMEFILE ----------------->
<!-- NOMEFILE ----------------->
<!-- NOMEFILE ----------------->
<div class="parteDXalta">
<form name="fNomeFile" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
File name choreography <input name="nomeFile" type="text" value="<? echo $nomeFile; ?>" size="50" >
</div><div class="parteSXalta">
<input type="submit" name="fNomeFileForm" value="set file name">
</form>
</div>

<hr>

<!-- ATTENDE --------------------->
<!-- ATTENDE --------------------->
<!-- ATTENDE --------------------->
<!-- ATTENDE --------------------->
<form name="f1" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<div class="parteDX">attende [CH_attend]
<!-- ts -->
<input type="number" name="valore[]" value="0" size="3" min="0" max="255">
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_attend ?>" readonly size="1" >
</div><div class="parteSX">
<input type="submit" name="f1Form" value="insert">
</div>
</form>

<!-- MIDI --------------------->
<!-- MIDI --------------------->
<!-- MIDI --------------------->
<!-- MIDI --------------------->
<form name="f2" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<div class="parteDX">midi [CH_randmidi]
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!--<input type="text" name="valore[]" value="0" size="3">-->
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_randmidi ?>" readonly size="1">
</div><div class="parteSX">
<input type="submit" name="f1Form" value="insert">
</div>
</form>

<!-- tempo ------------------->
<!-- tempo ------------------->
<!-- tempo ------------------->
<!-- tempo ------------------->
<form name="f3" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<div class="parteDX">time (Nb of ms between two actions) [CH_frame_duration]
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!--<input type="text" name="valore[]" value="0" size="3">-->
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_frame_duration ?>" readonly size="1">
<select name="valore[]">
<?php
 for($i=0;$i<256;$i++)
  if ($i==0x10)  
   echo "<option value=".$i." selected>".$i."</option>";
  else
   echo "<option value=".$i.">".$i."</option>";
?>
</select>
</div><div class="parteSX">
<input type="submit" name="f3Form" value="insert">
</div>
</form>

<!-- EAR --------------------->
<!-- EAR --------------------->
<!-- EAR --------------------->
<!-- EAR --------------------->
<!-- orecchio destro -->
<form name="f4" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<div class="parteDX">ear right [CH_set_motor]
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!--<input type="text" name="valore[]" value="0" size="3">-->
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_set_motor ?>" readonly size="1">
<!-- dx o sx -->
<input name="valore[]" value="0" readonly size="1" class="ColoreReadonly">
<!-- angolo --> 
<select name="valore[]">
<?php
 for($i=0;$i<19;$i++)
  echo "<option value='".$i."'>".$i."</option>";
?>
</select>
<!-- direzione -->
<select name="valore[]">
  <option value="0">clockwise rotation</option> <!--rotazione oraria-->
  <option value="1">counterclockwise rotation</option>
</select>
</div><div class="parteSX">
<input type="submit" name="f4Form" value="insert">
</div>
</form>

<!-- EAR --------------------->
<!-- EAR --------------------->
<!-- EAR --------------------->
<!-- EAR --------------------->
<!-- orecchio sinistro -->
<form name="f5" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<div class="parteDX">ear left [CH_set_motor]
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!--<input type="text" name="valore[]" value="0" size="3">-->
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_set_motor ?>" readonly size="1">
<!-- dx o sx -->
<input name="valore[]" value="1" readonly size="1" class="ColoreReadonly">
<!-- angolo --> 
<select name="valore[]">
<?php
 for($i=0;$i<19;$i++)
  echo "<option value='".$i."'>".$i."</option>";
?>
</select>
<!-- direzione -->
<select name="valore[]">
  <option value="0">clockwise rotation</option> <!--rotazione oraria-->
  <option value="1">counterclockwise rotation</option>
</select>
</div><div class="parteSX">
<input type="submit" name="f5Form" value="insert">
</div>
</form>

<!--  EAR STEP ------------------------------->
<!--  EAR STEP ------------------------------->
<!--  EAR STEP ------------------------------->
<!--  EAR STEP ------------------------------->
<form name="f6" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<!-- orecchio destro step -->
<div class="parteDX">ear right step [CH_avance]
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!--<input type="text" name="valore[]" value="0" size="3">-->
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_avance ?>" readonly size="1">
<!-- dx o sx -->
<input name="valore[]" value="0" readonly size="1" class="ColoreReadonly">
<!-- steps -->
<input name="valore[]" value="0" size="2">
</div><div class="parteSX">
<input type="submit" name="f6Form" value="insert">
</div>
</form>

<!--  EAR STEP ------------------------------->
<!--  EAR STEP ------------------------------->
<!--  EAR STEP ------------------------------->
<!--  EAR STEP ------------------------------->
<form name="f7" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<!-- orecchio sinistro step -->
<div class="parteDX">ear left step [CH_avance]
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!--<input type="text" name="valore[]" value="0" size="3">-->
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_avance ?>" readonly size="1">
<!-- dx o sx -->
<input name="valore[]" value="1" readonly size="1" class="ColoreReadonly">
<!-- steps -->
<input name="valore[]" value="0" size="2">
</div><div class="parteSX">
<input type="submit" name="f7Form" value="insert">
</div>
</form>

<!-- LED --------------------------------------------->
<!-- LED --------------------------------------------->
<!-- LED --------------------------------------------->
<!-- LED --------------------------------------------->
<?php
for($a=0;$a<5;$a++) {
//	echo "<br />";
	$t=$a+8;
	echo "<form name='f".$t."' action='".$_SERVER['PHP_SELF']."' method='POST'>";
    echo "<input name='nomeFile' type='hidden' value='$nomeFile'>";
	echo "<div class='parteDX'>";
	echo "- ".$posizioneLed[$a]." [CH_set_led_color]";
//    echo "<input type='text' name='valore[]' value='0' size='3'>";
    echo "<input type='number' name='valore[]' value='0' min='0' max='255'>";
    echo "<input class='ColoreCH' name='valore[]' value='".CH_set_led_color."' readonly size='1'>";
	echo "<input type='text' name='valore[]' value='".$a."' readonly size='1' class='ColoreReadonly'>";
    echo "<input type='text' name='valore[]' value='0' size='3'>";
	echo "<input type='text' name='valore[]' value='0' size='3'>";
    echo "<input type='text' name='valore[]' value='0' size='3'>";
    echo "<input type='text' name='valore[]' value='0' size='1' readonly class='ColoreReadonly'>";
    echo "<input type='text' name='valore[]' value='0' size='1' readonly class='ColoreReadonly'>";

	echo "
<select name='valore[]' onchange='colore(4,2,\"f".$t."\",\"f".$t."Colore\");'>
 <option value='0,0,0'>off(black)</option>
 <option value='192,192,192'>GREY</option>
 <option value='173,255,47'>LIGHT_GREEN</option>
 <option value='255,0,0'>red</option>
 <option value='255,127,0'>orange</option>
 <option value='255,255,0'>yellow</option>
 <option value='0,255,0'>green</option>
 <option value='0,0,255'>blue</option>
 <option value='255,0,255'>purple</option>
 <option value='127,0,0'>dim_red</option>
 <option value='127,63,0'>dim_orange</option>
 <option value='127,127,0'>dim_yellow</option>
 <option value='0,127,0'>dim_green</option>
 <option value='0,0,127'>dim_blue</option>
 <option value='127,0,127'>dim_purple</option>
</select>	
<span id='f".$t."Colore' style='border-radius:50px;background-color: rgb(0,0,0);'>&nbsp&nbsp</span>
	";
echo "</div><div class='parteSX'>";
    echo "<input type='submit' name='f".$t."Form' value='insert'>";
echo "</div>";	
    echo "</form>";
}
?>

<!-- LED TUTTI ------------------>
<!-- LED TUTTI ------------------>
<!-- LED TUTTI ------------------>
<!-- LED TUTTI ------------------>
<form name="f13" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<div class="parteDX">LEDS ALL [CH_set_leds_color]
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!--<input type="text" name="valore[]" value="0" size="3">-->
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_set_leds_color ?>" readonly size="1">
<input type="text" name="valore[]" value="0" size="3">
<input type="text" name="valore[]" value="0" size="3">
<input type="text" name="valore[]" value="0" size="3">
<select name="valore[]" onchange="colore(1,1,'f13','f13Colore');">
 <option value="0,0,0">off(black)</option>
 <option value="192,192,192">GREY</option>
 <option value="173,255,47">LIGHT_GREEN</option>
 <option value="255,0,0">red</option>
 <option value="255,127,0">orange</option>
 <option value="255,255,0">yellow</option>
 <option value="0,255,0">green</option>
 <option value="0,0,255">blue</option>
 <option value="255,0,255">purple</option>
 <option value="127,0,0">dim_red</option>
 <option value="127,63,0">dim_orange</option>
 <option value="127,127,0">dim_yellow</option>
 <option value="0,127,0">dim_green</option>
 <option value="0,0,127">dim_blue</option>
 <option value="127,0,127">dim_purple</option>
</select>
<span id="f13Colore" style="border-radius:50px;background-color: rgb(0,0,0);">&nbsp&nbsp</span>
</div><div class="parteSX">
<input type="submit" name="f13Form" value="insert">
</div>
</form>

<!-- LEDS OFF ---------------------->
<!-- LEDS OFF ---------------------->
<!-- LEDS OFF ---------------------->
<!-- LEDS OFF ---------------------->
<form name="f14" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<div class="parteDX">led off [CH_set_led_off]
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!--<input type="text" name="valore[]" value="0" size="3">-->
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_set_led_off ?>" readonly size="1">
<input type="text" name="valore[]" value="0" size="1" readonly class="ColoreReadonly">
</div><div class="parteSX">
<input type="submit" name="f14Form" value="insert">
</div>
</form>


<form name="f15" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<!-- set motor dir -->
<div class="parteDX">set motor dir right [CH_setmotordir]
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!--<input type="text" name="valore[]" value="0" size="3">-->
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_setmotordir ?>" readonly size="1">
<!-- dx o sx -->
<input name="valore[]" value="0" size="1" readonly class="ColoreReadonly">
<input name="valore[]" value="0" size="3">
</div><div class="parteSX">
<input type="submit" name="f15Form" value="insert">
</div>
</form>

<form name="f15a" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<!-- set motor dir -->
<div class="parteDX">set motor dir left [CH_setmotordir]
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!--<input type="text" name="valore[]" value="0" size="3">-->
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_setmotordir ?>" readonly size="1">
<!-- dx o sx -->
<input name="valore[]" value="1" size="1" readonly class="ColoreReadonly">
<input name="valore[]" value="0" size="3">
</div><div class="parteSX">
<input type="submit" name="f15aForm" value="insert">
</div>
</form>



<form name="f16" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<!-- set motor dir -->
<div class="parteDX">set palette [CH_set_led_palette]
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!--<input type="text" name="valore[]" value="0" size="3">-->
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_set_led_palette ?>" readonly size="1">
<!-- ?? -->
<input name="valore[]" value="0" size="3">
<input name="valore[]" value="0" size="3">
</div><div class="parteSX">
<input type="submit" name="f16Form" value="insert">
</div>
</form>

<form name="f17" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<!-- set motor dir -->
<div class="parteDX">if=x jump blk of bytes len specified [CH_ifne]
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!--<input type="text" name="valore[]" value="0" size="3">-->
<!-- command -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_ifne ?>" readonly size="1">
<!--  -->
<input name="valore[]" value="0" size="3">
<input name="valore[]" value="0" size="3">
<input name="valore[]" value="0" size="3">
</div><div class="parteSX">
<input type="submit" name="f17Form" value="insert">
</div>
</form>



<!--------------------- FILEMIDI ---------------->
<!--------------------- FILEMIDI ---------------->
<!--------------------- FILEMIDI ---------------->
<!--------------------- FILEMIDI ---------------->
<form name="fMidi" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<input name="nomeFile" type="hidden" value="<? echo $nomeFile; ?>" >
<div class="parteDX">(bootcode modified) filemidi
<!-- ts -->
<input type="number" name="valore[]" value="0" min="0" max="255">
<!-- comando nuovo -->
<input class="ColoreCH" name="valore[]" value="<?php echo CH_file_midi ?>" readonly size="1">
<!-- lun dati midi autogenerati -->
<input type="text" name="valore[]" value="0" size="3">
<input type="text" name="valore[]" value="0" size="3">
<!-- dati in esa -->
<input type="text" name="valore[]">
</div><div class="parteSX">
<input type="submit" name="fMidi" value="insert">
</div>
</form>



</tt>
<hr>



<?php

function visualizza( $nomeFile )
{
 $CH_comandi = array(
   1=>"03CH_frame_duration",
   2=>"05CH_02",
//var CH_set_color=6;;
   7=>"08CH_set_led_color",
   8=>"05CH_set_motor",
   9=>"05CH_set_leds_color",
   10=>"03CH_set_led_off",
   14=>"04CH_set_led_palette",
//var CH_set_palette=15;;
   16=>"02CH_randmidi",
   17=>"04CH_avance",
   18=>"05CH_ifne",
   19=>"02CH_attend",
   20=>"04CH_setmotordir",
   30=>"99CH_file_midi" );

 $contenuto = array();
 if ((file_exists($nomeFile)) && (filesize($nomeFile)>0)) {

	$file = fopen($nomeFile, "rb");
	$contenuto = array();
	$b = fread($file, filesize($nomeFile));
	$contenuto = unpack("C*",$b);
	fclose($file);

    printf("HEADER: len %'04X bytes", ($contenuto[4]+256*$contenuto[3]) );
//    printf("HEADER: lunghezza dati %'04X bytes", ($contenuto[4]+256*$contenuto[3]) );

	//$x = array_pop($contenuto);
	//$x = array_pop($contenuto);
	//$x = array_pop($contenuto);
	//$x = array_pop($contenuto);
	$x = array_shift($contenuto);
	$x = array_shift($contenuto);
	$x = array_shift($contenuto);
	$x = array_shift($contenuto);

    $i = count($contenuto);

	for($v=0;$v<$i;$v++) {
	  printf("<br />[%'04X] TS %'02X ",$v,$contenuto[$v]);
      $v++;
      if ($v>=$i) { break;}
      
      $lenFrame = intval(substr($CH_comandi[$contenuto[$v]],0,2));
	  $lenFrame--;
	  printf("(%'02X) %s", $contenuto[$v],substr($CH_comandi[$contenuto[$v]],2,99));
      $codaSTR = "";
	  if (($contenuto[$v]==18))
	    $codaSTR = sprintf("  **** if %'02X jump to %'04X",$contenuto[$v+1],($v+$contenuto[$v+3]+256*$contenuto[$v+2] + 4));
//	    $codaSTR = sprintf("  **** se %'02X salto a %'04X",$contenuto[$v+1],($v+$contenuto[$v+3]+256*$contenuto[$v+2] + 4));
	  if (($contenuto[$v]==30))
	    $lenFrame = $contenuto[$v+2]+256*$contenuto[$v+1] + 3;

		// anteprima colore
	  if (($contenuto[$v]==7))
    	 echo "<span style='border-radius:50px;background-color: rgb(".$contenuto[$v+2].",".$contenuto[$v+3].",".$contenuto[$v+4].");'>&nbsp&nbsp</span>";
	  if (($contenuto[$v]==9))
    	 echo "<span style='border-radius:50px;background-color: rgb(".$contenuto[$v+1].",".$contenuto[$v+2].",".$contenuto[$v+3].");'>&nbsp&nbsp</span>";
	  while ($lenFrame >1) {
		printf(" %'02X ",$contenuto[++$v]);
		$lenFrame--;
     }
	 echo $codaSTR; 
    }
	
	}
return;

}

?>

</body>
</html>
