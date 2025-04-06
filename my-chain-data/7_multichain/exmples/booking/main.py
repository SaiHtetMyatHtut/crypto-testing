
from flask import Flask, render_template, request
app = Flask(__name__)

#############################################

@app.route('/')
def index():
    return render_template('index.html')

############################################

from myutil import *

@app.route('/prepare', methods=['POST'])
def perpare():

   ## verify admin password
   adminpwd = request.form['pwd']
   if not is_valid_pwd(adminpwd):
      return 'Invalid password'

   ## verify number of seats
   numseat = request.form['numseat']
   if not is_valid_seat(numseat, 100):
      return 'Invalid number of seat'
   num_seat = int(numseat)

   ticket = request.form['ticket']
   admin_addr = get_admin_addr()
   r = api.create('stream', 'ticket', {'restrict': 'write'})
   try:
      if r['error']:
         return r['error']['message']
   except:
      api.subscribe('ticket')

   ## ['seat', <seat_num>] {'json': {'state': <state>}}
   try:
      for s in range(num_seat):
         api.publish('ticket', ['seat', str(s)], {'json': {'state': '00'}})
   except:
      return 'Error creating seat ... please reset the Blockchain'

   ## save num_seat
   r = api.publish('ticket', 'num_seat', str_hex(str(num_seat)))
   try:
      if r['error']:
         return str(r['error']['message'])
   except:
      pass
   return 'Success'

###############################################################

@app.route('/getnumseat')
def get_num_seat_():
   return get_num_seat()

@app.route('/getseatstate', methods=['POST'])
def get_seat_state_():
   seat_num = request.form['seat_num']
   if not is_valid_seat(seat_num, int(get_num_seat())):
      return 'Invalid seat number'
   return state_map[get_seat_state(seat_num)]


@app.route('/listseats')
def list_seats():
   s = []
   for i in range(int(get_num_seat())):
      s.append((i, state_map[get_seat_state(str(i))]))
   return str(s)


#############################################################################

@app.route('/books', methods=['POST'])
def books():
   name = request.form['name']
   if not is_valid_name(name):
      return 'Invalid name'

   num_seat = int(get_num_seat())
   seat_num = request.form['seat_num']
   if not is_valid_seat(seat_num, num_seat):
      return 'Invalid seat number'

   if get_seat_state(seat_num) != '00':
      return 'The seat is not available'

   ## ['seat', <seat_num>] {'json': {'state': <state>, 'name': <name>}}
   r = api.publish('ticket', ['seat', seat_num], {'json': {'state': '11', 'name': name}})
   try:
      if r['error']:
         return 'Error updating seat: ' + str(r['error']['message'])
   except:
      pass

   pwd = gen_pwd()
   ename = encode(name, pwd)
   ## ['name', <name>] {'json': {'ename': <ename, 'seat': <seat_num>}}
   r = api.publish('ticket', ['name', name], {'json': {'ename': ename, 'seat': seat_num}})
   try:
      if r['error']:
         return 'Error saving name: ' + str(r['error']['message'])
   except:
      pass

   return "{'name': %s, 'seat': %s, 'pwd': %s}" % (name, seat_num, pwd)

@app.route('/verifybooks', methods=['POST'])
def verify_books():
   name = request.form['name']
   if not is_valid_name(name):
      return 'Invalid name'

   pwd = request.form['pwd']
   if not is_valid_pwd(pwd):
      return 'Invalid pwd'

   r = api.liststreamkeyitems('ticket', name, False, 1)
   if len(r) == 0:
      return 'The name is not in the booked list'
   namex = decode(r[0]['data']['json']['ename'], pwd)
   if namex != name:
      return 'The password is not belong to the name'
   seat = r[0]['data']['json']['seat']
   return str({'seat': seat})

@app.route('/getseatowner', methods=['POST'])
def get_seat_owner():
   num_seat = int(get_num_seat())
   seat_num = request.form['seat_num']
   if not is_valid_seat(seat_num, num_seat):
      return 'Invalid seat number'

   r = api.liststreamkeyitems('ticket', seat_num, False, 1)[0]
   try:
      if r['data']['json']['state'] == '00':
         return 'None'
      return str(r['data']['json']['name'])
   except:
      return 'Error'

###############################################################

@app.route('/seats', methods=['POST'])
def seat():
   name = request.form['name']
   if not is_valid_name(name):
      return 'Invalid name'

   pwd = request.form['pwd']
   if not is_valid_pwd(pwd):
      return 'Invalid pwd'

   num_seat = int(get_num_seat())
   seat_num = request.form['seat_num']
   if not is_valid_seat(seat_num, num_seat):
      return 'Invalid seat number'

   state = get_seat_state(seat_num)
   if state == '00':
      return 'The seat is not booked.'
   if state == '22':
      return 'The seat is already seated.'

   r = api.liststreamkeyitems('ticket', name, False, 1)
   if len(r) == 0:
      return 'The name is not in the booked list'
   namex = decode(r[0]['data']['json']['ename'], pwd)
   if namex != name:
      return 'The password is not belong to the voter'
   seatx = r[0]['data']['json']['seat']
   if seat_num != seatx:
      return 'The seat is not belonged to the name.'

   ## update seat state
   r = api.publish('ticket', ['seat', seat_num], {'json': {'state': '22', 'name': name}})
   try:
      if r['error']:
         return 'Error updating seat: ' + str(r['error']['message'])
   except:
      pass

   return 'Success.'

##################################################################################

@app.route('/unbooks', methods=['POST'])
def unbooks():
   name = request.form['name']
   if not is_valid_name(name):
      return 'Invalid name'

   pwd = request.form['pwd']
   if not is_valid_pwd(pwd):
      return 'Invalid pwd'

   num_seat = int(get_num_seat())
   seat_num = request.form['seat_num']
   if not is_valid_seat(seat_num, num_seat):
      return 'Invalid seat number'

   state = get_seat_state(seat_num)
   if state == '00':
      return 'The seat is not booked.'
   if state == '22':
      return 'The seat is already seated.'

   r = api.liststreamkeyitems('ticket', name, False, 1)
   if len(r) == 0:
      return 'The name is not in the booked list'
   namex = decode(r[0]['data']['json']['ename'], pwd)
   if namex != name:
      return 'The password is not belong to the voter'
   seatx = r[0]['data']['json']['seat']
   if seat_num != seatx:
      return 'The seat is not belonged to the name.'

   ## reset the seat state
   r = api.publish('ticket', ['seat', seat_num], {'json': {'state': '00'}})
   try:
      if r['error']:
         return 'Error updating seat: ' + str(r['error']['message'])
   except:
      pass

   ## Nullify the name
   r = api.publish('ticket', ['name', name], {'json': {'ename': 'none', 'seat': 'none'}})
   try:
      if r['error']:
         return 'Error nullify name: ' + str(r['error']['message'])
   except:
      pass

   return 'Success: The seat has been reseted and the name is nullified.'


###############################################################

if __name__ == '__main__':
    app.run(port=8080, debug=True)


