'''
Ethernet learning switch in Python.

Note that this file currently has the code to implement a "hub"
in it, not a learning switch.  (I.e., it's currently a switch
that doesn't learn.)

Name: Jesse Williams
SN: 300390324

For this project I used LFU to determine whether an entry should be removed
if the interface too mac dictionary is full.
'''
from switchyard.lib.userlib import *

MAX_ENTRIES = 2    # the max number of host entries
intf_2mac = dict() # interface -> mac address

def main(net):
    global MAX_ENTRIES
    global intf_2mac

    my_interfaces = net.interfaces()
    mymacs = [intf.ethaddr for intf in my_interfaces]

    while True:
        try:
            timestamp,input_port,packet = net.recv_packet()
        except NoPackets:
            continue
        except Shutdown:
            return

        # Store packet header data
        srchwaddr = packet[0].src
        dsthwaddr = packet[0].dst
        print ('Src: {} | Dst: {}'.format(srchwaddr, dsthwaddr))

        ''' If the src port is in table, continue
            otherwise, save it in table. '''
        if input_port not in intf_2mac.keys():
            check_size()
            intf_2mac[input_port] = [srchwaddr, 0] # 0 = usage frequency

        log_debug ("In {} received packet {} on {}".format(net.name, packet, input_port))
        if packet[0].dst in mymacs:
            log_debug ("Packet intended for me")
        else:
            ''' If the dst address is known then find the output port
                and send. '''
            if get_intf(dsthwaddr) == True:
                for key, val in intf_2mac.items():
                    if val[0] == dsthwaddr:
                        b_freq = val[1]
                        val[1] = val[1] + 1 # increment frequency
                        #print ('Before: {} | After: {}'.format(b_freq, val[1])) # debug LFU
                        net.send_packet(key, packet)
            else:
                for intf in my_interfaces:
                    if input_port != intf.name:
                        log_debug ("Flooding packet {} to {}".format(packet, intf.name))
                        print ("Flooding packet")
                        net.send_packet(intf.name, packet)

    net.shutdown()

''' Check that there is space in the dict to add a new entry. '''
def check_size():
    min_freq = 200
    intf = None

    if len(intf_2mac) == MAX_ENTRIES:
        # find the LFU entry
        for key, val in intf_2mac.items():
            if val[1] < min_freq:
                min_freq = val[1]
                intf = key

        # remove the LFU entry
        if intf != None:
            print ("Deleting: {}".format(intf))
            del intf_2mac[intf]

''' Check if there is an entry with the matching hw address '''
def get_intf(dsthwaddr):
    global intf_2mac
    for key, val in intf_2mac.items():
        if val[0] == dsthwaddr:
            return True
    return False
