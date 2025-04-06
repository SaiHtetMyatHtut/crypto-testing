## reset_mc.bat

## pip install requests
import requests

from myutil import *
def json_rpc(method):
	url = 'http://' + rpchost + ':' + rpcport
	data = '{"method": "%s",  \
                 "params": [],    \
		 "id": 1, 	  \
		 "chain_name": "chain1"}' % method 
	# print(data)
	headers = { 'Content-type': 'application/json', 'Accept': 'text/plain'}
	res = requests.post(url, data=data, headers=headers,
			auth=(rpcuser,rpcpasswd)).json()  ## dict
	print_json(res)
json_rpc("getinfo")

#---------------------------------------------------------------

print_json(api.getinfo())

