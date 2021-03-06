# Nabaztag emulator for Karotz by Carlo64 :-P
# 2015 v 001
#      v 002 add buttons events (one and two click)
#      v3 test with authentication
#      v3.1 add ping
#      v3.2 fix rfid problem..... 
#      v3.3 add taichi add and record voice and fix
#      v3.4 3 click fix
#      v3.5 add auto-re-connect 50try..
#      v3.6 fix taichi at wakeup
import random
import string

import md5
import time, threading
import subprocess
import os.path
import socket    
import sys
import struct
import time
import base64
import re
#
# variables
#
status=0
sleep=0
infoTaichi=0
loopTry=50 ### CHANGE if you want
midiList=["midi_1noteA4","midi_1noteB5","midi_1noteBb4","midi_1noteC5",
"midi_1noteE4","midi_1noteF4","midi_1noteF5","midi_1noteG5","midi_2notesC6C4",
"midi_2notesC6F5","midi_2notesD4A5","midi_2notesD4G4","midi_2notesD5G4",
"midi_2notesE5A5","midi_2notesE5C6","midi_2notesE5E4","midi_3notesA4G5G5",
"midi_3notesB5A5F5","midi_3notesB5D5C6","midi_3notesD4E4G4","midi_3notesE5A5C6",
"midi_3notesE5C6D5","midi_3notesE5D5A5","midi_3notesF5C6G5"]
defaultLedColor='00FF00'
bootVer="18673"
pathAudio='/usr/openkarotz/Extra/A'
pathAudioFile='/usr/openkarotz/Extra/audio.wav'
pathLocate='/usr/openkarotz/Extra/locate.txt'
ledPath ='/usr/openkarotz/Extra/led.txt'
userPath ='/usr/openkarotz/Extra/user.txt'
pathRfid='/usr/openkarotz/Extra/R'
rfidtxt='/usr/openkarotz/Extra/rfid.txt'
path1Click='/usr/openkarotz/Extra/1'
path2Click='/usr/openkarotz/Extra/2'
script = '/usr/openkarotz/Extra/script.sh'

#h = 'ojn.raspberry.pi'
#h = 'openznab.it' 
h = 'openjabnab.fr'   ################# CHANGE HERE
httpPort=':80'; ## :80 or empty for default
port = 5222;
#mac      = "" ################ CHANGE HERE
mac = open('/sys/class/net/wlan0/address').readline().replace('\n', '').replace(':','') #automac (pixel :) )
password = "123456789012"  ################ CHANGE HERE if you want. (12 numbers)
##password = ''.join(random.choice(string.digits) for _ in range(12))
passwordX=''.join(hex( int(a,16) ^ int(b,16) )[2:] for a,b in zip(mac, password))

rgb=['000000','0000ff','00ff00','00ffff','ff0000','ff00ff','ffff00','ffffff']
#none blue green cyan red violet yellow white

# recover info by locate... and find ping server
ping=h
if  os.path.exists(pathLocate):
  subprocess.call(["/bin/rm", pathLocate])

locate='http://'+h+httpPort+'/vl/locate.jsp?sn='+mac+'&h=4&v='+bootVer#####+'18673'
subprocess.call( "/usr/bin/curl -0 -A MTL '"+locate+"' >"+pathLocate, shell=True )
print locate
f=open(pathLocate, "r")
for line in f:
  mm=re.search('ping (.*)\n',line)
  if mm:
    break
if mm:
  ping=mm.group(1)

  print ping

############################
# FUNCTION create sock connection
############################
def createSock( h ):
    ############# Create sock
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print 'Failed to create socket. Exiting...'
        sys.exit()
    print 'Socket Created'
    ############# find ip
    try:
        remote_ip = socket.gethostbyname( h )
    except socket.gaierror:
        print 'Hostname ', h, ' could not be resolved. Exiting...'
        sys.exit()
    ############# connect to...    
    s.connect((remote_ip , port))
    s.setblocking(0)
    print 'Yeee! Socket Connected to ' + h + ' on ip ' + remote_ip
    return s

