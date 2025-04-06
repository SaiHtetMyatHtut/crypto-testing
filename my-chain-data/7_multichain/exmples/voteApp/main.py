## start_mc.bat
## run.bat

from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

from myutil import *
import csv

@app.route('/prepare', methods=['POST'])
def perpare():
## Verify admin password
   adminpwd = request.form['pwd']
   if not is_valid_pwd(adminpwd):
      return 'Invalid password'

## Create stream 'names' and subscribe.
   r = api.create('stream', 'names', True)
   try:
      if r['error']['code'] == -705:
         return 'The Blockchain is already initialized'
   except:
      api.subscribe('names')

## Read voter list and publish to 'names'
   try:
      with open('data/voters_list.csv') as f:
         for r in csv.DictReader(f):
            api.publish('names', 'voter', str_hex(r['name']))
   except:
      return 'Error reading voters list.... please reset the Blockchain'

## Issue asset 'score' to admin with amount equal to number of voters.
   adminaddr = api.getaddresses()[0]
   api.issue(adminaddr, 'score', count('voter'), 1.0)

## create stream 'nameaddr' and publish admin address to 'nameaddr'
   api.create('stream', 'nameaddr', True)
   api.publish('nameaddr', 'admin', str_hex(encode(adminaddr, adminpwd)))
   api.subscribe('nameaddr')

## read candidate list and publish to 'names' and 'nameaddr'.
   try:
       with open('data/candidates_list.csv') as f:
           for r in csv.DictReader(f):
               ## 'candidate' is the key for all candidate names.
               api.publish('names', 'candidate', str_hex(r['name']))

               ## Create an address for each candidate and grant permissions.
               canaddr = api.getnewaddress()
               api.publish('nameaddr', r['name'], str_hex(canaddr))
               api.grant(canaddr, 'receive') ## Assume candidates cannot vote.
   except:
      return 'Error reading candidates list.... please reset the Blockchain'
   return 'There are %d voters and %d candidates.' % (count('voter'), count('candidate'))

#############################################################################

@app.route('/listvoters')
def list_voters():
    return str(get_list('voter'))

@app.route('/verifyvoter', methods=['POST'])
def verify_voter():
    return str(is_valid('voter', request.form['name']))

@app.route('/listcandidates')
def list_candidates():
    return str(get_list('candidate'))

@app.route('/verifycandidate', methods=['POST'])
def verify_candidate():
    return str(is_valid('candidate', request.form['name']))

@app.route('/liststreams')
def list_streams():
    ss = ''
    for s in api.liststreams():
        ss += s['name'] + '<br/>'
    return ss

#####################################################

@app.route('/registervoter', methods=['POST'])
def register_voter():
    ## The name must be valid voter.
    name = request.form['name']
    if not is_valid('voter', name):
        return 'Invalid voter'

    ## A name must register only once.
    if is_valid('registered', name):
        return 'The voter is already registered'

    ## 'registered' is the key for all registered names.
    api.publish('names', 'registered', str_hex(name))

    ## Create address for registered name and grant permissions.
    addr = api.getnewaddress()
    api.grant(addr, 'send,receive')

    ## Send a 'score' vote from 'root' to registered name address.
    api.sendassetfrom(get_root_addr(), addr, 'score', 1)

    ## Create a password for the registered name.
    pwd = gen_pwd()
    ## 'nameaddr' stream stores 'name' key with encrypted 'addr' and'pwd' as value.
    ## 'pwd' is the key for encoding 'addr'
    api.publish('nameaddr', name, str_hex(encode(addr, pwd)))
    return '{"name": %s, "pwd": %s}' % (name, pwd)

@app.route('/listregisters')
def list_registers():
   return str(get_list('registered'))

@app.route('/verifyregister', methods=['POST'])
def verify_register():
    ## 'pwd' must be valid.
    pwd = request.form['pwd']
    if not is_valid_pwd(pwd):
        return 'Invalid password'

    ## 'name' must be valid voter.
    name = request.form['name']
    if not is_valid('voter', name):
        return 'Invalid voter'

    ## 'name' must be registered voter.
    r = api.liststreamkeyitems('nameaddr', name)
    if len(r) == 0:
        return 'The voter is not registered'

    ## Using 'pwd' as key for decoding the voter address.
    addr = decode(hex_str(r[0]['data']), pwd)
    ## Verify that the address is valid.
    if not api.validateaddress(addr)['isvalid']:
        return 'The password is not belong to the voter'
    return 'True'

#####################################################

@app.route('/votes', methods=['POST'])
def votes():
    pwd = request.form['pwd']
    if not is_valid_pwd(pwd):
        return 'Invalid password'

    ## The name must be valid voter.
    name = request.form['name']
    if not is_valid('voter', name):
        return 'Invalid voter'

    ## The number of voted must not excess the number of registered.
    if count('voted') >= count('registered'):
        return 'All registered voters had been voted'

    ## A voter must not vote more than once.
    if is_valid('voted', name):
        return 'The voter had alreadt voted'

    ## A voter must register.
    r = api.liststreamkeyitems('nameaddr', name)
    if len(r) <= 0:
        return 'The voter is not registered'

    ## 'pwd' must belonged to the name.
    addr = decode(hex_str(r[0]['data']), pwd)
    if not api.validateaddress(addr)['isvalid']:
        return 'The password is not belong to the voter'

    ## The voted candidate must be valid.
    cand = request.form['cand']
    r = api.liststreamkeyitems('nameaddr', cand)
    if len(r) <= 0:
        return 'Invalid candidate'

    ## Retrieve the candidate address and send 'vote' score to the address.
    canaddr = hex_str(r[0]['data'])
    r = api.sendassetfrom(addr, canaddr, 'score', 1)
    try:
        if r['error']:
            return 'Error vote: ' + str(r['error']['message'])
    except:
        pass
    api.publish('names', 'voted', str_hex(name))
    return 'Success'

@app.route('/listvoted')
def list_voted():
   return str(get_list('voted'))


@app.route('/verifyvoted', methods=['POST'])
def verify_voted():
   pwd = request.form['pwd']
   if not is_valid_pwd(pwd):
      return 'Invalid password'

   name = request.form['name']
   if not is_valid('voter', name):
      return 'Invalid voter'

   r = api.liststreamkeyitems('nameaddr', name)
   if len(r) == 0:
      return 'The voter is not registered'

   addr = decode(hex_str(r[0]['data']), pwd)
   if not api.validateaddress(addr)['isvalid']:
      return 'The password is not belong to the voter'
   return str(is_valid('voted', name))

######################################################

@app.route('/status')
def status():
   v = count('voter')
   r = count('registered')
   ve = count('voted')
   return 'voters: %d <br/> registered: %d <br/> voted: %d <br/>' % (v, r, ve)

@app.route('/score')
def score():
   x = []
   for c in get_list('candidate'):
      a = get_can_addr(c)
      re = api.getaddressbalances(a)
      if len(re) <= 0:
         x.append((c, 0))
      else:
         x.append((c, re[0]['qty']))
   return str(sorted(x, key=getKey, reverse=True))

####################################################################


@app.route('/getaddr', methods=['POST'])
def get_addr():
   pwd = request.form['pwd']
   if not is_valid_pwd(pwd):
      return 'Invalid password'

   name = request.form['name']
   r = api.liststreamkeyitems('nameaddr', name)
   if len(r) <= 0:
      return 'Invalid name'
   return decode(hex_str(r[0]['data']), pwd)


###############################################################

if __name__ == '__main__':
    app.run(port=8080, debug=True)
