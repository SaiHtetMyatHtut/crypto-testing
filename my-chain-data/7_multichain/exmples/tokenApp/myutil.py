## python -m pip install savoir

from Savoir import Savoir
import random

rpcuser = 'multichainrpc'
rpcpasswd = '52TH6uU5onYPrwGoZzMittjoEjg9iZS6rDi8i3aVQjNi'
rpchost = '127.0.0.1'
rpcport = '1234'
chainname = 'chain1'
api = Savoir(rpcuser, rpcpasswd, rpchost, rpcport, chainname)

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
#---------------------------------------------------------

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

def admin_addr():
   return api.getaddresses()[0]

def is_valid_addr(addr):
   return api.validateaddress(addr)['isvalid']

def is_valid_addr_pwd(addr, pwd):
   if not is_valid_pwd(pwd):
      return False
   if not is_valid_addr(addr):
       return False
   r = api.liststreamkeyitems('encaddr', addr)
   if len(r) == 0:
      return False
   encaddr = hex_str(r[0]['data'])
   return decode(encaddr, pwd) == addr

# addr = '1HTTDLg8v8YyN9D4YCCHX3Qy3WNx4nVDK5Z58E'
# print(api.liststreamkeyitems('encaddr', addr))
# print(is_valid_addr_pwd('1HTTDLg8v8YyN9D4YCCHX3Qy3WNx4nVDK5Z58E', 'bwjd'))

def is_valid_asset(asset):
   try:
      return api.getassetinfo(asset, False)['name'] == asset
   except:
      return False

def is_valid_amount(amount):
   if (not amount.isdecimal()) or float(amount) <= 0:
      return False
   return True

