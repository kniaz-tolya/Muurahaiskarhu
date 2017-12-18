#!/bin/bash
cpuTemp0=$(cat /sys/class/thermal/thermal_zone0/temp)
cpuTemp1=$(($cpuTemp0/1000))
cpuTemp2=$(($cpuTemp0/100))
cpuTempM=$(($cpuTemp2 % $cpuTemp1))
CPU=$cpuTemp1"."$cpuTempM
GPU=$(/opt/vc/bin/vcgencmd measure_temp | tr -cd '0-9.')
echo "CPU: " $CPU
echo "GPU: " $GPU
curl -i -XPOST 'http://localhost:8086/write?db=rpicputemp' -u admin:KalkkiPetteri1803influx --data-binary 'temperature CPU='$CPU',GPU='$GPU
