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

# find load-load-op-store pattern for the whole trace

import optparse
import os
import sys
import copy
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt

all_cache_trace = []
all_request_trace = []
all_stage = []


def gene_stage_access(o3Trace, cacheTrace, requestTrace, maxInst, outfile):

    line = None
    fields = None

    # read all cache access trace, detect key information only for read memory request:
    # (#tick, #hierarchy, #packet, #hit/miss flag)


    while True:
        cache_trace = {
            'tick': 0,
            'level': None,
            'pkt': None,
            'flag': None,
        }
        line = cacheTrace.readline()
        if not line: break
        fields = line.split()

        if len(fields) == 3:
            cache_trace['tick'] = long(fields[0].rstrip(':'))
            cache_trace['level'] = (fields[1].split('.')[-1]).rstrip(':')
            cache_trace['pkt'] = fields[-1]
            cache_trace['flag'] = 'update'
            all_cache_trace.append(cache_trace)
            continue

        request_type = fields[2]
        if request_type == 'WriteReq': continue
        cache_trace['tick'] = long(fields[0].rstrip(':'))
        cache_trace['level'] = (fields[1].split('.')[-1]).rstrip(':')
        cache_trace['pkt'] = fields[3]
        if (' '.join(fields[4::])).find('miss') == -1:
            cache_trace['flag'] = 'hit'
        else:
            cache_trace['flag'] = 'miss'

        all_cache_trace.append(cache_trace)


    last_tick_seq = 0

    outfile.write('%s %s %s %s\n' % (
        "dcache".ljust(15),
        "l2".ljust(15),
        "dram".ljust(10),
        "total".rjust(10)
    ))
    outfile.write('\n')


    while True:
        request_trace = {
            'tick': 0,
            'pkt': None,
            'sn': 0,
            'level': None  # L1, L2, L3, DRAM
        }

        line = requestTrace.readline()
        if not line: break

        fields = line.split()

        request_trace['tick'] = long(fields[0].rstrip(':'))
        request_trace['pkt'] = fields[3]
        request_trace['sn'] = long((fields[-1].split(':'))[-1].rstrip(']'))

        # find hit/miss information of the current packet
        ini_tick = request_trace['tick']
        i = last_tick_seq - 1
        # record the search sequence numeber
        while i < len(all_cache_trace):
            i = i + 1
            if all_cache_trace[i]['tick'] < ini_tick: continue
            last_tick_seq = i
            #print(last_tick_seq)

            start_ref_address = long(request_trace['pkt'].split(':')[0].strip('['), 16)
            end_ref_address = long(request_trace['pkt'].split(':')[1].strip(']'), 16)
            # address align processing
            if start_ref_address & (~0x3f) != end_ref_address & (~0x3f):
                # data access is divided into two parts
                end_ref_address = (end_ref_address & (~0x3f)) - 1
            # detect the pkt from this tick
            while True:
                if all_cache_trace[i]['flag'] == 'update':
                    blk_addr = long(all_cache_trace[i]['pkt'], 16)
                    if blk_addr == start_ref_address & (~0x3f):
                        request_trace['level'] = all_cache_trace[i]['level']
                        break
                    else:
                        i = i + 1
                        continue
                else:
                    start_address = long(all_cache_trace[i]['pkt'].split(':')[0].strip('['), 16)
                    end_address = long(all_cache_trace[i]['pkt'].split(':')[1].strip(']'), 16)
                    if (start_address <= start_ref_address) and (end_address >= end_ref_address):
                        if all_cache_trace[i]['flag'] == 'hit':
                            request_trace['level'] = all_cache_trace[i]['level']
                            break
                        elif all_cache_trace[i]['level'] == 'l2':
                            request_trace['level'] = 'dram'
                            break
                        else:
                            i = i + 1
                    else:
                        i = i + 1
                        continue

            break

        '''outfile.write('%s %s %s %s\n' % (
            str(request_trace['tick']).ljust(15),
            (request_trace['pkt'].ljust(15)),
            (request_trace['level']).ljust(10),
            str((request_trace['sn'])).rjust(10)
        ))'''

        all_request_trace.append(request_trace)

    print('\n')

    stage_memory_trace = {
            'dcache_access': 0,
            'l2_access': 0,
            'dram_access': 0,
            'overall_access': 0 
    }
    num = 0
    lines = 0
    length = len(all_request_trace)
    memoryTraceData = np.empty(shape=[0,3])

    while True:

        line = o3Trace.readline()
        if not line: break
        fields = line.split()
        if fields[0] == 'disasm': continue

        if num == 0: 
            stage_memory_trace = {
                'dcache_access': 0,
                'l2_access': 0,
                'dram_access': 0,
                'overall_access': 0 
            }
            start_seq = int(fields[-1])
            print(start_seq)
            num += 1
            continue
        if num < maxInst: 
            num += 1
            continue
        else:
            end_seq = int(fields[-1])
            print(end_seq)
            num = 0
            
            for i in range(len(all_request_trace)):
                if int(all_request_trace[i]['sn']) < start_seq: continue
                if int(all_request_trace[i]['sn']) > end_seq: 
                    stage_memory_trace['overall_access'] = stage_memory_trace['dcache_access'] + stage_memory_trace['l2_access'] + stage_memory_trace['dram_access']
                    break
                if all_request_trace[i]['level'] == 'dcache':
                    stage_memory_trace['dcache_access'] += 1
                elif all_request_trace[i]['level'] == 'l2':
                    stage_memory_trace['l2_access'] += 1
                elif all_request_trace[i]['level'] == 'dram':
                    stage_memory_trace['dram_access'] += 1

            outfile.write('%s %s %s %s\n' % (
                str(stage_memory_trace['dcache_access']),
                str(stage_memory_trace['l2_access']),
                str(stage_memory_trace['dram_access']),
                str(stage_memory_trace['overall_access'])
            ))

            #new_line = np.array([stage_memory_trace['dcache_access'],stage_memory_trace['l2_access'],stage_memory_trace['dram_access']])   
            #memoryTraceData = np.r_[memoryTraceData, new_line]
            memoryTraceData = np.insert(memoryTraceData, lines, [stage_memory_trace['dcache_access'],stage_memory_trace['l2_access'],stage_memory_trace['dram_access']], axis=0)
            lines += 1

    print memoryTraceData

    plt.hist(memoryTraceData[:,0], 100)
    plt.xlabel('dcache_access')
    plt.ylabel('numbers (10000 instructions per block)')
    plt.show()

    plt.hist(memoryTraceData[:,1], 50)
    plt.xlabel('l2_access')
    plt.ylabel('numbers (10000 instructions per block)')
    plt.show()

    plt.hist(memoryTraceData[:,2], 50)
    plt.xlabel('l2_access')
    plt.ylabel('numbers (10000 instructions per block)')
    plt.show()       






