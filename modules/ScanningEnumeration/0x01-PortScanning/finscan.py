#!/usr/bin/env python3
# -*- coding : utf-8

#-:-:-:-:-:-:-:-:-:-:-:-:#
#    Vaile Framework     #
#-:-:-:-:-:-:-:-:-:-:-:-:#

#Author : @_tID
#This script is a part of Vaile Framework
#https://github.com/VainlyStrain/Vaile


from scapy.all import *
import sys
from datetime import datetime
import time
import socket
from core.Core.colors import *
from core.variables import processes
from core.methods.multiproc import listsplit
from multiprocessing import Pool, TimeoutError
from time import sleep
from time import strftime
from logging import getLogger, ERROR
getLogger("scapy.runtime").setLevel(ERROR)

info = "FIN Scanner."
searchinfo = "FIN Scanner"
properties = {"INIT":["Start of port range to scan.", " "], "FIN":["End of the port range to scan.", " "], "VERBOSE":["Verbose Output? [1/0]", " "]}


def checkhost(ip): # Function to check if target is up
    conf.verb = 0 # Hide output
    try:
        ping = sr1(IP(dst = ip)/ICMP()) # Ping the target
        print(G+"\n [+] Target server detected online...")
        time.sleep(0.6)
        print(GR+' [*] Beginning scan...')
    except Exception: # If ping fails
        print(R+"\n [-] Couldn't Resolve Target")
        print(R+" [-] Exiting...")
        quit()

def portloop(portlist, verbose, target):
    open = []
    closed = []
    filtered = []
    for port in portlist:
        result = scanport(port, verbose, target)
        open += result[0]
        closed += result[1]
        filtered += result[2]
    return (open, closed, filtered)


def scanport(port, verbose, ip_host): # Function to scan a given port
    open = []
    closed = []
    filtered = []
    SYNACK = 0x12 # Set flag values for later reference
    RSTACK = 0x14
    try:
        srcport = RandShort()
        conf.verb = 0
        if verbose:
            print(C+' [*] Sending FIN flagged packet to port : ' + str(port))
        fin_scan_resp = sr1(IP(dst=ip_host)/TCP(sport = srcport, dport=port,flags="F"),timeout=10)
        if verbose:
            print(C+' [*] Receiving incoming packet from port : ' + str(port))
            print(B+' [*] Extracting the received packet...')
        try:
            if (str(type(fin_scan_resp))=="<type 'NoneType'>"):
                print("\033[1;92m [!] Port \033[33m%s \033[1;92mdetected Open...\033[0m" % port)
                open.append(port)

            elif(fin_scan_resp.haslayer(TCP)):
                if(fin_scan_resp.getlayer(TCP).flags == RSTACK):
                    if verbose:
                        print(''+R+" [!] Port %s detected Closed..."+O+'' % port)
                    closed.append(port)
                    pass

            elif(fin_scan_resp.haslayer(ICMP)):
                if(int(fin_scan_resp.getlayer(ICMP).type)==3 and int(fin_scan_resp.getlayer(ICMP).code) in [1,2,3,9,10,13]):
                    if verbose:
                        print("\n\033[1;32m [!] Port \033[33m%s \033[1;92mdetected Filtered !\033[0m" % port)
                    filter.append(port)

        except:
            pass

    except KeyboardInterrupt: # In case the user needs to quit

        print('\033[91m [*] User requested shutdown...\033[0m')
        print(O+" [*] Exiting...")
        quit()

    return (open, closed, filtered)

