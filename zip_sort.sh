#!/bin/bash
# exec 3>&1 4>&2
# trap 'exec 2>&4 1>&3' 0 1 2 3
# exec 1>>/home/pi/code/log/Bira 2>&1

SORT=/home/pi/code/sort/
config_file=/home/pi/code/bash.config
SENDFOLDER=/home/pi/code/send/
SORTFILE=/home/pi/code/sort/* 
RESTOREFOLDER=/home/pi/code/restore/ 

enable_sd="$( jq -r '.enable_save_on_sd' "$config_file" )"
enable_cloud="$( jq -r '.enable_save_on_cloud' "$config_file" )"

{ 
    inotifywait -m -e create -e move --exclude ".filepart$" --exclude ".gz$" --format "%f"  $SORT \
        | while read FILENAME
                do
                        if [[ "$FILENAME" =~ .*mf4$ ]]; then
                                
                                if [ $enable_sd == 'True' ]
                                then
                                        variable=`sudo blkid | awk -F: 'index($1, "/dev/sd") {print $1}'` 
                                        
                                        
                                        USB=/media/my_usb/
                                        sudo umount $USB || true
                                        sudo gzip -r $SORT
                                        for file in $SORTFILE; do
                                                onlyfile="${file##*/}"
                                                if [ $onlyfile != 'start.mf4.gz' ]
                                                then
                                                        if [ $enable_cloud == 'True' ]
                                                        then
                                                                sudo cp $SORT$onlyfile "$SENDFOLDER$onlyfile" || continue
                                                        fi
                                                        sudo mount -o uid=pi $variable $USB && (sudo cp $SORT$onlyfile "$USB$onlyfile" && rm $SORT$onlyfile || sudo umount $USB continue ) || sudo cp $SORT$onlyfile "$RESTOREFOLDER$onlyfile" && rm $SORT$onlyfile
                                                        
                                                        sudo umount $USB || continue
                                                else
                                                        sudo cp $SORT$onlyfile "$SENDFOLDER$onlyfile" && rm $SORT$onlyfile
                                                fi
                                                
                                        done
                                else
                                        sudo gzip -r $SORT 
                                        if [ $enable_cloud == 'True' ]
                                        then
                                                for file in $SORTFILE; do
                                                        onlyfile="${file##*/}"
                                                        sudo cp $SORT$onlyfile "$SENDFOLDER$onlyfile" && rm $SORT$onlyfile
                                                done
                                        fi
                                fi
                
                        fi

                done

} 

# sudo rm $USB"$(ls -t $USB | tail -1)"|| { n=2
# until [ "$n" -ge 5 ]
# do
# sudo rm $USB"$(ls -t $USB | tail -%n)" && break  # substitute your command here
# n=$((n+1)) 
# done
# save log for exception 
#                                                                                                                                              }
# gzsize="$( ls -l $SORT$onlyfile | awk '{print $5}' )"
# mbgzsize="$( bc <<< $gzsize*0.000001 )"

# usbfd="$( df -m /media/my_usb/ | awk '{print $4}' | sed -n 2p )"
# gzsize="$( ls -l $SORT$onlyfile | awk '{print $5}' )"
# mbgzsize="$( bc <<< $gzsize*0.000001 )"
# #echo usb$usbfd gz$gzsize mb$mbgzsize

# if (( $(echo "$usbfd > $mbgzsize" |bc -l) ))
# then
# sudo cp $SORT$onlyfile "$USB$onlyfile" && rm $SORT$onlyfile || sudo umount $USB continue

# fi