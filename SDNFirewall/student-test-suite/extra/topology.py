#!/usr/bin/python
# CS 6250 Spring 2021 - SDN Firewall Project with POX
# build leucosia-v20

# This file defines the default topology used to grade your assignment.  You
# may create additional firewall topologies by using this file as a template.
# All commands in here are standard Mininet commands like you have used in the first
# project.  This file has been updated to Python 3.

from mininet.topo import Topo
from mininet.net  import Mininet
from mininet.node import CPULimitedHost, RemoteController
from mininet.util import custom
from mininet.link import TCLink
from mininet.cli  import CLI

class FirewallTopo(Topo):

    def __init__(self, cpu=.1, bw=10, delay=None, **params):
        super(FirewallTopo,self).__init__()
        
        # Host in link configuration
        hconfig = {'cpu': cpu}
        lconfig = {'bw': bw, 'delay': delay}
        
        # Create the firewall switch
        s1 = self.addSwitch('s1')

        # us network under 10.0.1.0/8
        # atlanta
        atl = self.addHost( 'atl', ip='10.0.1.1', mac='00:00:00:00:00:1e', **hconfig)
        # dallas
        dal = self.addHost( 'dal', ip='10.0.1.2', mac='00:00:00:00:01:1e', **hconfig)
        self.addLink(s1,atl)
        self.addLink(s1,dal)

        # uk network under 10.0.2.0/8
        # london
        ldn = self.addHost( 'ldn', ip='10.0.2.1', mac='00:00:00:01:00:1e', **hconfig)
        # manchester
        mrc = self.addHost( 'mcr', ip='10.0.2.2', mac='00:00:00:02:01:1e', **hconfig)
        self.addLink(s1,ldn)
        self.addLink(s1,mrc)
        

def main():
    print("Starting Mininet Topology...")
    print("If you see a Unable to Contact Remote Controller, you have an error in your code...")
    print("Remember that you always use the Server IP Address when calling test scripts...")
    topo = FirewallTopo()
    net = Mininet(topo=topo, link=TCLink, controller=RemoteController("SDNFirewall",port=6633))

    net.start()
    CLI(net)

if __name__ == '__main__':
    main()