############################
# FUNCTION restore/set led
############################
def restoreLed( defaultLedColor, ledPath ):
    if os.path.exists(ledPath):
        defaultLedColor = open(ledPath).read().replace('\n','') 
    subprocess.call([script,"leds",defaultLedColor])   
    return defaultLedColor
############################
# FUNCTION taichi
############################
#// 
#// donc si x=30, (x*R)>>7 => 15  45 mn
#// donc si x=40, (x*R)>>7 => 20  61 mn
#// donc si x=80, (x*R)>>7 => 40  122 mn
#    R=60*((rand&127)+64)) => 64  196 mn
#// donc si x=216, (x*R)>>7 => 108  330 mn
#// donc si x=255, (x*R)>>7 => 127  390 mn, soit 2  6,5h
#openjabnab.fr 
#<option value="10" selected >Ultra</option> 0x0a
#<option value="30"  >Beaucoup</option> 0x1e
#<option value="60"  >Souvent</option> 0x3c
#<option value="120"  >Un peu</option> 0x78
#<option value="0"  >Pas de TaiChi</option>
# base source
#<option value="50" <?php if ($frequency==50) echo 'selected'; ?> >Un peu...</option> 0x32
#<option value="125" <?php if ($frequency==125) echo 'selected'; ?>>Beaucoup...</option> 0x7d
#<option value="250" <?php if ($frequency==250) echo 'selected'; ?>>A la folie...</option> 0xfa
#<option value="0" <?php if ($frequency==0) echo 'selected'; ?>>Pas du tout!</option>
# fr      # it      # base 
# 10(0a)  # 255(ff) # 250(fa)   a la folie
# 30(1e)  # 125(7d) # 125(7d)   beaucoup
# 60(3c)  # --      # ---   souvent ###########
# 120(78) # 50(32)  # 50(32)    un peu
# 0       # 0       # 0     pas du tout
def taichi(infoTaichi):
    nextTaichi=0
    if infoTaichi>0:
        if infoTaichi=="ff" or infoTaichi=="fa" or infoTaichi=="0a":
          nextTaichi = random.randint(15,45) #a la folie
        if infoTaichi=="7d" or infoTaichi=="1e":
          nextTaichi = random.randint(20,61) #beaucoup
        if infoTaichi=="3c":
          nextTaichi = random.randint(40,122) #souvent
        if infoTaichi=="32" or infoTaichi=="78":
          nextTaichi = random.randint(64,196) #un peu
    #    if infoTaichi==216:
    #      nextTaichi = random.randint(108,330)
    #    if infoTaichi==255:
    #      nextTaichi = random.randint(127,390)
        nextTaichi=nextTaichi*60 #second
    else:
        nextTaichi=0
    print "next taichi after ....",nextTaichi," seconds..."
    return nextTaichi

############################
# FUNCTION ping (or similar..) v3.1
############################
def testPing():
    global s
    global status

    status=status+1
    if status>1:
        print "DISCONNECT!", status
        s.close()
    else:  
        m='<presence from=\''+mac+'@'+h+'/idle\' id=\'1\'></presence>'
        print "PING!",m,status
        sendmsg(s,m)
    # every 30 seconds (to much?)
##    if status<2:
        threading.Timer(30, testPing).start()
