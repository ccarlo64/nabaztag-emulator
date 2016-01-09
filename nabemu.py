#! /usr/bin/python
#
# Nabaztag emulator for Karotz by Carlo64 :-P
# 2016 v 004
# Happy New Year

import random
import string
import md5
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
errorSOCK=0
later=0.3 #delay between send and receive
logSW=0 # value: 0 nothing, 1 write file log.txt (warning no size control), 2 console
sleep=0
infoTaichi=0
loopTry=100 ### CHANGE if you want
midiList=["midi_1noteA4","midi_1noteB5","midi_1noteBb4","midi_1noteC5",
"midi_1noteE4","midi_1noteF4","midi_1noteF5","midi_1noteG5","midi_2notesC6C4",
"midi_2notesC6F5","midi_2notesD4A5","midi_2notesD4G4","midi_2notesD5G4",
"midi_2notesE5A5","midi_2notesE5C6","midi_2notesE5E4","midi_3notesA4G5G5",
"midi_3notesB5A5F5","midi_3notesB5D5C6","midi_3notesD4E4G4","midi_3notesE5A5C6",
"midi_3notesE5C6D5","midi_3notesE5D5A5","midi_3notesF5C6G5"]
defaultLedColor='00FF00'
bootVer="18673"
pathBase='/usr/openkarotz/Extra/'
pathAudio=pathBase+'A'
pathAudioFile=pathBase+'audio.wav'
pathLocate=pathBase+'locate.txt'
pathUser =pathBase+'user.txt'
pathRfid=pathBase+'R'
rfidtxt=pathBase+'rfid.txt'
path1Click=pathBase+'1'
path2Click=pathBase+'2'
script=pathBase+'script.sh'
logFile=pathBase+'log.txt'

def pollButton():
    print "pollButton.."
    if  os.path.exists(pathAudio):
      subprocess.call(["/bin/rm", pathAudio])
      subprocess.call(["/bin/rm", pathAudioFile])
      tt = "/usr/bin/ffmpeg -f oss -i /dev/dsp "+pathAudioFile+" -t 00:00:03"
      subprocess.call( tt, shell=True )      
      audio = 'http://'+h+httpPort+'/vl/record.jsp?sn='+mac+'&v='+bootVer+'&h=4&m=0'
      tt = "/usr/bin/curl -0 --header 'Content-Type:application/octet-stream' --data-binary @"+pathAudioFile+" '"+audio+"'"
#      subprocess.call( tt, shell=True )      
      subprocess.Popen( tt, shell=True )  # dont wait    
      debugLog( 'rcord audio file: ' )
    if  os.path.exists(pathRfid):
      rfid = open(pathRfid).read().replace('\n','') 
      rfid=rfid.lower()
      subprocess.call(["/bin/rm", pathRfid])
      rfidSend='http://'+h+httpPort+'/vl/rfid.jsp?sn='+mac+'&v='+bootVer+'&h=4&t='+rfid ###+''
#      subprocess.call( "/usr/bin/curl -0 -A MTL --header 'Accept: ' --header 'Pragma: no-cache' --header 'Icy-MetaData: 0' --header 'Host: "+ping+"' '"+rfidSend+"' >"+rfidtxt, shell=True )      
      subprocess.Popen( "/usr/bin/curl -0 -A MTL --header 'Accept: ' --header 'Pragma: no-cache' --header 'Icy-MetaData: 0' --header 'Host: "+ping+"' '"+rfidSend+"' >"+rfidtxt, shell=True )   # dont wait
      debugLog( 'rfid: ' + rfid )
    if  os.path.exists(path1Click):
      subprocess.call(["/bin/rm", path1Click])
      m='<message from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' id=\'26\'><button xmlns="violet:nabaztag:button"><clic>1</clic></button></message>'
      sendmsg(s,m)
      debugLog( 'one button click: ' + m )
    if  os.path.exists(path2Click):
      subprocess.call(["/bin/rm", path2Click])
      m='<message from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' id=\'26\'><button xmlns="violet:nabaztag:button"><clic>2</clic></button></message>'
      sendmsg(s,m)
      debugLog( 'two button click: ' + m )  
