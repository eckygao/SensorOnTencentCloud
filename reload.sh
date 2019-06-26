#!/bin/bash

function reload()
{
    propath=$(realpath $1)
    count=$(ps aux | grep $propath | wc -l)
    if [ $count -lt 2 ]
    then
        echo reload $propath
        $propath &
    else
        echo process exists : $propath
    fi
}

dpath=$(dirname $0)

reload $dpath/getdata.py
reload $dpath/flusholed.py