############################
# FUNCTION verify button tot seconds v002
############################
def testButton():
# do something here ... 2 seconds
    global s
    global status
    if  os.path.exists(pathAudio):
      subprocess.call(["/bin/rm", pathAudio])
      subprocess.call(["/bin/rm", pathAudioFile])
      tt = "/usr/bin/ffmpeg -f oss -i /dev/dsp "+pathAudioFile+" -t 00:00:03"
      subprocess.call( tt, shell=True )      
      audio = 'http://'+h+httpPort+'/vl/record.jsp?sn='+mac+'&v='+bootVer+'&h=4&m=0'
      tt = "/usr/bin/curl -0 --header 'Content-Type:application/octet-stream' --data-binary @"+pathAudioFile+" '"+audio+"'"
      subprocess.call( tt, shell=True )      
    if  os.path.exists(pathRfid):
      rfid = open(pathRfid).read().replace('\n','') 
      rfid=rfid.lower()
      subprocess.call(["/bin/rm", pathRfid])
      rfidSend='http://'+h+httpPort+'/vl/rfid.jsp?sn='+mac+'&v='+bootVer+'&h=4&t='+rfid ###+''
      subprocess.call( "/usr/bin/curl -0 -A MTL --header 'Accept: ' --header 'Pragma: no-cache' --header 'Icy-MetaData: 0' --header 'Host: "+ping+"' '"+rfidSend+"' >"+rfidtxt, shell=True )      
      print "rfid send", rfid
    if  os.path.exists(path1Click):
      subprocess.call(["/bin/rm", path1Click])
      m='<message from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' id=\'26\'><button xmlns="violet:nabaztag:button"><clic>1</clic></button></message>'
      sendmsg(s,m)
      print "one button click!",m
    if  os.path.exists(path2Click):
      subprocess.call(["/bin/rm", path2Click])
      m='<message from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' id=\'26\'><button xmlns="violet:nabaztag:button"><clic>2</clic></button></message>'
      sendmsg(s,m)
      print "two button click!",m
    threading.Timer(2, testButton).start()
############################
# FUNCTION decode msg packet
############################
def decodeString( orig ):
    currentChar = 35
    x=''
    for i in range(1,len(orig)-2,2):
      code = int(orig[i+1:i+3],16)
      currentChar = ((code -47)*(1+2*currentChar))%256
      x=x+chr(currentChar)
    return x
############################
# FUNCTION socket send data
############################
def sendmsg(s,m):
    #c#print 'send:',m
    try :
      #Set the whole string
      s.sendall(m)
    except socket.error:
      #Send failed
      #c#print 'Send failed'
      sys.exit()
    return
############################
# FUNCTION socket receive date (change timeout for slow conection)
############################
def recv_timeout(the_socket,timeout=1):
    #make socket non blocking
    the_socket.setblocking(0)
     
    #total data partwise in an array
    total_data=[];
    data='';
     
    #beginning time
    begin=time.time()
    while 1:
        #if you got some data, then break after timeout
        if total_data and time.time()-begin > timeout:
            break
         
        #if you got no data at all, wait a little longer, twice the timeout
        elif time.time()-begin > timeout*2:
            break
         
        #recv something
        try:
            data = the_socket.recv(1024)
            if data:
                total_data.append(data)
                #change the beginning time for measurement
                begin=time.time()
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass
     
    #join all parts to make final string
    return ''.join(total_data)

############################
# FUNCTION socket send and receive data
############################
def sendANDreceive( s, m ):
    #c#print 'send:',m
    try :
      #Set the whole string
      s.sendall(m)
    except socket.error:
      #Send failed
      #c#print 'Send failed'
      sys.exit()
    d = recv_timeout(s)
    print 'receive:',d
    return d
    
