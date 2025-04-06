## python -m pip install savoir

from Savoir import Savoir
import random

rpcuser = 'multichainrpc'
rpcpasswd = '52TH6uU5onYPrwGoZzMittjoEjg9iZS6rDi8i3aVQjNi'
rpchost = '127.0.0.1'
rpcport = '1234'
chainname = 'chain1'
api = Savoir(rpcuser, rpcpasswd, rpchost, rpcport, chainname)

SYM = ['2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b',
'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n',
'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def gen_pwd():
   p = ''
   for _ in range(random.randint(4, 6)):
      p += random.choice(SYM)
   return p

def is_valid_pwd(pwd):
   if pwd.__class__.__name__ == 'str':
      if 3 < len(pwd) < 7:
         for c in pwd:
            if c not in SYM:
               return False
         return True
   return False

def is_valid_seat(seat, max):
   try:
      s = int(seat)
      if 0 <= s < max:
         return True
   except:
      return False

def is_valid_name(name):
   return True

def get_admin_addr():
   return api.getaddresses()[0]

def get_num_seat():
   return hex_str(api.liststreamkeyitems('ticket', 'num_seat', False, 1)[0]['data'])
   
state_map = { '00': 'available', '11': 'booked', '22': 'seated' }

def get_seat_state(seat_num):
   return str(api.liststreamkeyitems('ticket', seat_num, False, 1)[0]['data']['json']['state'])








def str_hex(s):
   return s.encode().hex()

def hex_str(h):
   return bytes.fromhex(h).decode()

def encode(text, pwd):
   def encrypt(text, s): 
      result = "" 
      for i in range(len(text)): 
         char = text[i] 
         if (char.isdigit()):
            result += chr((ord(char) + s-48) % 10 + 48) 
         elif (char.isupper()): 
            result += chr((ord(char) + s-65) % 26 + 65) 
         else: 
            result += chr((ord(char) + s-97) % 26 + 97) 
      return result
   if not is_valid_pwd(pwd):
      return 'Invalid password'
   for c in pwd:
      text = encrypt(text, ord(c) - 48)
   return text

def decode(text, pwd):
   def decrypt(text, s): 
      result = "" 
      for i in range(len(text)): 
         char = text[i] 
         if (char.isdigit()):
            result += chr((ord(char) - s-48) % 10 + 48) 
         elif (char.isupper()): 
            result += chr((ord(char) - s-65) % 26 + 65) 
         else: 
            result += chr((ord(char) - s-97) % 26 + 97) 
      return result
   if not is_valid_pwd(pwd):
      return 'Invalid password'
   for c in reversed(pwd):
      text = decrypt(text, ord(c) - 48)
   return text 