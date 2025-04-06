## pip install savoir
from Savoir import Savoir
rpcuser = 'multichainrpc'
rpcpasswd = '52TH6uU5onYPrwGoZzMittjoEjg9iZS6rDi8i3aVQjNi'
rpchost = '127.0.0.1'
rpcport = '1234'
chainname = 'chain1'
api = Savoir(rpcuser, rpcpasswd, rpchost, rpcport, chainname)

import json
def print_json(st):
    print(json.dumps(st, indent=4))

def str_hex(s):
    return s.encode().hex()

def hex_str(h):
    return bytes.fromhex(h).decode()

#--------------------------------------

## Create 5 new addresses.
import pickle
def prepare_addresses(num=4):
    addrs = api.getaddresses()  ## The first address is 'root'.
    for _ in range(num):
        addrs.append(api.getnewaddress())

    ## Save to set_addr.bat to use in command line.
    with open('set_addrs.bat', 'w') as f:
        for i, a in enumerate(addrs):
            f.write('set addr{}={}\n'.format(i, a))

    ## Pickle 'addrs' to use in Python.
    with open('addr.bin', 'wb') as f:
        pickle.dump(addrs, f)
    # print('prepare_addresses() success.')

def load_addresses():
    with open('addr.bin', 'rb') as f:
        addrs = pickle.load(f)
    # print('load_addresses() success.')
    return addrs
# print(load_addresses())

## Check:
# setaddrs
# echo %addr0%