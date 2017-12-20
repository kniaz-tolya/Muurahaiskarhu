#!/bin/bash

declare -a arr=("192.168.2.11" "192.168.2.12" "192.168.2.13" "192.168.2.14" "192.168.2.15"
                "192.168.2.16" "192.168.2.17" "192.168.2.18" "192.168.2.19" "192.168.2.20"
                "192.168.2.21" "192.168.2.22")

j=1
for i in "${arr[@]}"
do
   echo "Querying: $i"
   temp1=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $34'} | awk -F'=' {'print $2'})
   temp2=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $35'} | awk -F'=' {'print $2'})
   temp3=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $36'} | awk -F'=' {'print $2'})
   echo $temp1 $temp2 $temp3
   curl -i -XPOST 'http://localhost:8086/write?db=minertemp' -u admin:KalkkiPetteri1803influx --data-binary 'temperature miner='$j'','chip1='$temp1',chip2='$temp2',chip3='$temp3
   let j=j+1
done
