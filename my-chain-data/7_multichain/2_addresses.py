## reset_mc.bat, start_mc.bat

from myutil import *

''' There are three kinds of addresss:
        - In wallet addresses(iwa): created and managed in wallets.
        - Off wallet addresses(owa): created outside wallets.
        - Imported addresses(ia): created outside and imported into a wallet.

Get Addresses:
Returns iwa and ia in the node(wallet).
    multichain-cli chain1 getaddresses
mc getaddresses
Returns a list of str.
Initially there is only the 'root' address.
The 'root' address is always the first address.
'''
print_json(api.getaddresses())

''' List Addresses: Returns more information of addresses.
     multichain-cli chain1 listaddresses
mc listaddresses
Returns a list of dict.
'ismine' if 'true' the address is an iwa.
'''
print_json(api.listaddresses())

''' Create an iwa: 
     multichain-cli chain1 getnewaddress
mc getnewaddress
Return a str.
The private key is stored in the node.
'''
print_json(api.getnewaddress())

## Create sample addresses (from myutil).
# prepare_addrs()

''' Verify Address: 
        multichain-cli chain1 validateaddress <address>
set addr=<address>
mc validateaddress %addr%
Return a dict. The result is 'isvalid'.
The public key is shown but not the private key.
'''
def verify_addr(addr):
    return api.validateaddress(addr)['isvalid']
root_addr = api.getaddresses()[0]
print(verify_addr(root_addr)) 

''' Create owa: 
      multichain-cli chain1 createkeypairs <count>=1
<count> is the number of accounts to be generated.
mc createkeypairs
mc createkeypairs 2
An account contains private key, public key and address.
'''
def owa_test():
    keys = api.createkeypairs()   ## list of keys
    pri = keys[0]['privkey']
    pub = keys[0]['pubkey']
    addr = keys[0]['address']
    print(len(pri), pri)    ## (56 char) wif private key
    print(len(pub), pub)    ## (66 char) compressed hex public key
    print(len(addr), addr)  ## (38 char) wif compressed address
owa_test()

## Owas are not stored in the node.  Check:  mc getaddresses 
print_json(api.listaddresses())

''' Import Address:
     multichain-cli chain1 importaddress <addr> <scan>
If the <addr> is an owa.
It is imported in to the node, 'ismine' is 'false'.
<scan> is a boolean to specify tracking the transactions of the <addr>. '''
def import_addr():
    ## Created owa.
    addr = api.createkeypairs()[0]['address']
    print(addr)

    ## Show addresses in the node.
    [print(a) for a in api.listaddresses()]  ## The 'addr' is not shown.

    ## Import the owa.
    try:
        r = api.importaddress(addr, 'True')   ## 'True' is a str.
        if r == None:                         ## Success return None.
            print('Success')
        else:
            print(r['error']['message'])
    except:
        print('Import fails.')
        return

    [print(a) for a in api.listaddresses()]  ## 'addr' is shown but 'ismine': False.
import_addr()
