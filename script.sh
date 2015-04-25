#!/bin/bash

#echo "parametes $*"
BACK=N
    
case "$1" in
connect)
    #taichi connect ok
    # ears and led
    /karotz/bin/ears
    # 0 100 0 100
    for ((i=1; i<= 5; i++))
    do
      UUID=$(cat /proc/sys/kernel/random/uuid)
      dbus-send  --system --dest=com.mindscape.karotz.Led /com/mindscape/karotz/Led com.mindscape.karotz.KarotzInterface.light string:"$UUID" string:"123456"
      sleep 0.04
      UUID=$(cat /proc/sys/kernel/random/uuid)
      dbus-send  --system --dest=com.mindscape.karotz.Led /com/mindscape/karotz/Led com.mindscape.karotz.KarotzInterface.light string:"$UUID" string:"000000"
      sleep 0.04
    done
    ;;
sleep)
    #sleep
    shift
    QUERY_STRING=url=$1
    #echo $QUERY_STRING
    export QUERY_STRING
    /usr/www/cgi-bin/sleep
    ;;
sound)    
    #sound bypassed (not used)
    if [ "$2" == 'Y' ]
      then
        BACK=Y
    fi
    shift
    shift
    QUERY_STRING=url=$1
    #echo $QUERY_STRING
    export QUERY_STRING
    export BACK
    /usr/www/cgi-bin/soundMod
    ;;
stream)
    #stream bypassed (not used)
    if [ "$2" == 'Y' ]
      then
        BACK=Y
    fi
    shift
    shift
    QUERY_STRING=url=$1
    #echo $QUERY_STRING
    export QUERY_STRING
    export BACK
    /usr/www/cgi-bin/soundMod 
    ;;
wakeup)
    #wake
    shift
    QUERY_STRING=url=$1
    #echo $QUERY_STRING
    export QUERY_STRING
    /usr/www/cgi-bin/wakeup
    ;;
ears)    
    #ears
    shift
    QUERY_STRING="left=$1&right=$2&noreset=$3"
    #echo $QUERY_STRING
    export QUERY_STRING
    /usr/www/cgi-bin/ears
    ;;
leds)
    #leds
    shift
    QUERY_STRING="pulse=1&color=$1&speed=1100&color2=000000"
    echo $1 >/usr/openkarotz/Extra/led.txt
    #echo $QUERY_STRING
    export QUERY_STRING
    /usr/www/cgi-bin/leds
    ;;
reboot)
    #reboot
    shift
    /sbin/reboot  
    ;;
k000001)
    #karotz 000001 photo to email
    shift
    /usr/www/cgi-bin/snapshot_email
    ;;
*)
    #altro
    echo "Option $1 is not processed..."
    ;;
esac
