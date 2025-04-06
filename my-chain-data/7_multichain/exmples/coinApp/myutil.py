## python -m pip install savoir

from Savoir import Savoir

rpcuser = 'multichainrpc'
rpcpasswd = '52TH6uU5onYPrwGoZzMittjoEjg9iZS6rDi8i3aVQjNi'
rpchost = '127.0.0.1'
rpcport = '1234'
chainname = 'chain1'
api = Savoir(rpcuser, rpcpasswd, rpchost, rpcport, chainname)

def root_addr():
   return api.getaddresses()[0]

def is_valid_addr(addr):
   return api.validateaddress(addr)['isvalid']

def is_valid_asset(asset):
   try:
      return api.getassetinfo(asset, False)['name'] == asset
   except:
      return False

def is_valid_amount(amount):
   if (not amount.isdecimal()) or float(amount) <= 0:
      return False
   return True