############################
# FUNCTION write debug log 
############################
def debugLog( txt ): #v4
    n = "( " + time.strftime("%c") + " ) "
    if logSW==1:
       subprocess.call( 'echo "'+n+txt+'" >> '+logFile, shell=True )  
    if logSW==2:
       print n, txt
    return
############################
# FUNCTION restore/set led
############################
def restoreLed( defaultLedColor ):
    subprocess.call([script,"leds",defaultLedColor])   
    return
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
    if infoTaichi!='00':
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
    ##else: #-v4
        ##nextTaichi=0 #-v4
    ##print "next taichi after ....",nextTaichi," seconds..."
    return nextTaichi    
############################
# FUNCTION move ears 04 e 05 type in packet not used for now
############################
def moveEars( dx, sx ):
    rst='1'
    if (dx=='00') and (sx=='00'):
        rst='0' #do reset
    subprocess.call([script,"ears",str(int(sx,16)),str(int(dx,16)),rst])    
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
    global later    
    try :
      s.sendall(m)
    except socket.error, e:
        debugLog( 'SENDMSG: sendmsg' )               
        sys.exit()
##    debugLog( 'sendmsg: ' + m )        
    time.sleep( later )
    return
############################
# FUNCTION socket send and receive data
############################
def sendANDreceive( s, m ):
    d=''
    global later
    global errorSOCK
    try :
      s.sendall(m)
    except socket.error, e:
      debugLog( 'SENDANDRECEIVE: sendall' )
      #sys.exit()
      errorSOCK=1
    time.sleep( later )
    try:
      d = s.recv(1024)
    except socket.error, e:
      debugLog( 'SENDANDRECEIVE: recv' )               
      #sys.exit() 
      errorSOCK=1      
#    d = recv_timeout(s)
    debugLog( 'send: ' + m )
    debugLog( 'receive: ' + d )
    return d
########################
# MAIN 
########################
#h = 'ojn.raspberry.pi'
#h = 'openjabnab.nappey.org'
#h = 'openznab.it' 
h = 'openjabnab.fr'   ################# CHANGE HERE
httpPort= ':80' #':20081' #':80' ## :80 or empty for default
port = 5222 # 5222 default
#mac      = "" ################ CHANGE HERE
mac = open('/sys/class/net/wlan0/address').readline().replace('\n', '').replace(':','') #automac (pixel :) )

password = "123456789012"  ################ CHANGE HERE if you want. (12 numbers)
##password = ''.join(random.choice(string.digits) for _ in range(12))
passwordX=''.join(hex( int(a,16) ^ int(b,16) )[2:] for a,b in zip(mac, password))

rgb=['000000','0000ff','00ff00','00ffff','ff0000','ff00ff','ffff00','ffffff']
#none blue green cyan red violet yellow white

if  os.path.exists(pathLocate):
  subprocess.call(["/bin/rm", pathLocate])
if  os.path.exists(logFile):
  subprocess.call(["/bin/rm", logFile])
  
# get file locate... 
ping=h  
locate='http://'+h+httpPort+'/vl/locate.jsp?sn='+mac+'&h=4&v='+bootVer#####+'18673'
subprocess.call( "/usr/bin/curl -0 -A MTL '"+locate+"' >"+pathLocate, shell=True )

f=open(pathLocate, "r")
try:
  for line in f:
    mm=re.search('ping.*:(.*)',line)
    if mm:
      httpPort=':'+mm.group(1)
      mm=re.search('ping (.*):.*',line)
      ping=mm.group(1)
    zz=re.search('xmpp_domain.*:(.*)',line)
    if zz:
      port=int(zz.group(1),10)
      zz=re.search('xmpp_domain (.*):.*',line)
      h=zz.group(1)      
    #  break
