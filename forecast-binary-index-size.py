#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import math
import locale
import os

locale.setlocale(locale.LC_ALL, 'en_US')

pointer_size = 4

def number_of_bits(n):
    return int(math.log(n, 2)) + 1

def utf8len(s):
    return len(s.encode('utf-8'))

# This doesn't actually produce a binary-encoded version of the JSON index
# Instead, it just estimates how big it will be.
# Nothing fancy, no BWT, deflate or other compression employed, yet.
# The number produced here should get smaller once node and list compression is applied.
def walk_tree(root,print_it=True):
    # sum of this level's parts and pieces
    sum = 0
    # how many characters in this node
    chars_len = len("".join(root.keys()).encode('utf-8'))

    # iterate the characters
    for char in root:
        # skip the _id_ array
        if char!='_id_':
            # collect the sums from the subtree nodes beneath this char
            sum += walk_tree( root[char], False )
        else:
            # subtract 1 from this node's length if _id_
            chars_len-=1

    # each char in the node will point to another node, 
    # so the cost of that pointer table is chars x pointer_size
    pointers_len = chars_len * pointer_size

    # cost of the _id_ array
    max_bits = 0 # max bits used by the max id in this node's _id_ array
    id_count = 0 # number of ids in _id_ array
    
    # not all nodes get an _id_ array, potentially, due to -s option threshold
    if '_id_' in root:
        # number of bits used by the maximum value in the current node's _id_ array
        max_bits = number_of_bits(max(root['_id_']))
        # number of ids pointed to by the _id_ array
        id_count = len(root['_id_'])

    # sum (subtree cost) + chars
    return sum + chars_len + chars_len * pointer_size + (math.ceil((0.0+max_bits)/8.0) * id_count)

def forecast_binary_index_size(filename):
    fileinfo = os.stat(filename)
    gzfileinfo = os.stat(filename+'.gz')
    fh = open(filename,'r')
    jstr = fh.read()
    fh.close()

    d = json.loads(jstr[14:-2])  # trim off the non-JSON var declaration added for benefit of JS ingestion

    bin_filesize = int(walk_tree( d ))
    print "Bytes for binary index: %s" % locale.format("%d", bin_filesize, grouping=True)
    print "Bytes for original JSON: %s" % locale.format("%d", fileinfo.st_size, grouping=True)
    print "Bytes for gzipped JSON: %s" % locale.format("%d", gzfileinfo.st_size, grouping=True)
    

forecast_binary_index_size('test_index2.js')
