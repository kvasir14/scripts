#!/usr/bin/env python3

from influxdb import InfluxDBClient
import subprocess

client = InfluxDBClient(host='192.168.2.6', port=8086, database='telegraf')
client.create_database('telegraf')

output = subprocess.run(f"ipmitool -H 192.168.2.205 -U ADMIN -P QIPXBUTDBO sensor | grep RPM | cut -d '|' -f2", shell=True, stdout=subprocess.PIPE)
output = str(output.stdout)
output = output[2:len(output) -3].replace("\\n", "\n").splitlines()
json_body = []

#print(output)
count = 0
for line in output:
	rpm = float(line.strip())


	json_body.append( 
		{
			"measurement": "ipmi_sensor",
			"tags": {
				"name": f"fan1{count}",
				"host": "DAS",
				"unit" : "rpm"
			},
			"fields": {
				"value" : rpm
			}
		}
	)
	count+=1
print(json_body)


client.write_points(json_body, database='telegraf', time_precision='ms', batch_size=10000, protocol='json')