finally:
    f.close()
    
debugLog( ' locate file ' + locate )
debugLog( ' ping server ' + ping )
debugLog( ' http port ping server ' + httpPort )
debugLog( ' server xmpp ' + h )
debugLog( ' port xmpp ' + str(port) )
    
######
#
# Hey Ho, Lets Go!
#
######
while loopTry>0:
    # v4 remove sleep status file (openkarotz)
    sleepFile1 = '/usr/openkarotz/Run/karotz.sleep'
    sleepFile2 = '/usr/openkarotz/Run/karotz.time.sleep'
    if  os.path.exists(sleepFile1):
      subprocess.call(["/bin/rm", sleepFile1])    
    if  os.path.exists(sleepFile2):
      subprocess.call(["/bin/rm", sleepFile2])
    ##  
    if  os.path.exists(pathAudio):
      subprocess.call(["/bin/rm", pathAudio])
      subprocess.call(["/bin/rm", pathAudioFile])
    if  os.path.exists(pathRfid):
      subprocess.call(["/bin/rm", pathRfid])
    if  os.path.exists(path1Click):
      subprocess.call(["/bin/rm", path1Click])
    if  os.path.exists(path2Click):
      subprocess.call(["/bin/rm", path2Click])

    sleep=0
    infoTaichi='00'
    loopTry=loopTry-1
    errorSOCK=0
    
