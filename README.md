Nabaztag emulator for Karotz
update

2015 v3.x
rfid fix

events: 
1 click ok

2 click ok

3 click start emulator
long click start recorder after sound, 3 second of registration, after the audio file is send to server

taichi experimental (based on nabaztag choreography)
fix and fix..

2015 v 001

prerequisite: Openkarotz

set variables MAC and H with your mac address and your server OJN
in the script
copy the files in '/ usr / openkarotz / Extra /' with ftp or the way you want
if you change the folder name must also customize the variable SCRIPT

add your Karotz server OJN
connect to telnet to Karotz
go to the folder '/ usr / openkarotz / Extra /'
and run python s004.py
.. Wait a few seconds
if all goes well you will see 'Authentication complete ....'

go to set the plugin server OJN:-)

obviously not all work (would be nice) but something already goes ..


** v002 add buttons click
now working one click and two click.

please copy 'dbus_events' into /usr/www/cgi-bin 
backup first the original if you want...  :-)
