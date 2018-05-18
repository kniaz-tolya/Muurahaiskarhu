#!/bin/bash
IFS=' ' read -r -a miners <<< $(cat miners.json| jq -r 'map(.ip) | join(" ")')

j=1
for i in "${miners[@]}"
do
   echo "Querying Miner #$j, IP: $i"
   temp1=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $50'} | awk -F'=' {'print $2'})
   temp2=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $51'} | awk -F'=' {'print $2'})
   temp3=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $52'} | awk -F'=' {'print $2'})
   if [ -z "$temp1" ]; then
     temp1="-1"
   fi
   if [ -z "$temp2" ]; then
     temp2="-1"
   fi
   if [ -z "$temp3" ]; then
     temp3="-1"
   fi
    echo "Chip Temp 1: $temp1"
    echo "Chip Temp 2: $temp2"
    echo "Chip Temp 3: $temp3"
#   curl -i -XPOST 'http://localhost:8086/write?db=minertemp' -u admin:KalkkiPetteri1803influx --data-binary 'temperature,miner='$j' chip1='$temp1',chip2='$temp2',chip3='$temp3
#   curl -i -XPOST 'http://52.212.250.132:8086/write?db=minertemp' -u admin:tamaeivittuolemikaanmysli --data-binary 'temperature,miner='$j' chip1='$temp1',chip2='$temp2',chip3='$temp3
   let j=j+1
done
