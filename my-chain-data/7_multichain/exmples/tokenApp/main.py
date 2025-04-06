## pip install flask
## start_mc.bat
from flask import Flask, render_template, request
app = Flask(__name__)

#############################################

@app.route('/')
def index():
    return render_template('index.html')

from myutil import *

@app.route('/prepare')
def prepare():
   r = api.create('stream', 'encaddr', True)
   try:
      if r['error']:
         return 'The Blockchain has already been prepared'
   except:

      pass
   addr = admin_addr()
   pwd = gen_pwd()
   enc = encode(addr, pwd)
   api.publish('encaddr', addr, str_hex(enc))
   api.subscribe('encaddr')
   return "{'address': %s, 'pwd': %s}" % (addr, pwd)

@app.route('/listaddr')
def list_addr():
   s = ''
   for r in api.getaddresses()[1:]:
      s += r + '<br/>'
   return s if s != '' else 'None'

@app.route('/liststream')
def list_streams():
    s = ''
    for r in api.liststreams():
        s += r['name'] + '<br/>'
    return s if s != '' else 'None'

@app.route('/listperm')
def list_perm():
   root_addr = api.getaddresses()[0]
   s = ''
   for r in api.listpermissions():
      if r['address'] != root_addr:
         s += (r['address'] + ' ' + r['type']) + '<br/>'
   return s if s != '' else 'None'

################################################

@app.route('/regacc')
def reg_acc():
   addr = api.getnewaddress()
   pwd = gen_pwd()
   enc = encode(addr, pwd)
   api.publish('encaddr', addr, str_hex(enc))
   api.grant(addr, 'send,receive')
   return "{'address': %s, 'pwd': %s}" % (addr, pwd)

@app.route('/verifyaddrpwd', methods=['POST'])
def verify_addr_pwd():
   if is_valid_addr_pwd(request.form['addr'], request.form['pwd']):
      return 'Valid'
   return 'Invalid address or password'

@app.route('/issue', methods=['POST'])
def issue():
   adminaddr = admin_addr()
   if not is_valid_addr_pwd(adminaddr, request.form['pwd']):
      return 'Invalid admin address or password'

   addr = request.form['addr']
   if not is_valid_addr(addr):
      return 'Invalid receiver address'
   if adminaddr == addr:
      return 'The admin cannot own any asset'

   asset = request.form['asset']
   if is_valid_asset(asset):
      return 'The asset already exist'

   amount = request.form['amount']
   if not is_valid_amount(amount):
      return 'Invalid amount'

   r = api.issue(addr, asset, float(amount), 1.0)
   try:
      if r['error']:
         return str(r['error']['message'])
   except:
      pass
   return 'Success'

#################################################

@app.route('/sendfrom', methods=['POST'])
def send_from():
   pwd = request.form['pwd']
   add1 = request.form['add1']
   if not is_valid_addr_pwd(add1, pwd):
      return 'Invalid sender address or password'

   add2 = request.form['add2']
   if not is_valid_addr(add2):
      return 'Invalid receiver address'
   if add2 == admin_addr():
      return 'Admin cannot own asset'

   asset = request.form['asset']
   if not is_valid_asset(asset):
      return 'Invalid asset'

   amount = request.form['amount']
   if not is_valid_amount(amount):
      return 'Invalid amount'

   r = api.sendassetfrom(add1, add2, asset, float(amount))
   try:
      if r['error']:
         return str(r['error']['message'])
   except:
      pass
   return 'Success'

#################################################

@app.route('/addrbal', methods=['POST'])
def addr_bal():
   addr = request.form['addr']
   if not is_valid_addr_pwd(addr, request.form['pwd']):
      return 'Invalid address'
   s = ''
   for b in api.getaddressbalances(addr):
      s += b['name'] + '  ' + str(b['qty']) + '<br/>'
   return s if s != '' else 'None'

#################################################

if __name__ == '__main__':
    app.run(port=8080, debug=True)


