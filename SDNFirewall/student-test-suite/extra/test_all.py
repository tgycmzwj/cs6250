#!/usr/bin/python
# test script for CS 6250 Spring 2021 - SDN Firewall Project with POX
# Author: Hao Tian

from mininet.net  import Mininet
from mininet.node import CPULimitedHost, RemoteController
from mininet.link import TCLink
# cannot import py file which name has '-'
# need to rename sdn-topology.py file
import os
os.system("cp sdn-topology.py topology.py")
from topology import FirewallTopo
import time
import sys

topo = FirewallTopo()
net = Mininet(topo=topo, link=TCLink, controller=RemoteController("SDNFirewall",port=6633))
net.start()

hosts = {host.name: host for host in net.hosts}

# spare some time for host to run
sleep_time = 0.3

testcases = []

for line in open("./testcases.txt", "r").readlines():
    if line[0] != "#" and len(line) > 1:
        testcases.append(line.split())

score = 0
wrong_ans = []

for i in range(len(testcases)):
    # progress bar
    sys.stdout.write("\r")
    sys.stdout.write("%d%%" %(100 / len(testcases) * (i+1)))
    sys.stdout.flush()

    case = testcases[i]
    client_name, host_name, protocol, port, src_port, ans = case
    host = hosts[host_name]
    client = hosts[client_name]
    host_ip = host.IP()

    if protocol == "P":
        # ping 
        client_ping = client.cmdPrint("timeout 0.1 ping -c 1 %s" %host.IP())
        connected = "True" if "icmp_seq" in client_ping else "False"
        score += connected == ans

    else:
        # TCP, UDP
        if src_port == "-":
            host_message = host.cmdPrint("python test-server.py %s %s %s &" %(protocol, host_ip, port))
            time.sleep(sleep_time)
            client_message = client.cmdPrint("python test-client.py %s %s %s &" %(protocol, host_ip, port))
            time.sleep(sleep_time)
            # I don't know why, but just repeat client two times, then you can see the message
            client_message = client.cmdPrint("python test-client.py %s %s %s &" %(protocol, host_ip, port))
        else:
            host_message = host.cmdPrint("python test-server.py %s %s %s &" %(protocol, host_ip, port))
            time.sleep(sleep_time)
            client_message = client.cmdPrint("python test-client.py %s %s %s %s &" %(protocol, host_ip, port, src_port))
            time.sleep(sleep_time)
            # I don't know why, but just repeat client two times, then you can see the message
            client_message = client.cmdPrint("python test-client.py %s %s %s %s &" %(protocol, host_ip, port, src_port))

        connected = "True" if "Received" in client_message else "False"
        score += connected == ans

    if connected != ans:
        wrong_ans.append("%d: %s -> %s with %s at %s, should be %s, current %s" %(i, client_name, host_name, protocol, port, ans, connected))


print()
print("Passed %d / %d" %(score, len(testcases)))

if len(wrong_ans) > 0:
    print("failed testcases:")
    for line in wrong_ans:
        print(line)