######
#
# Hey Ho, Lets Go!
#
######
while loopTry>0:
    ### removes any pending actions
    if  os.path.exists(pathAudio):
      subprocess.call(["/bin/rm", pathAudio])
      subprocess.call(["/bin/rm", pathAudioFile])
    if  os.path.exists(pathRfid):
      subprocess.call(["/bin/rm", pathRfid])
    if  os.path.exists(path1Click):
      subprocess.call(["/bin/rm", path1Click])
    if  os.path.exists(path2Click):
      subprocess.call(["/bin/rm", path2Click])

    status=0
    sleep=0
    infoTaichi=0
    loopTry=loopTry-1
    
    s = createSock( h )

    m = "<?xml version='1.0' encoding='UTF-8'?><stream:stream to='"+h+"' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"
    d = sendANDreceive(s,m)
    ### 1 # test if already register (file user.txt with mac address)
    already=''
    if os.path.exists(userPath):
        already = open(userPath).read().replace('\n','') 
    if already!=mac:
        m = "<iq type='get' id='1'><query xmlns='violet:iq:register'/></iq>"
        d = sendANDreceive(s,m)
        m="<iq to='"+h+"' type='set' id='2'><query xmlns=\"violet:iq:register\"><username>"+mac+"</username><password>"+passwordX+"</password></query></iq>"
        d = sendANDreceive(s,m)

    m = "<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='DIGEST-MD5'/>"
    d = sendANDreceive(s,m)
    ### 2
    a= repr(d)
    mm = re.search('>(.+)</challenge>', a)
    if mm:
      #b=mm.group(0)
      c=mm.group(1)
      d=base64.b64decode(c)
      mm = re.search('nonce=\"(.+)\",qop', d)
      #b=mm.group(0)
      c=mm.group(1)
    else:
      print 'Error fase 2 nonce not found :('
      sys.exit()   
      
    nc="00000001"
    nonce = c
    #         1234567890123
    #cnonce = '4840560059474'+chr(0)
    cnonce = ''.join(random.choice(string.digits) for _ in range(13))
    cnonce = cnonce + chr(0)
    digest_uri="xmpp/"+h

    # crypt crypt
    c1=md5.new()
    c1.update(mac + "::" + password)
    c2=md5.new()
    c2.update(c1.digest() + ":" + nonce + ":" + cnonce)
    HA1 = c2.hexdigest()
    c3=md5.new()

    mode="AUTHENTICATE"
    c3.update(mode + ":" + digest_uri)
    HA2=c3.hexdigest()
    c4=md5.new()
    c4.update(HA1 + ":" + nonce + ":" + nc + ":" + cnonce + ":auth:" + HA2)
    response=c4.hexdigest()
    other = ',nc='+nc+',qop=auth,digest-uri="'+digest_uri+'",response='+response+',charset=utf-8'
    stringa = 'username="'+mac+'",nonce="'+nonce+'",cnonce="'+cnonce+'"'+other
    a=base64.b64encode(stringa)
    #print ": ",response

    m = '<response xmlns="urn:ietf:params:xml:ns:xmpp-sasl">'+a+'</response>'
    d = sendANDreceive(s,m)

    #riceive ok register <challenge xmlns='urn:ietf:params:xml:ns:xmpp-sasl'>cnNwYXV0aD1iNTk4NDM1NjY2OWJhM2JkNWZhMTU1Nzg4YjgyNDJjZg==</challenge>
    mm = re.search('<challenge[^>]*>([^<]*)</challenge>', d)
    if mm:
       text_file = open(userPath, "w")
       text_file.write(mac)
       text_file.close()
       m="<response xmlns='urn:ietf:params:xml:ns:xmpp-sasl'/>"
       d = sendANDreceive(s,m)

    ### 3
    m = "<?xml version='1.0' encoding='UTF-8'?><stream:stream to='"+h+"' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"
    d = sendANDreceive(s,m)
    ### 4
    m='<iq from="'+mac+'@'+h+'/" to="'+h+'" type=\'set\' id=\'1\'><bind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>Boot</resource></bind></iq>'
    d = sendANDreceive(s,m)
    ### 5
    m='<iq from="'+mac+'@'+h+'/boot" to="'+h+'" type=\'set\' id=\'2\'><session xmlns=\'urn:ietf:params:xml:ns:xmpp-session\'/></iq>'
    d = sendANDreceive(s,m)
    ### 6
    m='<iq from=\''+mac+'@'+h+'/boot\' to=\'net.violet.platform@'+h+'/sources\' type=\'get\' id=\'3\'><query xmlns="violet:iq:sources"><packet xmlns="violet:packet" format="1.0"/></query></iq>'
    d = sendANDreceive(s,m)
    ### 7
    m='<iq from="0019db9ed017@'+h+'/boot" to="'+h+'" type=\'set\' id=\'4\'><bind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>idle</resource></bind></iq>'
    d = sendANDreceive(s,m)
    ### 8
    m='<iq from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' type=\'set\' id=\'5\'><session xmlns=\'urn:ietf:params:xml:ns:xmpp-session\'/></iq>'
    d = sendANDreceive(s,m)
    ### 9
    m='<presence from=\''+mac+'@'+h+'/idle\' id=\'6\'></presence>'
    d = sendANDreceive(s,m)
    ### 10
    m='<iq from=\''+mac+'@'+h+'/boot\' to=\''+h+'\' type=\'set\' id=\'7\'><unbind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>boot</resource></unbind></iq>'
    d = sendANDreceive(s,m)
    ### 11
    #
    # End authentication..
    #
        
    print 'Authentication complete....'
    subprocess.call([script, "connect"])
    defaultLedColor = restoreLed( defaultLedColor, ledPath )
    print 'Now wait.... (press ^C to exit)...'
     
    msgExtra=re.findall('<message[^>]*><packet[^>]*>(?:[^<]*)</packet></message>',d)
    l1=len(msgExtra)
    l2=0
    print 'found ',l1, ' message extra..'

    # start thread
    testButton()
    testPing()
    times=int(time.time())
    nextTaichi = taichi(infoTaichi)
    while 1:
        if infoTaichi:
          now=int(time.time())
          if now>(times+nextTaichi) and sleep==0:
              print "TTTTTTTTAAAAAAIIIICCCCHIIIIIII"
              choiceMidi = random.randint(0,len(midiList)-1)
              tt = '/usr/openkarotz/Extra/mid/_'+midiList[ choiceMidi ]+".mp3"
              subprocess.call( 'echo "'+tt+'" >/tmp/tlist.txt', shell=True )
              subprocess.call( '/bin/killall mplayer >> /dev/null 2>> /dev/null', shell=True )
              subprocess.call( '/usr/bin/mplayer -quiet -playlist /tmp/tlist.txt', shell=True )
              z = random.randint(0,31)
              name='/usr/openkarotz/Extra/chor/tmp'+str(z)+'.sh'
              subprocess.call( name, shell=True )
              times=times+nextTaichi
              nextTaichi = taichi(infoTaichi)
              subprocess.call( '/usr/bin/mplayer -quiet -playlist /tmp/tlist.txt', shell=True )
              defaultLedColor = restoreLed( defaultLedColor, ledPath )
    ########################################           
        try:
            s.setblocking(1)
        except socket.error:
            print 'ERRORE SOCK'
            break
        da=''
        if l1>0:
            da=msgExtra[l2]
            l2=l2+1
            l1=l1-1
        else:
            try:
                da = s.recv(1024)    
            except socket.error:
                print 'ERRORE SOCK'
                break
        if len(da)>0:
          a= repr(da)
          mm=re.match('"<presence',a)
          if mm:
            print "PONG!"
            status = status - 1 
            
          if status>1:
            break #exit main loop while.............. ping fail
            
          print ':', a
          mm=re.search('<message[^>]*><packet[^>]*>([^<]*)</packet></message>',a)
          if not mm:
            print 'error search message: unknown or ping'
            c="7f0000000000000000"
            ###sys.exit()            
          else:
            c=mm.group(1)
            #c#print 'packet:',c
            a=base64.b64decode(c)
            b=''
            c=b.join(x.encode('hex') for x in a)

          print "<<<<<<< ",c
    ######################## sleep
          if c[0:14]=='7f0b00000101ff':
            sleep=1
            #c#print 'sleep packet'
            subprocess.call([script, "sleep"])
            ##from subprocess import Popen  
            ##p = Popen(csleep, shell=True) 
    # responce
            m='<iq from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' type=\'set\' id=\'16\'><bind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>asleep</resource></bind></iq>'
            sendmsg(s,m)
            d = recv_timeout(s)
            #c#print 'sleep (1):',d
    ##<iq from="0013d3846d30@ojn.raspberry.pi/idle" to="ojn.raspberry.pi" type='set' id='16'><bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><resource>asleep</resource></bind></iq>        
    #wait        
            m='<iq from=\''+mac+'@'+h+'/asleep\' to=\''+h+'\' type=\'set\' id=\'17\'><session xmlns=\'urn:ietf:params:xml:ns:xmpp-session\'/></iq>'
            sendmsg(s,m)
            d = recv_timeout(s)
            #c#print 'sleep (2):',d
    #<iq from='0013d3846d30@ojn.raspberry.pi/asleep' to='ojn.raspberry.pi' type='set' id='17'><session xmlns='urn:ietf:params:xml:ns:xmpp-session'/></iq>
    #wait
            m='<presence from=\''+mac+'@'+h+'/asleep\' id=\'18\'></presence>'
            sendmsg(s,m)
            d = recv_timeout(s)
            #c#print 'sleep (3):',d
    #<presence from='0013d3846d30@ojn.raspberry.pi/asleep' id='18'></presence>
    #wait
            m='<iq from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' type=\'set\' id=\'19\'><unbind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>idle</resource></unbind></iq>'
            sendmsg(s,m)
            d = recv_timeout(s)
            #c#print 'sleep (4):',d
            print 'I am sleeping...'
    #<iq from='0013d3846d30@ojn.raspberry.pi/idle' to='ojn.raspberry.pi' type='set' id='19'><unbind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><resource>idle</resource></unbind></iq>
    #wait

    ######################## wakeup
          if c[0:14]=='7f0b00000100ff':
            times=int(time.time())          #fix v3.6
            nextTaichi = taichi(infoTaichi) #fix v3.6
            #c#print 'wakeup packet'
            sleep=0
            subprocess.call([script,"wakeup"])
            #from subprocess import Popen  
            #p = Popen(cwakeup, shell=True) 
    # responce
            m='<iq from=\''+mac+'@'+h+'/asleep\' to=\''+h+'\' type=\'set\' id=\'20\'><bind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>idle</resource></bind></iq>'
            sendmsg(s,m)
            d = recv_timeout(s)
            #c#print 'wakeup (1):',d
    #<iq from="0013d3846d30@ojn.raspberry.pi/asleep" to="ojn.raspberry.pi" type='set' id='20'><bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><resource>idle</resource></bind></iq>
    #wait        
            m='<iq from=\''+mac+'@'+h+'/asleep\' to=\''+h+'\' type=\'set\' id=\'21\'><session xmlns=\'urn:ietf:params:xml:ns:xmpp-session\'/></iq>'
            sendmsg(s,m)
            d = recv_timeout(s)
            #c#print 'wakeup (2):',d
    #<iq from='0013d3846d30@ojn.raspberry.pi/idle' to='ojn.raspberry.pi' type='set' id='21'><session xmlns='urn:ietf:params:xml:ns:xmpp-session'/></iq>
    #wait
            m='<presence from=\''+mac+'@'+h+'/idle\' id=\'22\'></presence>'
            sendmsg(s,m)
            d = recv_timeout(s)
            #c#print 'wakeup (3):',d
    #<presence from='0013d3846d30@ojn.raspberry.pi/idle' id='22'></presence>
    #wait
            m='<iq from=\''+mac+'@'+h+'/asleep\' to=\''+h+'\' type=\'set\' id=\'19\'><unbind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>asleep</resource></unbind></iq>'
            sendmsg(s,m)
            d = recv_timeout(s)
            #c#print 'wakeup (4):',d
            print 'I am wake up...'
            #<iq from='0013d3846d30@ojn.raspberry.pi/asleep' to='ojn.raspberry.pi' type='set' id='23'><unbind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><resource>asleep</resource></unbind></iq>
    #wait
    #
          if c[0:12]=='7f09000000ff':
            # reboot
            subprocess.call([script,"reboot"])
    ########################
    #
    # KAROTZ dedicated :)
    #
    ######################## 
          if c[0:12]=='7fcc000001ff':
            # karotz 000001
            subprocess.call([script,"k000001"])
          if c[0:12]=='7fcc000002ff':
            # karotz 000002
            subprocess.call([script,"k000002"])
          if c[0:12]=='7fcc000003ff':
            # karotz 000003
            subprocess.call([script,"k000003"])
    ########################
    #
    # 
    #
    ######################## 
          if c[0:4]=='7f04':
            dx=False
            sx=False        
            #c#print 'msg type 04 Ambient block'
            l = int(c[8:10],16)  
            #c#print ' len: ', l
            l = l*2 + 18 - 8
            # len not used...
            #c#print 'dati:', c[18:l]
            type = c[18:20]
    #### move ears        
            if type=='04': #ear dx must 04xx05xx
              #c#print 'type ears', type
              dx = c[20:22]
              sx = c[24:26]
              rst='1'
              if (dx=='00') and (sx=='00'):
                 rst='0' #do reset
              subprocess.call([script,"ears",str(int(sx,16)),str(int(dx,16)),rst])
    ### others (to do)
            if type=='00': #disable
              print 'type disable', type, c[20:22]
            if type=='01': #meteo
              print 'type meteo', type, c[20:22]
            if type=='02': #borse
              print 'type borse', type, c[20:22]
            if type=='03': #traffic
              print 'type traffic', type, c[20:22]
            if type=='06': #mail
              print 'type mail', type, c[20:22]
            if type=='07': #air
              print 'type air', type, c[20:22]
            if type=='08': #blinknose
              print 'type blinknose', type, c[20:22]
    ### color breath    
            if type=='09': #ledbreath
              print 'type ledbreath', type, c[20:22]
              color = rgb[ int(c[20:22],16) ]
              subprocess.call([script,"leds",color])
            
    #openjabnab.fr !!!!
            if type=='21': #ledbreath
              print 'OPENJABNAB.FR type ledbreath', type, c[20:22]
              color = rgb[ int(c[20:22],16) ]
              subprocess.call([script,"leds",color])
            if type=='22': #set volume
              print 'OPENJABNAB.FR type volume', type, c[20:22]
              #volume = rgb[ int(c[20:22],16) ]
              #subprocess.call([script,"volume",volume])
            if type=='23': #set taichi
              print 'OPENJABNAB.FR type taichi', type, c[20:22]
              infoTaichi = c[20:22]
              #subprocess.call([script,"taichi",taichi])
     
    ### others..
            if type=='0e': #taichi
              print 'type taichi', type, c[20:22]
              infoTaichi = c[20:22]
    ### block crypt message....
          if c[0:4]=='7f0a':
            ##print 'msg type 0a message block'
            l = int(c[8:10],16)
            hb = int(c[6:8],16)
            print ' len ', l, hb
            l = l*2 + 10 - 2 + hb*256
            # len not used...
            #l = len(c) -10
            ##print ' dati ', c[10:l]
            #decode
            P=c[10:] #l
            sound = decodeString( P )
            print sound
            #,sound.encode('hex')
            print c
            listn=re.split('[\n]+',sound) #create list by newline
            newlistn=[]     
            for elink in listn:
                repStr = 'http://'+h
                el=re.sub('broadcast',repStr,elink) #
                mw = re.search('^MW([^.]*)', el) # excludes MW
                si = re.search('^SI([^.]*)', el) # excludes SI
                se = re.search('^SE([^.]*)', el) # excludes SE
                pl = re.search('^PL([^.]*)', el) # excludes PL
    #add type for openjabnab.fr !!!
                rb = re.search('^RB([^.]*)', el) # excludes RB (reset bunny??)
                gv = re.search('^GV([^.]*)', el) # volume ?!
                if not mw and not si and not se and not pl and not rb and not gv:
                  newlistn.append(el)     
            tt=''
            #commandLen=len(newlistn)
            for el in newlistn:
                sound=''  
                mm = re.search('MU (.+)', el) #mp3
                if mm:
                  sound=mm.group(1)             
                mm = re.search('^ST (.+)', el)  #stream
                if mm:
                  sound=mm.group(1)
                tt=tt+sound+'\n'

            subprocess.call( 'echo "'+tt+'" >/tmp/list.txt', shell=True )
            subprocess.call( '/bin/killall mplayer >> /dev/null 2>> /dev/null', shell=True )
            subprocess.call( '/usr/bin/mplayer -quiet -playlist /tmp/list.txt &', shell=True )
            

    #Close the socket
    s.close()
    # end :-(

