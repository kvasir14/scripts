#!/usr/bin/env python3

from influxdb import InfluxDBClient
import subprocess

client = InfluxDBClient(host='192.168.2.6', port=8086, database='hddtemp')
client.create_database('hddtemp')

file = open("/var/local/emhttp/disks.ini", "r")

sum = 0
count = 0
max=0

device = ""
temp = ""

json_body = []
for line in file:
	line = line.replace("\n", "")
	if line.startswith("device="):
		#print(line)
		device = line.replace("device=\"","").replace("\"","")
		is_hdd = False
	if line.startswith("temp="):
		#print(line)
		temp = line.replace("temp=\"","").replace("\"","")
		if temp == "*":
			temp = 0
	if temp == 0:
		continue
	if line.startswith("rotational=\"1"):
			is_hdd = True
	if device != "" and temp != "" and line.startswith("color="):
		temp = int(temp)

		if is_hdd:
			sum += temp
			count += 1
			if temp > max:
				max = temp
			#print(f"{device}:{temp}")

		json_body.append( 
				{
					"measurement": "hddtemp",
					"tags": {
						"device": device,
						"host": "Tower",
						"is_hdd": is_hdd
					},
					"fields": {
						"temperature" : temp
					}
				}
			)
#print(json_body)

avg = round(sum/count, None)

print(f"avg: {avg}")
print(f"max: {max}")
client.write_points(json_body, database='hddtemp', time_precision='ms', batch_size=10000, protocol='json')


exit()


temp_values = 		[0 , 32, 33, 34, 35, 36, 37, 38, 39]
fan_speed_values = 	[25, 30, 35, 40, 45, 50, 55, 60, 65]
if(len(temp_values) !=len(fan_speed_values)):
	print("fan curve arrays different lengths")
	exit()

temp = max

for i in  range(len(temp_values)-1):
	if temp_values[i] <= temp and temp < temp_values[i+1]:
		speed= fan_speed_values[i]
		output = subprocess.run(f"/mnt/user/transcode/bin/dasfans %s" % (str(speed)), shell=True, stdout=subprocess.PIPE)
		output = str(output.stdout)
		output = output[2:len(output) -3]

		print(output)