def scan0x00(target):
    try:
        from core.methods.print import pscan
        pscan("fin scan")
        #print(''+R+'\n          =================')
        #print(''+R + '           F I N   S C A N ')
        #print(''+R + '          =================')
        print(''+R + '   [Reliable only in LA Networks]\n')

        if properties["INIT"][1] == " ":
            min_port = input(O+' [#] Enter initial port :> ')
        else:
            min_port = properties["INIT"][1]
        if properties["FIN"][1] == " ":
            max_port = input(O+' [#] Enter ending port :> ')
        else:
            max_port = properties["FIN"][1]
        openfil_ports = []
        filter_ports = []
        closed_ports = []
        ip_host = socket.gethostbyname(target)

        if properties["VERBOSE"][1] == " ":
            chk = input(C+' [#] Do you want a verbose output? (enter if not) :> ')
            verbose = chk is not ""
        else:
            verbose = properties["VERBOSE"][1] == "1"

        try:
            print(GR+' [*] Checking port range...')
            if int(min_port) >= 0 and int(max_port) >= 0 and int(max_port) >= int(min_port) and int(max_port) <= 65536:
                print('\033[1;32m [!] Port range detected valid...\033[0m')
                time.sleep(0.3)
                print(GR+' [*] Preparing for the the FIN Scan...')
                pass
            else: # If range didn't raise error, but didn't meet criteria
                print("\n\033[91m [!] Invalid Range of Ports\033[0m")
                print(O+" [!] Exiting...")
                quit()
        except Exception: # If input range raises an error
            print("\n\033[91m [!] Invalid Range of Ports\033[0m")
            print(O+" [!] Exiting...")
            quit()


        ports = range(int(min_port), int(max_port)+1) # Build range from given port numbers
        starting_time = time.time() # Start clock for scan time

        checkhost(ip_host) # Run checkhost() function from earlier
        print(O+" [*] Scanning initiated at " + strftime("%H:%M:%S") + "!\n") # Confirm scan start


        prtlst = listsplit(ports, round(len(ports)/processes))
        with Pool(processes=processes) as pool:
            res = [pool.apply_async(portloop, args=(l,verbose,ip_host,)) for l in prtlst]
            #res1 = pool.apply_async(portloop, )
            for i in res:
                j = i.get()
                openfil_ports += j[0]
                closed_ports += j[1]
                filter_ports += j[2]


        print("\n [!] Scanning completed at %s" %(time.strftime("%I:%M:%S %p")))
        ending_time = time.time()
        total_time = ending_time - starting_time
        print(GR+' [*] Preparing report...\n')
        time.sleep(1)
        print(O+' ——·+-------------+')
        print(O+'    [ SCAN REPORT ]    finscan')
        print(O+'    +-------------+   ----------')
        print(O+'             ')
        print(O+'    +--------+------------------+')
        print(O+'    |  '+GR+'PORT  '+O+'|       '+GR+'STATE      '+O+'|')
        print(O+'    +--------+------------------+')

        if openfil_ports:
            for i in sorted(openfil_ports):

                c = str(i)
                if len(c) == 1:
                    print(O+'    |   '+C+c+O+'    |       '+G+'OPEN       '+O+'|')
                    print(O+'    +--------+------------------+')
                    time.sleep(0.2)
                elif len(c) == 2:
                    print(O+'    |   '+C+c+'   '+O+'|       '+G+'OPEN       '+O+'|')
                    print(O+'    +--------+------------------+')
                    time.sleep(0.2)
                elif len(c) == 3:
                    print(O+'    |  '+C+c+'   '+O+'|       '+G+'OPEN       '+O+'|')
                    print(O+'    +--------+------------------+')
                    time.sleep(0.2)
                elif len(c) == 4:
                    print(O+'    |  '+C+c+'  '+O+'|       '+G+'OPEN       '+O+'|')
                    print(O+'    +--------+------------------+')
                    time.sleep(0.2)
                elif len(c) == 5:
                    print(O+'    | '+C+c+'  '+O+'|       '+G+'OPEN       '+O+'|')
                    print(O+'    +--------+------------------+')
                    time.sleep(0.2)

        if filter_ports:
            for i in sorted(filter_ports):
                c = str(i)
                if len(c) == 1:
                    print(O+'    |   '+C+c+O+'    |     '+GR+'FILTERED     '+O+'|')
                    print(O+'    +--------+------------------+')
                    time.sleep(0.2)
                elif len(c) == 2:
                    print(O+'    |   '+C+c+'   '+O+'|     '+GR+'FILTERED     '+O+'|')
                    print(O+'    +--------+------------------+')
                    time.sleep(0.2)
                elif len(c) == 3:
                    print(O+'    |  '+C+c+'   '+O+'|     '+GR+'FILTERED     '+O+'|')
                    print(O+'    +--------+------------------+')
                    time.sleep(0.2)
                elif len(c) == 4:
                    print(O+'    |  '+C+c+'  '+O+'|     '+GR+'FILTERED     '+O+'|')
                    print(O+'    +--------+------------------+')
                    time.sleep(0.2)
                elif len(c) == 5:
                    print(O+'    | '+C+c+'  '+O+'|     '+GR+'FILTERED     '+O+'|')
                    print(O+'    +--------+------------------+')
                    time.sleep(0.2)

        else:
            print(''+R+" [-] No filtered ports found.!!"+O+'')
        print(B+"\n [!] " + str(len(closed_ports)) + ' closed ports not shown')
        print(O+" [!] Host %s scanned in %s seconds\n" %(target, total_time))
    except KeyboardInterrupt:
        print(R+"\n [-] User Requested Shutdown...")
        print(" [*] Exiting...")
        quit()


def finscan(web):
    print(GR+' [*] Loading scanner...')
    time.sleep(0.5)
    if 'http://' in web:
        web = web.replace('http://','')
    elif 'https://' in web:
        web = web.replace('https://','')
    else:
        pass

    scan0x00(web)

def attack(web):
    finscan(web)