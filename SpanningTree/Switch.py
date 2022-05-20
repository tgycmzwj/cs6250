# Spanning Tree project for GA Tech OMS-CS CS 6250 Computer Networks
#
# This defines a Switch that can can send and receive spanning tree 
# messages to converge on a final loop free forwarding topology.  This
# class is a child class (specialization) of the StpSwitch class.  To 
# remain within the spirit of the project, the only inherited members
# functions the student is permitted to use are:
#
# self.switchID                   (the ID number of this switch object)
# self.links                      (the list of swtich IDs connected to this switch object)
# self.send_message(Message msg)  (Sends a Message object to another switch)
#
# Student code MUST use the send_message function to implement the algorithm - 
# a non-distributed algorithm will not receive credit.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2016 Michael Brown, updated by Kelly Parks
#           Based on prior work by Sean Donovan, 2015, updated for new VM by Jared Scott and James Lohse

from Message import *
from StpSwitch import *


class Switch(StpSwitch):

    def __init__(self, idNum, topolink, neighbors):
        # Invoke the super class constructor, which makes available to this object the following members:
        # -self.switchID                   (the ID number of this switch object)
        # -self.links                      (the list of swtich IDs connected to this switch object)
        super(Switch, self).__init__(idNum, topolink, neighbors)
        # TODO: Define a data structure to keep track of which links are part of / not part of the spanning tree.
        self.root = self.switchID
        self.distance = 0
        self.activeLinks = []
        self.switchThrough = self.switchID

    def send_initial_messages(self):
        # TODO: This function needs to create and send the initial messages from this switch.
        #      Messages are sent via the superclass method send_message(Message msg) - see Message.py.
        #      Use self.send_message(msg) to send this.  DO NOT use self.topology.send_message(msg)
        # need to send a message for each of the connected switches at initialization
        for link in self.links:
            #create the message object: claimedRoot, distanceToRoot, originID, destinationID, pathThrough
            msg = Message(self.switchID, 0, self.switchID, link, False)
            self.send_message(msg)
        return

    def process_message(self, message):
        # TODO: This function needs to accept an incoming message and process it accordingly.
        #      This function is called every time the switch receives a new message.
        # add to active link
        if message.pathThrough and message.origin not in self.activeLinks:
            self.activeLinks.append(message.origin)
        # remove from active link
        if message.pathThrough==False and message.origin!=self.switchThrough and message.origin in self.activeLinks:
            self.activeLinks.remove(message.origin)

        # find a smaller root
        if message.root<self.root:
            # update root
            self.root=message.root
            # update distance
            self.distance=message.distance+1
            # update the switchThrough
            self.switchThrough=message.origin
            # update the activeLinks
            if message.origin not in self.activeLinks:
                self.activeLinks.append(message.origin)
            # update neighbors with new message
            for link in self.links:
                msg=Message(self.root,self.distance,self.switchID,link,self.switchThrough==link)
                self.send_message(msg)
        #same root but shorter distance
        if (message.root==self.root) and (message.distance+1<self.distance):
            # remove old link from active links
            self.activeLinks.remove(self.switchThrough)
            # update distance
            self.distance=message.distance+1
            # update the switchThrough
            self.switchThrough=message.origin
            # update the activeLinks
            if message.origin not in self.activeLinks:
                self.activeLinks.append(message.origin)
            # update neighbors with new message
            for link in self.links:
                msg=Message(self.root,self.distance,self.switchID,link,self.switchThrough==link)
                self.send_message(msg)
        #same root, same distance, but a smaller origin
        if (message.root==self.root) and (message.distance+1==self.distance) and (message.origin<self.switchThrough):
            # remove old link from active links
            self.activeLinks.remove(self.switchThrough)
            # update the switchThrough
            self.switchThrough=message.origin
            # update the activeLinks
            if message.origin not in self.activeLinks:
                self.activeLinks.append(message.origin)
            # update neighbors with new message
            for link in self.links:
                msg=Message(self.root,self.distance,self.switchID,link,self.switchThrough==link)
                self.send_message(msg)
        return

    def generate_logstring(self):
        # TODO: This function needs to return a logstring for this particular switch.  The
        #      string represents the active forwarding links for this switch and is invoked 
        #      only after the simulaton is complete.  Output the links included in the 
        #      spanning tree by increasing destination switch ID on a single line. 
        #      Print links as '(source switch id) - (destination switch id)', separating links 
        #      with a comma - ','.  
        #
        #      For example, given a spanning tree (1 ----- 2 ----- 3), a correct output string 
        #      for switch 2 would have the following text:
        #      2 - 1, 2 - 3
        #      A full example of a valid output file is included (sample_output.txt) with the project skeleton.
        all_active_links = sorted(self.activeLinks)
        output_results=[]
        for link in all_active_links:
            output_results.append(str(self.switchID)+' - '+str(link))
        return ', '.join(output_results)

