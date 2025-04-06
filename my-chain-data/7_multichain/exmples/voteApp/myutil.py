from Savoir import Savoir
import random

rpcuser = 'multichainrpc'
rpcpasswd = '52TH6uU5onYPrwGoZzMittjoEjg9iZS6rDi8i3aVQjNi'
rpchost = '127.0.0.1'
rpcport = '1234'
chainname = 'chain1'
api = Savoir(rpcuser, rpcpasswd, rpchost, rpcport, chainname)

import string
sym = [ x for x in (string.digits + string.ascii_letters)]
# print(sym)

## Exclude 0, 1, i, l, o, I and O.
sym.remove('0'); sym.remove('1')
sym.remove('i'); sym.remove('l'); sym.remove('o')
sym.remove('I'); sym.remove('O')
SYM = ''.join(sym)
# print(SYM)

## A password must be 4 to 6 characters long.
def gen_pwd():
   pwd = ''
   for _ in range(random.randint(4, 6)):
      pwd += random.choice(SYM)
   return pwd
# [print(gen_pwd()) for _ in range(10)]

def is_valid_pwd(pwd):
   if pwd.__class__.__name__ == 'str':
      if 3 < len(pwd) < 7:
         for c in pwd:
            if c not in SYM:
               return False
         return True
   return False
# print(is_valid_pwd('jack55'))

def is_valid(kind, name):
   for j in api.liststreamkeyitems('names', kind):
      if name == hex_str(j['data']):
         return True
   return False

def get_list(kind):
   r = api.liststreamkeyitems('names', kind)
   if len(r) == 0:
      return 'None'
   s = []
   for j in r:
      s.append(hex_str(j['data']))
   return s

def count(kind):
   return len(api.liststreamkeyitems('names', kind))

def get_root_addr():
   return api.getaddresses()[0]

def get_can_addr(name):
   r = api.liststreamkeyitems('nameaddr', name)
   if len(r) <= 0:
      return False
   return hex_str(r[0]['data'])

def getKey(item):
   return item[1]

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

#--------------------------------------------------------

def xor_encode(text, pwd):
   if not is_valid_pwd(pwd):
      return 'Invalid password'
   key = int.from_bytes(pwd.encode(), 'big')
   text_bytes = int.from_bytes(text.encode(), 'big')
   return key ^ text_bytes

def xor_decode(entext_bytes, pwd):
   if not is_valid_pwd(pwd):
      return 'Invalid password'
   key = int.from_bytes(pwd.encode(), 'big')
   text_bytes = key ^ entext_bytes
   length = text_bytes.bit_length()
   text = text_bytes.to_bytes((length+ 7) // 8, 'big')
   return text.decode()

def enc_test():
    for _ in range(10):
       pwd = gen_pwd(); print(pwd)
       txt = api.getnewaddress()
       ##txt = api.createkeypairs()[0]['privkey']
       print(txt)
       # en = encode(txt, pwd); print(en)
       en = xor_encode(txt, pwd); print(en)
       # de = decode(en, pwd); print(de)
       de = xor_decode(en, pwd); print(de)
       if txt != de:
          print('Falis')
          break
       print()
# enc_test()
