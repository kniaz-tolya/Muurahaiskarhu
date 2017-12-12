from gpiozero import CPUTemperature
from time import sleep, strftime, time

with open("cpu_temp.csv", "a") as log:
    while True:
        temp = cpu.temperature
        log.write("{0},{1}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(temp)))
        sleep(1)


