#!/bin/bash
config_file=/home/pi/code/bash.config

Startfile="$( jq -r '.Startfile' "$config_file" )"
Measurefolder="$( jq -r '.Measurefolder' "$config_file" )"

sudo cp $Startfile "$Measurefolder"

logsize=$( du /home/pi/code/log/ | awk '{print $1}' )
measuresize=$( du /home/pi/code/measure/ | awk '{print $1}' )
sortsize=$( du /home/pi/code/sort/ | awk '{print $1}' )
restoresize=$( du /home/pi/code/restore/ | awk '{print $1}' )
sendsize=$( du /home/pi/code/send/ | awk '{print $1}' ) 

RESTOREFOLDER=/home/pi/code/restore/* 
USB=/media/my_usb/
variable=`sudo blkid | awk -F: 'index($1, "/dev/sd") {print $1}'`

for file in $RESTOREFOLDER; do
        onlyfile="${file##*/}"
        if [ $onlyfile != 'start.mf4.gz' ]
        then
                sudo mount -o uid=pi $variable $USB && (sudo cp $RESTOREFOLDER$onlyfile "$USB$onlyfile" && rm $RESTOREFOLDER$onlyfile || sudo umount $USB continue )
                sudo umount $USB || continue
        fi   
done

for file in /home/pi/code/log/*; do
        filesize=$( stat -c%s $file ) || break
        if (( $(echo "$filesize > 50000" |bc -l) )); then
                sudo rm $file || continue
        fi || true
done || true 

if (( $logsize > 30000 )); then
        rm /home/pi/code/log/* || continue
fi || true

while (( $measuresize > 5000000 )); do
        variable="$(ls -t /home/pi/code/measure/ | tail -1)"
        sudo rm -f /home/pi/code/measure/$variable|| continue
        measuresize=$( du /home/pi/code/measure/ | awk '{print $1}' )
done || true

while (( $sortsize > 2000000 )); do
        variable="$(ls -t /home/pi/code/sort/ | tail -1)"
        sudo rm -f /home/pi/code/sort/$variable || continue
        sortsize=$( du /home/pi/code/sort/ | awk '{print $1}' )
done || true
                    
while (( $restoresize > 2000000 )); do
        variable="$(ls -t /home/pi/code/restore/ | tail -1)"
        sudo rm -f /home/pi/code/restore/$variable || continue
        restoresize=$( du /home/pi/code/restore/ | awk '{print $1}' )
done || true

while (( $sendsize > 5000000 )); do
        variable="$(ls -t /home/pi/code/send/ | tail -1)"
        sudo rm -f /home/pi/code/send/$variable || continue
        sendsize=$( du /home/pi/code/send/ | awk '{print $1}' ) 
done || true








