## reset_mc.abt, start_mc.bat

from myutil import *
prepare_addresses()
addrs = load_addresses()
print_json(addrs)

#--------------------------------------------------

''' MultiChain Permissions:
 - Low Risk:
     'connect' to other nodes.
     'send' and 'receive' transactions.
 - Medium Risk:
     'issue' assets
     'create' streams
     'activate' manage other address’s low risk permissions.
 - High Risk:
     'admin' modify other addresses permissions.
     'mine' participate in mining race.

Default permission for newly created users is defined in 'params.dat'.
Check: anyone-can-* in the 'params.dat':
     multichain-cli chain1 getblockchainparams
mc getblockchainparams
'''
def anyone_can():
    for (k, v) in api.getblockchainparams().items():
        if k.startswith('anyone-can'):
            print('%s:\t %s' % (k, v))
anyone_can()

''' Initially there is no other addresses excepts 'root'.
Root address has all permissions.
Other addresses created later do not have any permissions.
The first address in other nodes are 'admin', which
  should be granted 'admin' permission by the 'root' 
  to manage other addresses in the node.

List permissions: returns addresses that have any permissions.
        multichain-cli chain1 listpermissions
Try: mc listpermissions
'''
def list_permissions():  ## Print the addresses and their permissions.
    for j in api.listpermissions():
        print(j['address'] , j['type'])
list_permissions()

''' List Permissions with <perm> <addr>: returns addresses that
  have the permissions.
     multichain-cli chain1 listpermissions <perm>
     multichain-cli chain1 listpermissions <perm> <addr>
<perm> and <addr> may be lists, separated by ','.
Try:
      mc listpermissions send
      mc listpermissions send %addr1%
      mc listpermissions "send,receive"
      mc listpermissions "receive,send" "%addr0%,%addr1%"
'''
def list_perm(perm, addr=None):
    for j in api.listpermissions(perm, addr):
        print(j['address'], j['type'])
list_perm('send')
list_perm('connect', addrs[0])
list_perm('send', addrs[1])
list_perm('send,receive')
list_perm('send,connect', addrs[0] + ',' + addrs[1])

#----------------------------------------------------------------

''' Grant permissions to addresses:
      multichain-cli chain1 grant <addr> <perm>
<addr> and <perm> may be lists, separated by ','.
Permissions are properties of individual address.
The granter must have the right to grant.
    e.g. 'root', 'admin' or 'activate'.
Ex:
      mc grant %addr1% connect
      mc grant "%addr2%,%addr3%" "receive,send"
Return the 'txid' that creates the permissions.
Try:
      mc gettransaction %txid%
'''
def grant(addr, perm):
    print(api.grant(addr, perm))
grant(addrs[1], 'send')
list_perm('send', addrs[1])

## Multiple grants:
grant(addrs[2] + ',' + addrs[3], 'receive,send')
list_perm('receive,send', addrs[2] + ',' + addrs[3])

''' Grant permissions from address to another address:
  multichain-cli chain1 grantfrom <from_addr> <to_addr> <perm>
<to_addr> and <perm> may be lists, separated by ','.
<from_add> must have the right to grant permission.
Try:
      mc grantfrom %addr0% %addr1% admin
      mc grantfrom %addr1% %addr2% activate
      mc grantfrom %addr2% %addr3% connect
'''

''' Revoke permissions:
  multichain-cli chain1 revoke <addr> <perm>
  multichain-cli chain1 revokefrom <from_add> <to_add> <perm>
<perm> and <perm> may be lists, separated by ','.
Return the 'txid' that revokse the permissions.
Try:
     mc revokefrom %addr0% %addr1% connect
'''
#-------------------------------------------------------------------

''' 'admin' VS 'activate':
The 'admin' address may grant 'activate' permission to other
 nodes for managing their own address permissions.
An address with 'activate' permission may manage its own
 and other address’s low risk permissions.
Suppose 'addr1' does not have 'activate' permission.
Try:
      mc grantfrom %addr1% %addr2% send      # fail
      mc grantfrom %addr0% %addr1% activate
Then try granting 'send' permission from 'addr1' again.
'''
list_perm('activate', addrs[1])

''' An address with 'activate' permission may modify low risk
 permissions, but not medium nor high risk permissions.
Try:
      mc grantfrom %addr2% %addr3% issue     # fail
      mc grantfrom %addr0% %addr3% issue

The 'admin' and 'activate' permissions are not forever,
  they will last to the 'endblock' only.
'''
