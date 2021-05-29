#!/usr/bin/env python3

from influxdb import InfluxDBClient
import urllib.request
from datetime import datetime, timezone
import subprocess
from threading import Thread
import time
import ast
import requests
import json
import re

start_time = time.time()

client = InfluxDBClient(host='192.168.2.6', port=8086, database='internxt')
client.create_database('internxt')


def convert_time(time):
	#print(time)
	time = time[:len(time) -1]
	
	
	utc_dt = datetime.fromisoformat(time)
	#print(utc_dt)
	return datetime.now().timestamp()-utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None).timestamp()


def convert_size(humansize):
	size = int([len(humansize) -2])

	if humansize.endswith("TB"):
		size=size*1024*1024*1024*1024
	if humansize.endswith("GB"):
		size=size*1024*1024*1024
	if humansize.endswith("GB"):
		size=size*1024*1024
	if humansize.endswith("GB"):
		size=size*1024
	return size


def decimal_str(x: float, decimals: int = 10) -> str:
	ret = format(x, f".{decimals}f").lstrip().rstrip('0')
	if ret == "0.":
		ret = "0.0"
	return ret

def api(nodeid):
	url_str = 'https://api.internxt.com/contacts/' + nodeid
	try:
		url = urllib.request.urlopen(url_str)
		data = json.loads(url.read().decode())
		return data
	except:
		#print("first method failed")
		try:
			response = requests.get(url_str)
			data = json.loads(response.content)
			#print(data)
			return data
		except:
			print(response.content)

def get_data(nodename, nodeid, num):
	#print(num)
	data = api(nodeid)


	#try:
	#	status_result = subprocess.run(f"/mnt/user/transcode/bin/xcore %s %s" % ("json", str(num)), shell=True, stdout=subprocess.PIPE)
	#	status_json = status_result.stdout

	#	status = json.loads(status_json)
	#	status=status[0]
	#except:
	#	print(f"Ran into a problem with {nodename}'s status', chief")



	lastSeen=0
	lastSeen = convert_time(data['lastSeen'])
	lastTimeout = 0.0
	uptime=0.0
	try:

			uptime_result = subprocess.run(f"/mnt/user/transcode/bin/xcore %s %s" % ("uptime", str(num)), shell=True, stdout=subprocess.PIPE)
			
			uptime = uptime_result.stdout

			uptime = str(uptime)

			uptime = uptime[2:len(uptime) -3]
			uptime = uptime[:23]+"Z"
			uptime = convert_time(uptime)
	except:
			print(uptime_result)
			uptime=0.0
			print(f"Ran into a problem with {nodename}'s uptime', chief")

	timeout = 0.0
	try:
			timeout = float(data['timeoutRate'])
			a=1
	except:
			timeout = 0.0

	try:
			lastTimeout = convert_time(data['lastTimeout'])
	except:
			lastTimeout = 0.0
			#print(f"Ran into a problem with {nodename}'s last timeout', chief")

	json_body = [
		{
			"measurement": "reputation",
			"tags": {
				"host": nodename
			},
			"fields": {
				"reputation": data['reputation'],
				"Last Seen": lastSeen,
				"Timeout Rate": timeout,
				"Last Timeout": lastTimeout,
				"Uptime": uptime,
				#"dataReceivedCount": status['dataReceivedCount'],
				#"allocs": status['allocs'],
				#"Size" : convert_size(status['size']),
			}
		}
	]
	client.write_points(json_body, database='internxt', time_precision='ms', batch_size=10000, protocol='json')
	#print(f"{num} done")


threads = []
nodes = []
with open('/mnt/user/transcode/internxt-api-keys.txt', 'r') as reader:
	for line in reader:
		if not line.startswith("#"):
			nodes.append(re.split(r'\t+', line.strip("\n")))

for e in nodes:
	name = f"internxt{e[0].zfill(2)}"
	x = Thread(target=get_data, args=(name, e[2], e[0]))
	threads.append(x)



#for x in threads:
	x.start()

#for x in threads:
	x.join()

print("--- %s seconds ---" % round(time.time() - start_time,3))