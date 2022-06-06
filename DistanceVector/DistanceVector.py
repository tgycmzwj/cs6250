# Distance Vector project for CS 6250: Computer Networks
#
# This defines a DistanceVector (specialization of the Node class)
# that can run the Bellman-Ford algorithm. The TODOs are all related 
# to implementing BF. Students should modify this file as necessary,
# guided by the TODO comments and the assignment instructions. This 
# is the only file that needs to be modified to complete the project.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2017 Michael D. Brown
# Based on prior work by Dave Lillethun, Sean Donovan, Jeffrey Randow, new VM fixes by Jared Scott and James Lohse.

from Node import *
from helpers import *


class DistanceVector(Node):
    
    def __init__(self, name, topolink, outgoing_links, incoming_links):
        """ Constructor. This is run once when the DistanceVector object is
        created at the beginning of the simulation. Initializing data structure(s)
        specific to a DV node is done here."""

        super(DistanceVector, self).__init__(name, topolink, outgoing_links, incoming_links)
        
        # TODO: Create any necessary data structure(s) to contain the Node's internal state / distance vector data
        self.dv={name:0}

    def send_initial_messages(self):
        """ This is run once at the beginning of the simulation, after all
        DistanceVector objects are created and their links to each other are
        established, but before any of the rest of the simulation begins. You
        can have nodes send out their initial DV advertisements here. 

        Remember that links points to a list of Neighbor data structure.  Access
        the elements with .name or .weight """

        # TODO - Each node needs to build a message and send it to each of its neighbors
        # HINT: Take a look at the skeleton methods provided for you in Node.py
        # msg[0]---origin
        # msg[1]---dictionary of all topolinks (node, weight)
        for last_neighbor in self.incoming_links:
            self.send_msg([self.name,self.dv.copy()],last_neighbor.name)

    def process_BF(self):
        """ This is run continuously (repeatedly) during the simulation. DV
        messages from other nodes are received here, processed, and any new DV
        messages that need to be sent to other nodes as a result are sent. """

        # Implement the Bellman-Ford algorithm here.  It must accomplish two tasks below:
        dv_before_update=self.dv.copy()
        # TODO 1. Process queued messages
        for msg in self.messages:
            next_neighbor=msg[0]
            for next_next_neighbor in msg[1].keys():
                # discard the route to oneself
                if next_next_neighbor==self.name:
                    continue
                # if the next_next_neighbor not yet discovered
                elif next_next_neighbor not in self.dv.keys():
                    if next_next_neighbor in [x.name for x in self.outgoing_links]:
                        distance=int(self.get_outgoing_neighbor_weight(next_next_neighbor))
                    else:
                        distance=int(msg[1][next_next_neighbor])+int(self.get_outgoing_neighbor_weight(msg[0]))
                    self.dv[next_next_neighbor]=distance
                # if the next_next_neighbor already discovered
                else:
                    distance=int(msg[1][next_next_neighbor])+int(self.get_outgoing_neighbor_weight(msg[0]))
                    # set to be -99 as long as one of the element is -99 (avoid situation -99+120=21 but -99 is actually -infinity)
                    if int(msg[1][next_next_neighbor])<=-99 or int(self.get_outgoing_neighbor_weight(msg[0]))<=-99:
                        self.dv[next_next_neighbor]=-99
                    else:
                        self.dv[next_next_neighbor]=max(min(self.dv[next_next_neighbor],distance),-99)
        
        # Empty queue
        self.messages = []

        # TODO 2. Send neighbors updated distances
        # check whether is any update
        update_flag=False
        if len(dv_before_update)!=len(self.dv):
            update_flag=True
        else:
            for key in self.dv.keys():
                if self.dv[key]!=dv_before_update[key]:
                    update_flag=True
        if update_flag==True:
            for last_neighbor in self.incoming_links:
                self.send_msg([self.name,self.dv.copy()],last_neighbor.name)

    def log_distances(self):
        """ This function is called immedately after process_BF each round.  It 
        prints distances to the console and the log file in the following format (no whitespace either end):
        
        A:A0,B1,C2
        
        Where:
        A is the node currently doing the logging (self),
        B and C are neighbors, with vector weights 1 and 2 respectively
        NOTE: A0 shows that the distance to self is 0 """
        
        # TODO: Use the provided helper function add_entry() to accomplish this task (see helpers.py).
        # An example call that which prints the format example text above (hardcoded) is provided.        
        # add_entry("A", "A0,B1,C2")
        results=[str(key)+str(val) for (key,val) in self.dv.items()]
        add_entry(self.name,','.join(results))
