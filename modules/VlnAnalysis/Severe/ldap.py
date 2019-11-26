#!/usr/bin/env python3
# coding: utf-8

#-:-:-:-:-:-:-:-:-:-:-:-:#
#    Vaile Framework     #
#-:-:-:-:-:-:-:-:-:-:-:-:#

#Author: @_tID
#This module requires Vaile Framework
#https://github.com/VainlyStrain/Vaile


import os
import sys
import time
import requests as wrn
sys.path.append('files/signaturedb/')
from core.methods.tor import session
from multiprocessing import Pool, TimeoutError
from core.methods.multiproc import listsplit
from core.variables import processes
from core.Core.colors import *
from files.signaturedb.ldaperror_signatures import ldap_errors
from requests.packages.urllib3.exceptions import InsecureRequestWarning

wrn.packages.urllib3.disable_warnings(InsecureRequestWarning)

info = "This module tests LDAP Injections using either the default payload database, or an user-provided dictionary."
searchinfo = "LDAP Injection Scan"
properties = {}

def getFile0x00(fi):

    global payloads
    payloads = []
    print(GR+' [*] Importing payloads...')
    time.sleep(0.7)
    with open(fi,'r') as payl:
        for pay in payl:
            c = pay.replace('\n','')
            payloads.append(c)
    print(G+' [+] Loaded '+O+str(len(payloads))+G+' payloads...')

def check0x00(web000, headers, pays):
    success = []
    requests = session()
    for payload in pays:
        gotcha = False
        print(B+'\n [+] Using Payload : '+C+payload)
        web0x00 = web000 + payload
        print(O+' [+] Url : '+C+web0x00)
        print(GR+' [*] Making the request...')
        try:
            req = requests.get(web0x00, headers=headers, allow_redirects=False, timeout=7, verify=False).text
            print(O+' [!] Searching through error database...')
            for err in ldap_errors:
                if err.lower() in req.lower():
                    print(G+' [+] Possible LDAP Injection Found : '+O+web0x00)
                    gotcha=True
                    print(O+' [+] Response : ')
                    print(P+req)
                    success.append(payload)
                else:
                    pass

            if gotcha == False:
                print(R+' [-] No error reflection found in response!')
                time.sleep(0.4)
                print(R+' [-] Payload '+O+payload+R+' not working!')
                pass

        except Exception as e:
            print(R+' [-] Query Exception : '+str(e))
    return success

def ldap(web):

    print(GR+' [*] Loading module...')
    time.sleep(0.5)
    #print(R+'\n     =============================')
    #print(R+'\n      L D A P   I N J E C T I O N')
    #print(R+'     ——·‹›·––·‹›·——·‹›·——·‹›·––·‹›\n')

    from core.methods.print import pvln
    pvln("ldap Injection") 
                  
    try:
        web0 = input(O+' [#] Parameter path to test (eg. /lmao.php?foo=bar) :> ')
        if "?" in web0 and '=' in web0:
            if web0.startswith('/'):
                m = input(GR+'\n [!] Your path starts with "/".\n [#] Do you mean root directory? (Y/n) :> ')
                if m.lower() == 'y':
                    web00 = web + web0
                elif m.lower() == 'n':
                    web00 = web + web0
                else:
                    print(R+' [-] U mad?')
            else:
                web00 = web + '/' + web0
        print(B+' [+] Parameterised Url : '+C+web00)

        pa = input(" [?] Parallel Attack? (enter if not) :> ")
        parallel = pa is not ""

        input_cookie = input("\n [*] Enter cookies if needed (Enter if none) :> ")
        print(GR+' [*] Setting headers...')
        time.sleep(0.6)
        gen_headers =    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
                          'Accept-Language':'en-US;',
                          'Accept-Encoding': 'gzip, deflate',
                          'Accept': 'text/html,application/xhtml+xml,application/xml;',
                          'Connection':'close'}

        if(len(input_cookie) > 0):
            gen_headers['Cookie'] = input_cookie
        print(O+' [#] Enter the payloads file '+R+'(Default: files/payload-db/ldap_payloads.lst)...')
        fi = input(O+' [#] Your input (Press Enter for default) :> ')
        if fi == '':
            fi = 'files/payload-db/ldap_payloads.lst'
            getFile0x00(fi)
        else:
            if os.path.exists(fi) == True:
                print(G+' [+] File under '+fi+' found!')
                getFile0x00(fi)
            else:
                print(R+' [-] Invalid input... Using default...')
                fi = 'files/payload-db/ldap_payloads.lst'
                getFile0x00(fi)
        print(O+' [!] Parsing url...')
        time.sleep(0.7)
        web000 = web00.split('=')[0] + '='
        print(GR+' [*] Starting enumeration...')
        time.sleep(0.7)
        success = []
        if not parallel:
            success += check0x00(web000, gen_headers, payloads)
        else:
            paylists = listsplit(payloads, round(len(payloads)/processes))
            with Pool(processes=processes) as pool:
                res = [pool.apply_async(check0x00, args=(web000,gen_headers,l,)) for l in paylists]
                for y in res:
                    i = y.get()
                    success += i
        if success:
            print(" [+] LDAPi Vulnerability found! Successful payloads:")
            for i in success:
                print(i)
        else:
            print(R + "\n [-] No payload succeeded."+C)

    except KeyboardInterrupt:
        print(R+' [-] Aborting module...')
        pass
    except Exception as e:
        print(R+' [-] Exception : '+str(e))
    print(G+'\n [+] LDAP Injection module completed!\n')

def attack(web):
    ldap(web)