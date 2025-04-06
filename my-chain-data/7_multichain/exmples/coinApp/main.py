## pip install flask
## start_mc.bat
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

############################################

from myutil import *

## List addresses, exclude root address.
@app.route('/listaddr')
def list_addr():
   s = ''
   for r in api.getaddresses()[1:]: ## Exclude root address.
      s += r + '<br/>'
   return s if s != '' else 'None'

## Create new address and grant permissions.
@app.route('/newacc')
def new_acc():
   addr = api.getnewaddress()
   api.grant(addr, 'send,receive')
   return addr

## Verify if an address is valid.
@app.route('/verifyaddr', methods=['POST'])
def verify_addr():
   if not is_valid_addr(request.form['addr']):
       return 'Invalid.'
   return 'Valid.'

################################################

## List permissions, exclude root address.
@app.route('/listperm')
def list_perm():
   root_addr = api.getaddresses()[0]
   s = ''
   for r in api.listpermissions():
      if r['address'] != root_addr:
          s += (r['address'] + ' ' + r['type']) + '<br/>'
   return s

#################################################

## Issue asset to an address.
@app.route('/issue', methods=['POST'])
def issue():
    # The address must be valid.
    addr = request.form['addr']
    if not is_valid_addr(addr):
        return 'Invalid receiver address.'

    ## Cannot issue asset to root address.
    if root_addr() == addr:
        return 'Root cannot own asset.'

    ## The asset must not already exist.
    asset = request.form['asset']
    if is_valid_asset(asset):
        return 'The asset already exist.'

    ## The amount must be valid.
    amount = request.form['amount']
    if not is_valid_amount(amount):
        return 'Invalid amount.'

    ## The asset subdivide is always 1.0.
    r = api.issue(addr, asset, float(amount), 1.0)
    try:
        if r['error']:
            return str(r['error']['message'])
    except:
        pass
    return 'Success.'

## Send from 'add1' to 'add2' an asset with amount.
@app.route('/sendfrom', methods=['POST'])
def send_from():
    ## 'add1' and 'addr2' must be valid.
    add1 = request.form['add1']
    if not is_valid_addr(add1):
        return 'Invalid sender address.'
    add2 = request.form['add2']
    if not is_valid_addr(add2):
        return 'Invalid receiver address.'

    ## 'root' cannot receive assets.
    if add2 == root_addr():
        return 'Root cannot receive assets.'

    ## The asset must valid.
    asset = request.form['asset']
    if not is_valid_asset(asset):
        return 'Invalid asset.'

    ## The amount must valid.
    amount = request.form['amount']
    if not is_valid_amount(amount):
        return 'Invalid amount.'

    r = api.sendassetfrom(add1, add2, asset, float(amount))
    try:
        if r['error']:
            return str(r['error']['message'])
    except:
        pass
    return 'Success.'

#################################################

## Check address balance.
@app.route('/addrbal', methods=['POST'])
def addr_bal():
    ## The address must be valid.
    addr = request.form['addr']
    if not is_valid_addr(addr):
        return 'Invalid address.'

    ## An address may own more than one assets.
    s = ''
    for b in api.getaddressbalances(addr):
        s += b['name'] + '  ' + str(b['qty']) + '<br/>'
    return s

#################################################

if __name__ == '__main__':
    app.run(port=8080, debug=True)
