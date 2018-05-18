#!/bin/bash

# read miner info to arrays  from json file - requires jq to work
IFS=' ' read -r -a miner_ip <<< $(cat miners.json| jq -r 'map(.ip) | join(" ")')
IFS=' ' read -r -a miner_name <<< $(cat miners.json| jq -r 'map(.name) | join(" ")')
IFS=' ' read -r -a miner_type <<< $(cat miners.json| jq -r 'map(.type) | join(" ")')

# iterate through miners array
j=1
for i in "${miner_ip[@]}"
do
   # reset temperture values
   temp1="-2"
   temp2="-2"
   temp3="-2"
   temp4="-2"
   temp5="-2"
   temp6="-2"

   echo "Querying Miner #$j (${miner_name[$j-1]}), Type: ${miner_type[$j-1]}, IP: $i"

   if [ ${miner_type[$j-1]} == "S9" ];
   then
      echo "Getting chip temps from S9..."
      temp1=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $50'} | awk -F'=' {'print $2'})
      temp2=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $51'} | awk -F'=' {'print $2'})
      temp3=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $52'} | awk -F'=' {'print $2'})
   fi

   if [ ${miner_type[$j-1]} == "X3" ];
   then
      echo "Getting chip temps from X3..."
      temp1=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $24'} | awk -F'=' {'print $2'})
      temp2=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $25'} | awk -F'=' {'print $2'})
      temp3=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $26'} | awk -F'=' {'print $2'})
   fi

   if [ ${miner_type[$j-1]} == "T9" ];
   then
      echo "Getting chip temps from T9..."
      temp1=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $53'} | awk -F'=' {'print $2'})
      temp2=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $54'} | awk -F'=' {'print $2'})
      temp3=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $55'} | awk -F'=' {'print $2'})
      temp4=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $56'} | awk -F'=' {'print $2'})
      temp5=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $57'} | awk -F'=' {'print $2'})
      temp6=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $58'} | awk -F'=' {'print $2'})
   fi

   if [ ${miner_type[$j-1]} == "A3" ];
   then
      echo "Getting chip temps from A3..."
      temp1=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $27'} | awk -F'=' {'print $2'})
      temp2=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $28'} | awk -F'=' {'print $2'})
      temp3=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $29'} | awk -F'=' {'print $2'})
   fi

   if [ ${miner_type[$j-1]} == "L3+" ];
   then
      echo "Getting chip temps from L3+..."
      temp1=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $28'} | awk -F'=' {'print $2'})
      temp2=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $29'} | awk -F'=' {'print $2'})
      temp3=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $30'} | awk -F'=' {'print $2'})
      temp4=$(echo 'stats|0' | nc $i 4028 | awk -F',' {'print $31'} | awk -F'=' {'print $2'})
   fi

   if [ -z "$temp1" ]; then
     temp1="-1"
   fi

   if [ -z "$temp2" ]; then
     temp2="-1"
   fi

   if [ -z "$temp3" ]; then
     temp3="-1"
   fi

   if [ -z "$temp4" ]; then
     temp1="-1"
   fi

   if [ -z "$temp5" ]; then
     temp2="-1"
   fi

   if [ -z "$temp6" ]; then
     temp3="-1"
   fi

    echo "Chip Temp 1: $temp1"
    echo "Chip Temp 2: $temp2"
    echo "Chip Temp 3: $temp3"
    #echo "Chip Temp 4: $temp3"
    #echo "Chip Temp 5: $temp3"
    #echo "Chip Temp 6: $temp6"

   curl -i -XPOST 'http://localhost:8086/write?db=minertemp' -u admin:KalkkiPetteri1803influx --data-binary 'temperature,miner='$j' chip1='$temp1',chip2='$temp2',chip3='$temp3
   curl -i -XPOST 'http://52.212.250.132:8086/write?db=minertemp' -u admin:tamaeivittuolemikaanmysli --data-binary 'temperature,miner='$j' chip1='$temp1',chip2='$temp2',chip3='$temp3
   let j=j+1
done
