#! /usr/bin/env python2

# Copyright (c) 2011 ARM Limited
# All rights reserved
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Giacomo Gabrielli

# Pipeline activity viewer for the O3 CPU model.

import optparse
import os
import sys
import re
import profile
from time import time

from probe import *
# instProbe, pipeProbe, requestProbe, accessProbe

import trace as traceparser
from trace import seqinsts

import tree as treeparser
from tree import treeList

import memorytrace as memorytraceparser
from memorytrace import seqrequest

import pipeline as pipelineparser
from pipeline import pipestage

import outputcounter

def trace_tool(trace, treefile, cimtreefile, conf, outfile):

    print 'Parsing the output trace file of GEM5...\n'
    print 'Collecting instruction probe, pipeline probe, request probe, and memory access probe....\n'  
    process_probe(trace)

    print 'Parsing cache and request trace...\n '
    memorytraceparser.process_memory_access(requestProbe, accessProbe)
    
    print 'Processing o3 pipeline trace...\n'
    traceparser.process_trace(instProbe, True)

    print 'Simplifying instruction format...\n'
    treeparser.simply_insts(seqinsts, seqrequest)

    print 'Parsing instruction trace... building tree...\n'
    tree_out_en = True
    treeparser.gene_tree(tree_out_en, treefile)
    for i in range(len(treeList)):
        if treeList[i]['load']:
            if str(treeList[i]['seqnum']) in seqrequest.keys():
                treeList[i]['level'] = seqrequest[str(treeList[i]['seqnum'])]
            else:
                treeList[i]['level'] = 'dram'

    print 'Parsing pipeline trace...\n'
    pipelineparser.parse_pipeline(pipeProbe)

    print 'Outputing cache utilization factor...\n'
    outputcounter.parse_output(treeList, cimtreefile, pipestage, conf, outfile)




def validate_range(my_range):
    my_range = [int(i) for i in my_range.split(':')]
    if (len(my_range) != 2 or
        my_range[0] < 0 or
        my_range[1] > 0 and my_range[0] >= my_range[1]):
        return None
    return my_range


def main():
    # Parse options
    usage = ('%prog [OPTION]... TRACE_FILE')
    parser = optparse.OptionParser(usage=usage)

    # cim tree options
    parser.add_option(
        '--tree', 
        dest='treefile',
        default=os.path.join(os.getcwd(), 'tree.out'),
        help="output basic tree file (default: '%default')")

    parser.add_option(
        '--cimtree', 
        dest='cimtreefile',
        default=os.path.join(os.getcwd(), 'cim-tree.out'),
        help="output basic tree file (default: '%default')")

    parser.add_option(
        '--conf',
        dest='cacheconf',
        default=0
        )

    '''parser.add_option(
        '--request',
        dest='requestfile',
        default=os.path.join(os.getcwd(), 'request.trace'),
        help="input request file (default: '%default')")

    parser.add_option(
        '--pipeline',
        dest='pipelinefile',
        default=os.path.join(os.getcwd(), 'pipeline.trace'),
        help="input request file (default: '%default')")'''

    # replacement
    '''parser.add_option(
        '--only_change_cache',
        dest='managecache',
        action='store_false',
        help="only change cache policy without building tree again")'''

    parser.add_option(
        '-o',
        dest='outfile',
        default=os.path.join(os.getcwd(), 'counter.out'),
        help="input request file (default: '%ddefault')")


    (options, args) = parser.parse_args()
    
    # Process trace
    with open(args[0], 'r') as trace:
        with open(options.outfile, 'w') as outfile:
            trace_tool(trace, options.treefile, options.cimtreefile, options.cacheconf, outfile)


if __name__ == '__main__':
    sys.path.append(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'src', 'python'))
    main()
