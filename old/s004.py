# Nabaztag emulator for Karotz by Carlo64 :-P
# 2015 v 001
#
import time, threading
import subprocess
import os.path
import socket    
import sys
import struct
import time
import base64
import re
# variables
#
script = '/usr/openkarotz/Extra/script.sh'
#script = '/tmp/script.sh'
rgb=['000000','0000ff','00ff00','00ffff','ff0000','ff00ff','ffff00','ffffff']
#none blue green cyan red violet yellow white
mac = "000000000000" ################ CHANGE HERE
#h = 'ojn.raspberry.pi'
h = 'openznab.it'   ################# CHANGE HERE
port = 5222;

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

############################
# FUNCTION verify button tot seconds
############################
def testButton():
# do something here ... 2 seconds
    global s
    if  os.path.exists('1'):
      subprocess.call(["rm", "1"])
      m='<message from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' id=\'26\'><button xmlns="violet:nabaztag:button"><clic>1</clic></button></message>'
      sendmsg(s,m)
      print "one button click!"
    if  os.path.exists('2'):
      subprocess.call(["rm", "2"])
      m='<message from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' id=\'26\'><button xmlns="violet:nabaztag:button"><clic>2</clic></button></message>'
      sendmsg(s,m)
      print "two button click!"
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
           # else:
                #sleep for sometime to indicate a gap
            #    time.sleep(0.1)
        except:
            pass
     
    #join all parts to make final string
    return ''.join(total_data)
######
#
# Hey Ho, Lets Go!
#
######
m = "<?xml version='1.0' encoding='UTF-8'?><stream:stream to='"+h+"' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"
sendmsg(s,m)
d = recv_timeout(s)
#c#print 'receive:',d
### 1
m = "<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='DIGEST-MD5'/>"
sendmsg(s,m)
d = recv_timeout(s)
#c#print 'receive:',d
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
  print 'Error fase 2 :('
  sys.exit()    

nonce = c
cnonce = '4840560059474'+chr(0)
other = ',nc=00000001,qop=auth,digest-uri="xmpp/'+h+'",response=566acb262696d7ccdb7523f0e5e8510b,charset=utf-8'
stringa = 'username="'+mac+'",nonce="'+nonce+'",cnonce="'+cnonce+'"'+other
a=base64.b64encode(stringa)
m = '<response xmlns="urn:ietf:params:xml:ns:xmpp-sasl">'+a+'</response>'
sendmsg(s,m)
d = recv_timeout(s)
#c#print 'receive:',d
### 3
m = "<?xml version='1.0' encoding='UTF-8'?><stream:stream to='"+h+"' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"
sendmsg(s,m)
d = recv_timeout(s)
#c#print 'receive:',d
### 4
m='<iq from="'+mac+'@'+h+'/" to="'+h+'" type=\'set\' id=\'1\'><bind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>Boot</resource></bind></iq>'
sendmsg(s,m)
d = recv_timeout(s)
#c#print 'receive:',d
### 5
m='<iq from="'+mac+'@'+h+'/boot" to="'+h+'" type=\'set\' id=\'2\'><session xmlns=\'urn:ietf:params:xml:ns:xmpp-session\'/></iq>'
sendmsg(s,m)
d = recv_timeout(s)
#c#print 'receive:',d
### 6
m='<iq from=\''+mac+'@'+h+'/boot\' to=\'net.violet.platform@'+h+'/sources\' type=\'get\' id=\'3\'><query xmlns="violet:iq:sources"><packet xmlns="violet:packet" format="1.0"/></query></iq>'
sendmsg(s,m)
d = recv_timeout(s)
#c#print 'receive:',d
### 7
m='<iq from="0019db9ed017@'+h+'/boot" to="'+h+'" type=\'set\' id=\'4\'><bind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>idle</resource></bind></iq>'
sendmsg(s,m)
d = recv_timeout(s)
#c#print 'receive:',d
### 8
m='<iq from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' type=\'set\' id=\'5\'><session xmlns=\'urn:ietf:params:xml:ns:xmpp-session\'/></iq>'
sendmsg(s,m)
d = recv_timeout(s)
#c#print 'receive:',d
### 9
m='<presence from=\''+mac+'@'+h+'/idle\' id=\'6\'></presence>'
sendmsg(s,m)
d = recv_timeout(s)
#c#print 'receive:',d
### 10
m='<iq from=\''+mac+'@'+h+'/boot\' to=\''+h+'\' type=\'set\' id=\'7\'><unbind xmlns=\'urn:ietf:params:xml:ns:xmpp-bind\'><resource>boot</resource></unbind></iq>'
sendmsg(s,m)
d = recv_timeout(s)
#c#print 'receive:',d
### 11
#
# End authentication..
#
    
print 'Authentication complete....'
print 'Now wait.... (press ^C to exit)...'
 
testButton()

