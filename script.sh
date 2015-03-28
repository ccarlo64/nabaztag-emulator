#!/bin/bash

#echo "parametes $*"
BACK=N
    
case "$1" in
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
    #echo $QUERY_STRING
    export QUERY_STRING
    /usr/www/cgi-bin/leds
    ;;
*)
    #altro
    echo "Option $1 is not processed..."
    ;;
esac
    