##    s = createSock( h, port )
    try:
        ip = socket.gethostbyname( h )
    except socket.error, e:
        debugLog( 'CREATESOCK: ' + e.strerror )
        sys.exit()
    ##
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip , port))
        s.setblocking(1)
        s.settimeout(2.0) # 20
    except socket.error, e:
        debugLog( 'CREATESOCK: ' + e.strerror )
        sys.exit()
    print 'Yeee! Socket Connected to ' + h + ' on ip ' + ip
    
    m = "<?xml version='1.0' encoding='UTF-8'?><stream:stream to='"+h+"' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"
    d = sendANDreceive(s,m)
    ### 1 # test if already register (file user.txt with mac address)
    already=''
    if os.path.exists(pathUser):
        already = open(pathUser).read().replace('\n','') 
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
      debugLog('INIT: Error fase 2 nonce not found :(')
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
    
    m = '<response xmlns="urn:ietf:params:xml:ns:xmpp-sasl">'+a+'</response>'
    d = sendANDreceive(s,m)
    #riceive ok register <challenge xmlns='urn:ietf:params:xml:ns:xmpp-sasl'>cnNwYXV0aD1iNTk4NDM1NjY2OWJhM2JkNWZhMTU1Nzg4YjgyNDJjZg==</challenge>
    mm = re.search('<challenge[^>]*>([^<]*)</challenge>', d)
    if mm:
       text_file = open(pathUser, "w")
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
    bootPacket=re.search('<iq[^>]*><query[^>]*><packet[^>]*>([^<]*)</packet></query></iq>',d) #v4
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
    msgExtra=re.findall('<message[^>]*><packet[^>]*>(?:[^<]*)</packet></message>',d)
    ####
    # 
    # End authentication..
    #
    # boot packet v4 #
    times=int(time.time()) # default  no boot packet
    nextTaichi = taichi(infoTaichi) # default  no boot packet
    if bootPacket:
       c=bootPacket.group(1)
       debugLog( 'boot packet: ' + c )       
       a=base64.b64decode(c)
       b=''
       c=b.join(x.encode('hex') for x in a)
       debugLog( 'boot packet: ' + c )       
       #ears
       dx = c[20:22] #ear 04 e 05
       sx = c[24:26]       
       rst='1'
       if (dx=='00') and (sx=='00'):
           rst='0' #do reset
       ##subprocess.call([script,"ears",str(int(sx,16)),str(int(dx,16)),rst])
       ##moveEars(dx, sx)
       nose = c[28:30] #nose 08
       color = rgb[ int(c[32:34],16) ]   #breath 09    
       ##subprocess.call([script,"leds",color])
       defaultLedColor = color
       infoTaichi = c[36:38] ## taichi 0e or 23
       times=int(time.time())          #fix v3.6
       nextTaichi = taichi(infoTaichi) #fix v3.6
       if c[38:50]=='0b00000100ff':
            debugLog( 'boot ears: ' + dx + sx + ' nose: ' + nose + ' color breath: ' + defaultLedColor + ' taichi: ' + infoTaichi + ' wakeup!')                   
            sleep=0
            subprocess.call([script,"wakeup"])
       restoreLed( defaultLedColor )            
       if c[38:50]=='0b00000101ff':
            sleep=1
            debugLog( 'boot ears: ' + dx + sx + ' nose: ' + nose + ' breath: ' + color + ' taichi: ' + infoTaichi + ' sleep!')                   
            subprocess.call([script, "sleep"])
    debugLog( 'Authentication complete....' )                   
    print 'Now wait.... (press ^C to exit)...'
     
    #msgExtra=re.findall('<message[^>]*><packet[^>]*>(?:[^<]*)</packet></message>',d)
    l1=len(msgExtra)
    l2=0
    debugLog( 'found ' +str(l1) + ' message extra..' )                   

    ##ntestPing()
    idPing=0
    countSec=0
    while 1:
        if infoTaichi!='00':
          now=int(time.time())
          if now>(times+nextTaichi) and sleep==0:
              debugLog( 'start taichi..' )
              choiceMidi = random.randint(0,len(midiList)-1)
              tt = 'echo "'+pathBase+'mid/_'+midiList[ choiceMidi ]+'.mp3" >/tmp/tlist.txt'
              ##tt = 'echo "/usr/openkarotz/Extra/mid/_'+midiList[ choiceMidi ]+'.mp3" >/tmp/tlist.txt'
              stringTmp = ''
              stringTmp = tt + '\n'
              tt = '/bin/killall mplayer >> /dev/null 2>> /dev/null' #x
              stringTmp = stringTmp + tt +'\n'              
              tt = '/usr/bin/mplayer -quiet -playlist /tmp/tlist.txt' #x
              stringTmp = stringTmp + tt +'\n'                            
              #tt = '/usr/openkarotz/Extra/mid/_'+midiList[ choiceMidi ]+".mp3"              
              #subprocess.call( 'echo "'+tt+'" >/tmp/tlist.txt', shell=True )
              #subprocess.call( '/bin/killall mplayer >> /dev/null 2>> /dev/null', shell=True )              
              #subprocess.call( '/usr/bin/mplayer -quiet -playlist /tmp/tlist.txt', shell=True )
              z = random.randint(0,31)
              name=pathBase+'chor/tmp'+str(z)+'.sh'
              #subprocess.call( name, shell=True )
              #subprocess.call( '/usr/bin/mplayer -quiet -playlist /tmp/tlist.txt', shell=True )
              stringTmp = stringTmp + name +'\n'
              tt = '/usr/bin/mplayer -quiet -playlist /tmp/tlist.txt' #x              
              stringTmp = stringTmp + tt +'\n'
            
              tt = script +' leds ' + defaultLedColor
              stringTmp = stringTmp + tt +'\n'
              
              subprocess.call( 'echo "'+stringTmp+'" >'+pathBase+'taichi.sh', shell=True ) #x              
              subprocess.call( '/bin/chmod +x '+pathBase+'taichi.sh', shell=True ) #x     
              # run the file
              name=pathBase+'taichi.sh &'
              subprocess.call( name, shell=True )
              #
              times=times+nextTaichi
              nextTaichi = taichi(infoTaichi)              
              #restoreLed( defaultLedColor )
              debugLog( 'end taichi.. I used: ' + midiList[ choiceMidi ] + ', tmp' + str(z) + ' next taichi after ' +str(nextTaichi))              
    ########################################           
        da=''
        if l1>0:
            da=msgExtra[l2]
            l2=l2+1
            l1=l1-1
        else:
            try:
                if countSec>10: #10*timeout = 20sec
                    countSec=0

                    idPing=idPing+1
                    if idPing>1000:
                       idPing=1
                    m='<presence from=\''+mac+'@'+h+'/idle\' id=\''+str(idPing)+'\'></presence>'
                    print "o" ###,m,status
                    d = sendANDreceive(s,m)
                    if errorSOCK==1:
                      debugLog( 'ERROR: exit loop while, try reconnect..') ## +e.strerror )                
                      break
                    mm=re.search('<message[^>]*><packet[^>]*>([^<]*)</packet></message>',d)
                    if mm: #trovato messaggio nel ping
                      da = d
                    else:
                      da = s.recv(1024)
                else:
                    countSec=countSec+1
                    pollButton()
                    da = s.recv(1024)
                    #timeout 2 sec                                    
            except socket.timeout, e: #v4            
                print "t"
                #debugLog( 'loop while 1 timeout') ## +e.strerror )
            except socket.error, e: #v4            
                debugLog( 'ERROR: loop while sock, try reconnect..') ## +e.strerror )
                break
        ##debugLog( 'rcv data=> ' + da )        
        if len(da)>0:
          debugLog( 'rcv data=> ' + da )                
          a= repr(da)                
          mm=re.search('<message[^>]*><packet[^>]*>([^<]*)</packet></message>',a)
          if mm:
            c=mm.group(1)
            a=base64.b64decode(c)
            b=''
            c=b.join(x.encode('hex') for x in a)            
          debugLog( 'received packet: ' + c )

    ######################## sleep
          if c[0:14]=='7f0b00000101ff':
            sleep=1
            subprocess.call([script, "sleep"])
            m='<iq from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' type=\'set\' id=\'16\'><bind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>asleep</resource></bind></iq>'
            d = sendANDreceive(s,m)
            #
            msgExtra=re.findall('<message[^>]*><packet[^>]*>(?:[^<]*)</packet></message>',d)
            l1=len(msgExtra)
            l2=0            
            #                        
            m='<iq from=\''+mac+'@'+h+'/asleep\' to=\''+h+'\' type=\'set\' id=\'17\'><session xmlns=\'urn:ietf:params:xml:ns:xmpp-session\'/></iq>'
            d = sendANDreceive(s,m)
            m='<presence from=\''+mac+'@'+h+'/asleep\' id=\'18\'></presence>'
            d = sendANDreceive(s,m)
            m='<iq from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' type=\'set\' id=\'19\'><unbind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>idle</resource></unbind></iq>'
            d = sendANDreceive(s,m)
            debugLog( 'going to sleep... ' )
            debugLog( 'found ' +str(l1) + ' message extra in sleep..' )                   
    ######################## wakeup
          if c[0:14]=='7f0b00000100ff':
            times=int(time.time())          #fix v3.6
            nextTaichi = taichi(infoTaichi) #fix v3.6
            sleep=0
            subprocess.call([script,"wakeup"])
            m='<iq from=\''+mac+'@'+h+'/asleep\' to=\''+h+'\' type=\'set\' id=\'20\'><bind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>idle</resource></bind></iq>'
            d = sendANDreceive(s,m)
            #
            msgExtra=re.findall('<message[^>]*><packet[^>]*>(?:[^<]*)</packet></message>',d)
            l1=len(msgExtra)
            l2=0            
            #
            m='<iq from=\''+mac+'@'+h+'/asleep\' to=\''+h+'\' type=\'set\' id=\'21\'><session xmlns=\'urn:ietf:params:xml:ns:xmpp-session\'/></iq>'
            d = sendANDreceive(s,m)
            m='<presence from=\''+mac+'@'+h+'/idle\' id=\'22\'></presence>'
            d = sendANDreceive(s,m)
            m='<iq from=\''+mac+'@'+h+'/asleep\' to=\''+h+'\' type=\'set\' id=\'19\'><unbind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>asleep</resource></unbind></iq>'
            d = sendANDreceive(s,m)
            debugLog( 'I am wake up... ' )
            debugLog( 'found ' +str(l1) + ' message extra in wake up..' )                               
            restoreLed( defaultLedColor )
          if c[0:12]=='7f09000000ff':
            # reboot
            subprocess.call([script,"reboot"])
    ########################
    #
    # KAROTZ dedicated :)
    #
    ######################## 
          ###if sleep==0:
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
              debugLog( 'packet type 04 ears move: ' + dx + '  ' + sx)
    ### others (to do)
            if type=='00': #disable
              debugLog( 'packet disable ' + type + '  ' + c[20:22])
            if type=='01': #meteo
              debugLog( 'packet meteo ' + type + '  ' + c[20:22])
            if type=='02': #borse
              debugLog( 'packet borse ' + type + '  ' + c[20:22])
            if type=='03': #traffic
              debugLog( 'packet traffic ' + type + '  ' + c[20:22])
            if type=='06': #mail
              debugLog( 'packet mail ' + type + '  ' + c[20:22])
            if type=='07': #air
              debugLog( 'packet air ' + type + '  ' + c[20:22])
            if type=='08': #blinknose
              debugLog( 'packet blinknose ' + type + '  ' + c[20:22])
    ### color breath    
            if type=='09': #ledbreath
              color = rgb[ int(c[20:22],16) ]
              subprocess.call([script,"leds",color])
              defaultLedColor = color
              debugLog( 'packet ledbreath ' + type + '  ' + c[20:22] + ' color ' + color )              
    #openjabnab.fr !!!!
            if type=='21': #ledbreath
              color = rgb[ int(c[20:22],16) ]
              subprocess.call([script,"leds",color])
              defaultLedColor = color ##v4
              debugLog( 'OPENJABNAB.FR packet ledbreath ' + type + '  ' + c[20:22] + ' color ' + color )                            
            if type=='22': #set volume
              debugLog( 'OPENJABNAB.FR packet volume ' + type + '  ' + c[20:22] )                            
            if type=='23': #set taichi
              infoTaichi = c[20:22]
              debugLog( 'OPENJABNAB.FR packet taichi ' + type + '  ' + c[20:22] )                            
     
    ### others..
            if type=='0e': #taichi
              debugLog( 'packet taichi ' + type + '  ' + c[20:22] )                            
              infoTaichi = c[20:22]
    ### block crypt message....
          if c[0:4]=='7f0a':
            ##print 'msg type 0a message block'
            l = int(c[8:10],16)
            hb = int(c[6:8],16)
            ##print ' len ', l, hb
            l = l*2 + 10 - 2 + hb*256                        
            debugLog( 'packet messageblock 0a, len ' + str(l) )
            debugLog( 'packet messageblock:  ' + c )                                        
            # len not used...
            #l = len(c) -10
            ##print ' dati ', c[10:l]
            #decode
            P=c[10:] #l
            sound = decodeString( P )
            debugLog( 'packet messageblock: ' + sound )                            
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
            #if sleep==0:
            subprocess.call( 'echo "'+tt+'" >/tmp/list.txt', shell=True )
            subprocess.call( '/bin/killall mplayer >> /dev/null 2>> /dev/null', shell=True )
            subprocess.call( '/usr/bin/mplayer -quiet -playlist /tmp/list.txt &', shell=True )
            #else:
            #  debugLog( 'I would rather sleep than talk!' )                                      
    # endwhile 1       
    #Close the socket
    s.close()
# end :-(