while 1:

    s.setblocking(1)         
    d=False
    #for button next release...
    if  os.path.exists('xx'):
        #one click
        subprocess.call(["rm", "1"])
        ##from subprocess import Popen  
        ##p = Popen('rm 1', shell=True) 
  #<message from='0013d3846d30@ojn.raspberry.pi/idle' to='int@xmpp.objects.violet.net/int' id='26'><button xmlns="violet:nabaztag:button"><clic>2</clic></button></message>    
        #c#print 'one click'
  # responce
        m='<message from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' id=\'26\'><button xmlns="violet:nabaztag:button"><clic>1</clic></button></message>'
        sendmsg(s,m)
        d = recv_timeout(s)
        #c#print 'click (one):',d
    if  os.path.exists('2'):
        #two click
        subprocess.call(["rm", "2"])
        ##from subprocess import Popen  
        ##p = Popen('rm 1', shell=True) 
  #<message from='0013d3846d30@ojn.raspberry.pi/idle' to='int@xmpp.objects.violet.net/int' id='26'><button xmlns="violet:nabaztag:button"><clic>2</clic></button></message>    
        #c#print 'two click'
  # responce
        m='<message from=\''+mac+'@'+h+'/idle\' to=\''+h+'\' id=\'26\'><button xmlns="violet:nabaztag:button"><clic>2</clic></button></message>'
        sendmsg(s,m)
        d = recv_timeout(s)
        #c#print 'click (two):',d
      
      
    if d:
     da = d
    else:      
     da = s.recv(1024)
     #da = recv_timeout(s)        
    ###c#print '.'
    if len(da)>0:
      #c#print 'receive:', da
      a= repr(da)
#<message[^>]*><packet>([^<]*)</resource></unbind>"),
#<message from='net.openjabnab.platform@ojn.raspberry.pi/services' to='0019db9ed017@ojn.raspberry.pi/Idle' id='OJaNa-12'><packet xmlns='violet:packet' format='1.0' ttl='604800'>fwoAAFMA+v6PEfny7vv6xsCbhiAF5ZrDtizGU3Y7gyqobhDG/zTz+FTMY/iStbDc/wDlxjcgAH8w5hE+SUc0W8NBXSj4N0J/JR/Gjkys1nvtgH/ClYgkRf8=</packet></message>
      mm=re.search('<message[^>]*><packet[^>]*>([^<]*)</packet></message>',a)
      #mm = re.search('>(.+)</message>', a)
      #b=mm.group(0)
      #c=mm.group(1)
      #mm = re.search('>(.+)</packet>', c)
      #b=mm.group(0)
      if not mm:
        print 'error search message!'
        sys.exit()            
      c=mm.group(1)
      #c#print 'packet:',c
      a=base64.b64decode(c)
      b=''
      c=b.join(x.encode('hex') for x in a)
######################## sleep
      if c[0:14]=='7f0b00000101ff':
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
        #c#print 'wakeup packet'
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
########################
#
      if c[0:4]=='7f04':
        dx=False
        sx=False        
        #c#print 'msg type 04 Ambient block'
        l = int(c[8:10],16)  
        #c#print ' len: ', l
        l = l*2 + 18 - 8
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
          #from subprocess import Popen  
          #p = Popen(ctmp, shell=True) 
### others (to do)
        if type=='00': #disable
          print 'type disable', type
        if type=='01': #meteo
          print 'type meteo', type
        if type=='02': #borse
          print 'type borse', type
        if type=='03': #traffic
          print 'type traffic', type
        if type=='06': #mail
          print 'type mail', type
        if type=='07': #air
          print 'type air', type
        if type=='08': #blinknose
          print 'type blinknose', type
### color breath    
        if type=='09': #ledbreath
          #c#print 'type ledbreath', type
          color = rgb[ int(c[20:22],16) ]
          subprocess.call([script,"leds",color])
          #from subprocess import Popen  
          #p = Popen(ctmp, shell=True) 
### others..
        if type=='0e': #taichi
          print 'type taichi', type
### block message....
      if c[0:4]=='7f0a':
        ##print 'msg type 0a message block'
        l = int(c[8:10],16)
        hb = int(c[6:8],16)
        print ' len ', l, hb
        l = l*2 + 10 - 2 + hb*256
        #l = len(c) -10
        ##print ' dati ', c[10:l]
        #decode
        P=c[10:] #l
        sound = decodeString( P )
        ##sound = sound + chr(10)
        print sound
        print c
        commandShell=''
        commandTmp=''
        countCommand=0  
        listn=re.split('[\n]+',sound) #create list by newline

        newlistn=[]
       
        for elink in listn:
            repStr = 'http://'+h
            el=re.sub('broadcast',repStr,elink) #
            mw = re.search('^MW([^.]*)', el) # excludes MW
            si = re.search('^SI([^.]*)', el) # excludes SI
            se = re.search('^SE([^.]*)', el) # excludes SE
            pl = re.search('^PL([^.]*)', el) # excludes PL

            if not mw and not si and not se and not pl:
              newlistn.append(el)     
        tt=''
        commandLen=len(newlistn)
        for el in newlistn:
            countCommand = countCommand + 1
            background='Y'
            if countCommand<commandLen:
              background='N'
            sound=''  
            mm = re.search('MU (.+)', el) #mp3
            if mm:
              c=mm.group(1)
              sound=c
              commandTmp = script+' sound '+ background+ ' '+sound
              
            mm = re.search('^ST (.+)', el)  #stream
            if mm:
              c=mm.group(1)
              sound=c
              commandTmp = script+' stream '+ background+ ' '+sound
            tt=tt+sound+'\n'
            print 'exec ',commandTmp
            ###commandShell = commandShell + commandTmp + ' &&\n' #v2  
            #subprocess.call( commandTmp, shell=True )
        #if countCommand>1:
        subprocess.call( 'echo "'+tt+'" >lista.txt', shell=True )

        subprocess.call( '/bin/killall mplayer >> /dev/null 2>> /dev/null', shell=True )
        subprocess.call( 'mplayer -quiet -playlist lista.txt &', shell=True )
        
        #print commandShell

              #from subprocess import Popen  
              #p = Popen(ctmp, shell=True)

#Close the socket
s.close()
#