#!/usr/bin/env python3

import pybgpstream
from collections import defaultdict
"""
CS 6250 BGP Measurements Project

Notes:
- Edit this file according to the project description and the docstrings provided for each function
- Do not change the existing function names or arguments
- You may add additional functions but they need to be contained entirely in this file
"""
# Task 1A: Unique Advertised Prefixes Over Time
def unique_prefixes_by_snapshot(cache_files):
    """
    Retrieve the number of unique IP prefixes from each of the input BGP data files.
    Args:
        cache_files: A chronologically sorted list of absolute (also called "fully qualified") path names
    Returns:
        A list containing the number of unique IP prefixes for each input file.
        For example: [2, 5]
    """
    results=[]
    for fpath in cache_files:
        stream=pybgpstream.BGPStream(data_interface='singlefile')
        stream.set_data_interface_option('singlefile','rib-file',fpath)
        stream.add_filter('ipversion','4')
        unique_prefixes=set()
        for elem in stream:
            unique_prefixes.add(elem.fields['prefix'])
        results.append(len(unique_prefixes))
    return results

# Task 1B: Unique Autonomous Systems Over Time
def unique_ases_by_snapshot(cache_files):
    """
    Retrieve the number of unique ASes from each of the input BGP data files.
    Args:
        cache_files: A chronologically sorted list of absolute (also called "fully qualified") path names
    Returns:
        A list containing the number of unique ASes for each input file.
        For example: [2, 5]
    """
    results=[]
    for fpath in cache_files:
        stream=pybgpstream.BGPStream(data_interface='singlefile')
        stream.set_data_interface_option('singlefile','rib-file',fpath)
        stream.add_filter('ipversion','4')
        unique_ases=set()
        for elem in stream:
            # corner case: no element in as-path: drop
            if elem.fields['as-path']!='':
                for aspath in elem.fields['as-path'].split(' '):
                    unique_ases.add(aspath)
        results.append(len(unique_ases))
    return results

# Task 1C: Top-10 Origin AS by Prefix Growth
def top_10_ases_by_prefix_growth(cache_files):
    """
    Compute the top 10 origin ASes ordered by percentage increase (smallest to largest) of advertised prefixes.
    Args:
        cache_files: A chronologically sorted list of absolute (also called "fully qualified") path names
    Returns:
        A list of the top 10 origin ASes ordered by percentage increase (smallest to largest) of advertised prefixes
        AS numbers are represented as strings.

        For example: ["777", "1", "6"]
          corresponds to AS "777" as having the smallest percentage increase (of the top ten) and AS "6" having the
          highest percentage increase (of the top ten).
      """
    results=[]
    data=defaultdict(list)
    for fpath in cache_files:
        stream=pybgpstream.BGPStream(data_interface='singlefile')
        stream.set_data_interface_option('singlefile','rib-file', fpath)
        stream.add_filter('ipversion','4')
        counts=defaultdict(set)
        for elem in stream:
            if elem.fields['as-path']!='':
                prefix,ases=elem.fields['prefix'],elem.fields['as-path'].split(' ')
                origin=ases[-1]
                counts[origin].add(prefix)
        for key in counts:
            data[key].append(len(counts[key]))
    for key in data:
        if len(data[key])>1:
            diff=(float(data[key][-1])/float(data[key][0]))
            results.append([key,diff])
    return [r[0] for r in sorted(results,key=lambda x:-x[1])[:10]]



# Task 2: Routing Table Growth: AS-Path Length Evolution Over Time
def shortest_path_by_origin_by_snapshot(cache_files):
    """
    Compute the shortest AS path length for every origin AS from input BGP data files.

    Retrieves the shortest AS path length for every origin AS for every input file.
    Your code should return a dictionary where every key is a string representing an AS name and every value is a list
    of the shortest path lengths for that AS.

    Note: If a given AS is not present in an input file, the corresponding entry for that AS and file should be zero (0)
    Every list value in the dictionary should have the same length.
    Args:
        cache_files: A chronologically sorted list of absolute (also called "fully qualified") path names
    Returns:
        A dictionary where every key is a string representing an AS name and every value is a list, containing one entry
        per file, of the shortest path lengths for that AS
        AS numbers are represented as strings.
        For example: {"455": [4, 2, 3], "533": [4, 1, 2]}
        corresponds to the AS "455" with the shortest path lengths 4, 2 and 3 and the AS "533" with the shortest path
        lengths 4, 1 and 2.
    """
    results=defaultdict(list)
    for idx,fpath in enumerate(cache_files):
        stream=pybgpstream.BGPStream(data_interface='singlefile')
        stream.set_data_interface_option('singlefile','rib-file',fpath)
        stream.add_filter('ipversion','4')
        data={}
        for el in stream:
            if el.fields['as-path']!='':
                prefix,ases=el.fields['prefix'],el.fields['as-path'].split(' ')
                origin=ases[-1]
                unique_ases=set(ases)
                if len(unique_ases)>1:
                    if origin not in data.keys():
                        data[origin]=len(unique_ases)
                    data[origin]=min(data[origin],len(unique_ases))
        for key in data:
            if key not in results:
                results[key]=[0]*len(cache_files)
            results[key][idx]=data[key]
    return results