def main():
    # Parse options
    usage = ('%prog [OPTION]... O3PIPEVIEW_TRACE')
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-o',
        dest='outfile',
        default=os.path.join(os.getcwd(), 'stage_memory_trace.out'),
        help="output file (default: '%default')")
    parser.add_option(
        '--cache',
        dest='cachefile',
        default=os.path.join(os.getcwd(), 'cache.trace'),
        help="cache trace file (default: '%default')")
    parser.add_option(
        '--request',
        dest='requestfile',
        default=os.path.join(os.getcwd(), 'request.trace'),
        help="cache trace file (default: '%default')")
    parser.add_option(
        '--maxinsts',
        dest='maxInst',
        type='int', default=10000,
        help="instruction width (default: '%default')")
    (options, args) = parser.parse_args()

    # recognize the pattern
    print 'parse request packet and hit/miss states... ...',
    with open(args[0], 'r') as o3Trace:
        with open(options.cachefile, 'r') as cacheTrace:
            with open(options.requestfile, 'r') as requestTrace:
                with open(options.outfile, 'w') as out:
                    gene_stage_access(o3Trace, cacheTrace, requestTrace,
                                          options.maxInst, out)

    print 'done!'


if __name__ == '__main__':
    sys.path.append(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'src', 'python'))
    main()
