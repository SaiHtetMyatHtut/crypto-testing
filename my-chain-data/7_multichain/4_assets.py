## reset_mc.bat, start_mc.bat

from myutil import *
def set_addresses():
    prepare_addresses()
    addrs = load_addresses()
    print_json(addrs)
set_addresses()
addrs = load_addresses()
## set_addrs.bat

''' Get Address Balance:
      multichain-cli chain1 getaddressbalances <addr>

Initially all addresses, including 'root' have no balances.
mc getaddressbalances %addr0%
'''
def get_balance(addr):
    bs = api.getaddressbalances(addr)
    if bs == []:
        print(addr, 'None')
    else:
        for b in bs:
            print(addr, b['name'], b['qty'])
get_balance(addrs[1])

def prepare_permissions():
    ## Get all addresses except 'root', and grant 'receive,send' permissions.
    a = ','.join(addrs[1:]) ## a str of addresses separated by ','.
    api.grant(a, 'receive,send')	
prepare_permissions()

## List addresses that have permissions.
def list_permissions(perms):
    ## 'perms' is a str of permissions separated by ','.
    for j in api.listpermissions(perms, addrs):
        print(j['address'], j['type'])	
list_permissions('receive,send')

#---------------------------------------------------------

''' Assets:
List Assets:
      multichain-cli chain1 listassets
mc listassets
Initially there is no assets.
'''
def list_assets():
    assets = api.listassets()
    if assets == []:
        print('No assets.') 
    else:
        for a in assets:
            print(a['name'] , a['issueqty'])
list_assets()         

''' Issue: Asset to address
     multichain-cli chain1 issue <addr> <asset> <amount> <subdivide>

The issuer must be the 'root' or has 'admin' permission.
<addr> is address of the receiver that has 'receive' permission.
Return the 'txid' that issues the asset if success.
The asset is 'closed' by default , the asset cannot be issued more than once.
An address may own more than one assets.
'root' may have no balances but can issue assets to any addresses.
Normally we start with 'root' issuses an asset to itself.

Ex. 'addr0'(root) issues 100 'as0' asset to itself with subdivide 0.01.
mc issue %addr0% as0 100 0.01
mc getaddressbalances %addr0%
'''
def issue(recv, asset, amount, subd=1): ## 'root' is the issuer by default.
    print(api.issue(recv, asset, amount, subd))
issue(addrs[0], 'as1', 1000, 0.01)
list_assets()

''' Get Asset Info of an asset:
      multichain-cli chain1 getassetinfo <asset> <versbose>=false

'versbose' provides more information.
'name' and 'issueqty' are the name and amount of the asset.

mc getassetinfo as0
mc getassetinfo as1 true

----------------------------------------------------

'open' asset: can be reissued.
The asset is described as json, with 'open' is true.
  multichain-cli chain1 issue <recv> "{\"name\":<asset_name>, \"open\": true }" <amount> <subdivide>
  multichain-cli chain1 issueform <form_addr> <to_addr> "{\"name\":<asset_name>, \"open\": true }" <amount> <subdivide>
Ex. Issue 'ax' asset to addr1 as an opened asset:
mc issue %addr1% "{\"name\":\"ax\", \"open\":true}" 100 1
mc getassetinfo ax
mc getaddressbalances %addr1%

Issuing More:
     multichain-cli chain1 issuemore <recv> <asset> <amount>
     multichain-cli chain1 issuemoreform <form_addr> <to_addr> <asset> <amount>
mc issuemore %addr1% ax 200
mc getaddressbalances %addr1%
'''
#-------------------------------------------------------

''' Send Asset:
     multichain-cli chain1 sendasset <receiver_addr> <asset> <amount>

The sender is the 'root' or 'admin' and must have enough asset.
<addr> is address of the receiver and must has 'receive' permission.
Return 'txid' that send the asset if success.
Multichain handles the balances for both sender and receiver.
The wallet take cares of creating and signing tx.

mc getaddressbalances %addr0%
mc getaddressbalances %addr1%
mc sendasset %addr1% as0 10
mc getaddressbalances %addr0%
mc getaddressbalances %addr1%
'''
def send_asset(recv, asset, amount):
    print(api.sendasset(recv, asset, amount))
send_asset(addrs[1], 'as1', 10)

''' To send asset from non-root:
Senders must has 'send' permission. Receiver must has 'receive' permission.
   multichain-cli chain1 sendassetfrom <from_addr> <to_addr> <asset> <amount>

mc getaddressbalances %addr1%
mc getaddressbalances %addr2%
mc sendassetfrom %addr1% %addr2% as0 5
mc getaddressbalances %addr1%
mc getaddressbalances %addr2%
'''
def send_asset_form(from_addr, to_addr, asset, amount):
    print(api.sendassetfrom(from_addr, to_addr, asset, amount))
send_asset_form(addrs[1], addrs[2], 'as0', 5)

''' Sending multiple assets in a tx. The asset is represnted as json:
        {<asset1>:<amount1>, <asset2>:<amount2>, ...}
    multichain-cli chain1 send <receiver_addr> <json>
    multichain-cli chain1 sendfrom <from_addr> <to_addr> <json>
mc sendfrom %addr1% %addr2% "{\"as1\":1, \"as2\":2}"
'''
#----------------------------------------------------

## converting: string <--> hex string  (from myutil.py)
print(str_hex('Hello'))         ## 48656c6c6f
print(hex_str('48656c6c6f'))    ## Hello

#----------------------------------------------------

''' Sending Asset with hex-string Metadata:
Asset must be represented as json.
If <metadata> is just a text it must be a hex-string:
  multichain-cli chain1 sendwithdata <to_addr> <json_asset> <metadata>
  multichain-cli chain1 sendwithdatafrom <from_addr> <to_addr> <json_asset> <metadata>
mc sendwithdata %addr2% "{\"as0\":1}" 48656c6c6f
mc sendwithdatafrom %addr1% %addr2% "{\"as0\":1}" 48656c6c6f
'''
def send_with_datafrom(sender, recv, jsasset, mdata):
    print(api.sendwithdatafrom(sender, recv, jsasset, mdata))
send_with_datafrom(addrs[1], addrs[2], {'as1': 1}, str_hex('Hi'))

''' The metadata is stored in the tx of a receiver address.
List the last <n> transactions of an <addr>:
         multichain-cli chain1 listaddresstransactions <addr> <n>
mc listaddresstransactions %addr2% 2
'data' contains the metadata.
'''
def read_data(addr, n):
    for t in api.listaddresstransactions(addr, n):
        d = t['data'][0]
        if type(d) == str:
            print(hex_str(d))
        else:
            print(d)
read_data(addrs[2], 1)

#---------------------------------------------------

''' Sending Asset with Text Metadata:
<metadata> may be a json in the form of:  {"text": "<str>"}
mc sendwithdatafrom %addr0% %addr1% {\"as0\":1} "{\"text\": \"Hello\"}"
'''
send_with_datafrom(addrs[0], addrs[1], {'as1': 1}, {"text": "Hi how are you?"})
read_data(addrs[1], 1)

''' <metadata> may be a json object:  {"json": {"id":"123", "name":"john"}}
mc sendwithdatafrom %addr0% %addr1% "{\"as1\":1}" "{\"json\": {\"id\":\"123\", \"name\":\"john\"}}"
'''
def send_jsonobj():
    send_with_datafrom(addrs[0], addrs[1], {'as1': 1}, 
                                      {"json": [{'id': 500, 'name': 'jack'},
                                      {'id': 600, 'name': 'joe'}] })
send_jsonobj()
read_data(addrs[1], 1)

#-----------------------------------------------------------------