# Task 3: Announcement-Withdrawal Event Durations
def aw_event_durations(cache_files):
    """
    Identify Announcement and Withdrawal events and compute the duration of all explicit AW events in the input BGP data
    Args:
        cache_files: A chronologically sorted list of absolute (also called "fully qualified") path names
    Returns:
        A dictionary where each key is a string representing the IPv4 address of a peer (peerIP) and each value is a
        dictionary with keys that are strings representing a prefix and values that are the list of explicit AW event
        durations (in seconds) for that peerIP and prefix pair.

        For example: {"127.0.0.1": {"12.13.14.0/24": [4.0, 1.0, 3.0]}}
        corresponds to the peerIP "127.0.0.1", the prefix "12.13.14.0/24" and event durations of 4.0, 1.0 and 3.0.
    """
    results={}
    data=defaultdict(dict)
    for fpath in cache_files:
        stream=pybgpstream.BGPStream(data_interface='singlefile')
        stream.set_data_interface_option('singlefile','upd-file',fpath)
        stream.add_filter('ipversion','4')
        for elem in stream:
            tp,tm,addr,prefix=elem.type,elem.time,elem.peer_address,elem.fields['prefix']
            if tp=='A':
                data[addr][prefix]=tm
            elif tp=='W' and prefix in data[addr]:
                if tm-data[addr][prefix]>0:
                    if addr not in results.keys():
                        results[addr]={}
                    if prefix not in results[addr].keys():
                        results[addr][prefix]=[]
                    results[addr][prefix].append(tm-data[addr][prefix])
                del data[addr][prefix]
    return results


# Task 4: RTBH Event Durations
def rtbh_event_durations(cache_files):
    """
    Identify blackholing events and compute the duration of all RTBH events from the input BGP data

    Identify events where the IPv4 prefixes are tagged with at least one Remote Triggered Blackholing (RTBH) community.
    Args:
        cache_files: A chronologically sorted list of absolute (also called "fully qualified") path names
    Returns:
        A dictionary where each key is a string representing the IPv4 address of a peer (peerIP) and each value is a
        dictionary with keys that are strings representing a prefix and values that are the list of explicit RTBH event
        durations (in seconds) for that peerIP and prefix pair.

        For example: {"127.0.0.1": {"12.13.14.0/24": [4.0, 1.0, 3.0]}}
        corresponds to the peerIP "127.0.0.1", the prefix "12.13.14.0/24" and event durations of 4.0, 1.0 and 3.0.
    """
    results={}
    data=defaultdict(dict)
    for fpath in cache_files:
        stream=pybgpstream.BGPStream(data_interface='singlefile')
        stream.set_data_interface_option('singlefile','upd-file',fpath)
        stream.add_filter('ipversion','4')
        for elem in stream:
            tp,tm,addr,prefix=elem.type,elem.time,elem.peer_address,elem.fields['prefix']
            if tp=='A':
                comms=elem.fields['communities']
                flag=False
                for set_ele in comms:
                    if set_ele.split(':')[-1]=='666':
                        flag=True
                if flag==True:
                    data[addr][prefix]=tm
                elif prefix in data[addr]:
                    del data[addr][prefix]
            if tp=='W' and prefix in data[addr]:
                if tm-data[addr][prefix]>0:
                    if addr not in results.keys():
                        results[addr]={}
                    if prefix not in results[addr].keys():
                        results[addr][prefix]=[]
                    results[addr][prefix].append(tm-data[addr][prefix])
                del data[addr][prefix]
    return results


# The main function will not be run during grading.
# You may use it however you like during testing.
#
# NB: make sure that check_solution.py runs your
#     solution without errors prior to submission
if __name__ == '__main__':
    pass


